# -*- coding: utf-8 -*-
import os
import sys
import traceback
import re
import time
from xml.sax import saxutils
import sqlite3
import setproctitle
import click
import configparser
import hashlib
import unicodedata
import itertools
import urllib3
import shutil
from multiprocessing import Lock
from time import strftime, localtime
from urllib.error import URLError

from prompt_toolkit.history import FileHistory
from prompt_toolkit.shortcuts import PromptSession
from prompt_toolkit.formatted_text import HTML

from .cmdexecute import CmdExecute
from .cmdmapping import CmdMapping
from .hdfswrapper import HDFSWrapper
from .testcliexception import TestCliException
from .testclijobmanager import TestCliMeta
from .testclijobmanager import JOBManager
from .datawrapper import DataWrapper
from .testoption import TestOptions
from .__init__ import __version__
from .sqlparse import SQLAnalyze
from .apiparse import APIAnalyze

OFLAG_LOGFILE = 1
OFLAG_LOGGER = 2
OFLAG_CONSOLE = 4
OFLAG_SPOOL = 8
OFLAG_ECHO = 16


class TestCli(object):
    # 从配置文件中加载的连接配置信息
    db_connectionConf = None

    # SQLCli的初始化参数
    logon = None
    logfilename = None
    commandMap = None
    nologo = None

    # 屏幕输出
    Console = None  # 程序的控制台显示
    logfile = None  # 程序输出日志文件
    HeadlessMode = False  # 没有显示输出，即不需要回显，用于子进程的显示
    logger = None  # 程序的输出日志

    exitValue = 0  # 程序退出状态位

    def __init__(
            self,
            logon=None,                             # 默认登录信息，None表示不需要
            logfilename=None,                       # 程序输出文件名，None表示不需要
            script=None,                            # 脚本文件名，None表示命令行模式
            commandMap=None,                        # SQL映射文件名，None表示不存在
            nologo=False,                           # 是否不打印登陆时的Logo信息，True的时候不打印
            breakWithError=False,                   # 遇到命令行错误，是否中断脚本后续执行，立刻退出
            breakErrorCode=255,                     # 遇到命令行错误时候的退出代码
            xlog=None,                              # 扩展日志信息文件输出名，None表示不需要
            Console=sys.stdout,                     # 控制台输出，默认为sys.stdout,即标准输出
            HeadlessMode=False,                     # 是否为无终端模式，无终端模式下，任何屏幕信息都不会被输出
            WorkerName='MAIN',                      # 程序别名，可用来区分不同的应用程序,
            logger=None,                            # 程序输出日志句柄
            clientCharset='UTF-8',                  # 客户端字符集，在读取SQL文件时，采纳这个字符集，默认为UTF-8
            resultCharset='UTF-8',                  # 输出字符集，在打印输出文件，日志的时候均采用这个字符集
            profile=None,                           # 程序初始化执行脚本
            scripttimeout=-1,                       # 程序的脚本超时时间，默认为不限制
            suitename=None,                         # 程序所在的SuiteName
            casename=None,                          # 程序所在的CaseName
            namespace=None,                         # 程序的默认命名空间
    ):
        self.db_saved_conn = {}                         # 数据库Session备份
        self.cmdMappingHandler = CmdMapping()           # 函数句柄，处理SQLMapping信息
        self.cmdExecuteHandler = CmdExecute()           # 函数句柄，具体来执行语句
        self.httpHandler = urllib3.PoolManager()        # Http请求线程池，用于处理API请求
        self.testOptions = TestOptions()                # 程序运行中各种参数
        self.HdfsHandler = HDFSWrapper()                # HDFS文件操作
        self.JobHandler = JOBManager()                  # 并发任务管理器
        self.DataHandler = DataWrapper()                # 随机临时数处理
        self.MetaHandler = TestCliMeta()                # SQLCli元数据
        self.SpoolFileHandler = []                      # Spool文件句柄, 是一个数组，可能发生嵌套
        self.EchoFileHandler = None                     # 当前回显文件句柄
        self.AppOptions = None                          # 应用程序的配置参数
        self.Encoding = None                            # 应用程序的Encoding信息
        self.prompt_app = None                          # PromptKit控制台
        self.echofilename = None                        # 当前回显文件的文件名称
        self.Version = __version__                      # 当前程序版本
        self.xlogFile = None                            # xlog文件名
        self.xlogFileHandle = None                      # xlog文件句柄
        self.xlogFileLocker = None                      # 进程锁, 用来在输出perf文件的时候控制并发写文件
        self.breakWithError = breakWithError            # 是否在遇到错误的时候退出
        self.breakErrorCode = breakErrorCode            # 遇到错误的退出代码
        
        # 数据库连接的各种参数
        # 每次连接后需要保存这些变量，下次可以直接重新连接，如果不填写相关信息，则默认上次连接信息
        self.db_conn = None                             # 当前应用的数据库连接句柄
        self.db_sessionName = None                      # 当前会话的Session的名字
        self.db_url = None                              # 数据库连接URL
        self.db_username = None                         # 数据库连接用户名
        self.db_password = None                         # 数据库连接用户口令
        self.db_driver = None                           # 数据库驱动方式 JDBC？ODBC
        self.db_driverSchema = None                     # 数据库驱动类型  mysql? oracle？
        self.db_driverType = None                       # 数据库驱动类型  tcp? mem?
        self.db_host = None                             # 数据库连接主机
        self.db_port = None                             # 数据库连接端口
        self.db_service = None                          # 数据库连接服务
        self.db_parameters = None                       # 数据库连接额外参数

        # NLS处理，设置字符集
        if clientCharset is not None:                   # 客户端脚本字符集
            self.testOptions.set("SCRIPT_ENCODING", clientCharset)
            self.testOptions.set("RESULT_ENCODING", resultCharset)
        if resultCharset is not None:                   # 客户端结果字符集
            self.testOptions.set("RESULT_ENCODING", resultCharset)

        self.WorkerName = WorkerName                    # 当前进程名称. 如果有参数传递，以参数为准
        self.profile = []                               # 程序的初始化脚本文件
        self.lastComment = None                       # 如果当前SQL之前的内容完全是注释，则注释带到这里

        # 传递各种参数
        self.commandScript = script
        self.commandMap = commandMap
        self.nologo = nologo
        self.logon = logon
        self.logfilename = logfilename
        self.Console = Console
        self.HeadlessMode = HeadlessMode
        self.xlogFile = xlog
        if HeadlessMode:
            self.Console = open(os.devnull, "w")
        self.logger = logger
        self.suitename = suitename
        self.casename = casename
        # 运行空间，默认情况下是SQL
        # 如果用户指定，以用户指定为准
        # 如果用户没有指定，且脚本文件名后缀是api，则空间为API
        # 其他情况下运行空间为SQL
        self.nameSpace = "SQL"
        if namespace:
            self.nameSpace = namespace
        else:
            if script:
                if str(script).upper().endswith("API"):
                    self.nameSpace = "API"
        self.testOptions.set("NAMESPACE", self.nameSpace)

        # profile的顺序， <PYTHON_PACKAGE>/testcli/profile/default， TESTCLI_HOME/profile/default , user define
        if os.path.isfile(os.path.join(os.path.dirname(__file__), "profile", "default")):
            if os.path.getsize(os.path.join(os.path.dirname(__file__), "profile", "default")) > 0:
                self.profile.append(os.path.join(os.path.dirname(__file__), "profile", "default"))
        if "TESTCLI_HOME" in os.environ:
            if os.path.isfile(os.path.join(os.environ["TESTCLI_HOME"], "profile", "default")):
                self.profile.append(os.path.join(os.environ["TESTCLI_HOME"], "profile", "default"))
        if profile is not None:
            # os.path.isfile 不能检查带有单引号的文件信息，所以这里检查的时候不包含单引号
            # start 实际执行的时候需要有单引号，不然由于空格或者其他字符可能会导致SQL文件名称被分裂
            if str(profile).startswith("'") and str(profile).endswith("'"):
                m_Profile = str(profile)[1:-1]
            else:
                m_Profile = str(profile).strip()
            if os.path.isfile(m_Profile):
                self.profile.append(str(profile))
            else:
                if "TESTCLI_DEBUG" in os.environ:
                    print("Profile does not exist ! Will ignore it. [" + m_Profile + "]")
        if "TESTCLI_DEBUG" in os.environ:
            for m_Profile in self.profile:
                print("Profile = [" + str(m_Profile) + "]")

        # 设置脚本的超时时间
        self.testOptions.set("SCRIPT_TIMEOUT", scripttimeout)

        # 设置self.JobHandler， 默认情况下，子进程启动的进程进程信息来自于父进程
        self.JobHandler.setProcessContextInfo("logon", self.logon)
        self.JobHandler.setProcessContextInfo("nologo", self.nologo)
        self.JobHandler.setProcessContextInfo("commandMap", self.commandMap)
        self.JobHandler.setProcessContextInfo("xlog", xlog)
        self.JobHandler.setProcessContextInfo("logfilename", self.logfilename)
        self.JobHandler.setProcessContextInfo("script", self.commandScript)

        # 设置其他的变量
        self.cmdExecuteHandler.cliHandler = self
        self.cmdExecuteHandler.script = script
        self.cmdExecuteHandler.testOptions = self.testOptions
        self.cmdExecuteHandler.workerName = self.WorkerName
        self.cmdExecuteHandler.cmdMappingHandler = self.cmdMappingHandler

        self.DataHandler.SQLOptions = self.testOptions

        # 设置WHENEVER_ERROR
        if breakWithError:
            self.testOptions.set("WHENEVER_ERROR", "EXIT " + str(self.breakErrorCode))
        else:
            self.testOptions.set("WHENEVER_ERROR", "CONTINUE")

        # 加载程序的配置文件
        self.AppOptions = configparser.ConfigParser()
        m_conf_filename = os.path.join(os.path.dirname(__file__), "conf", "testcli.ini")
        if os.path.exists(m_conf_filename):
            self.AppOptions.read(m_conf_filename)
        else:
            raise TestCliException("Can not open inifile for read [" + m_conf_filename + "]")

        # 打开输出日志, 如果打开失败，就直接退出
        try:
            if self.logfilename is not None:
                self.logfile = open(self.logfilename, mode="w", encoding=self.testOptions.get("RESULT_ENCODING"))
                self.cmdExecuteHandler.logfile = self.logfile
        except IOError:
            if "TESTCLI_DEBUG" in os.environ:
                print('traceback.print_exc():\n%s' % traceback.print_exc())
                print('traceback.format_exc():\n%s' % traceback.format_exc())
            raise TestCliException("Can not open logfile for write [" + self.logfilename + "]")

        # 加载已经被隐式包含的数据库驱动，文件放置在TestCli\jlib下
        m_jlib_directory = os.path.join(os.path.dirname(__file__), "jlib")
        if self.db_connectionConf is None:
            self.db_connectionConf = []
        if self.AppOptions is not None:
            for row in self.AppOptions.items("driver"):
                m_DriverName = None
                m_JarFullFileName = []
                m_JDBCURL = None
                m_JDBCProp = None
                m_jar_filename = None
                m_DatabaseType = row[0].strip()
                for m_driversection in str(row[1]).split(','):
                    m_driversection = m_driversection.strip()
                    if m_DriverName is None:
                        try:
                            m_DriverName = self.AppOptions.get(m_driversection, "driver")
                        except (configparser.NoSectionError, configparser.NoOptionError):
                            m_DriverName = None
                    if m_JDBCURL is None:
                        try:
                            m_JDBCURL = self.AppOptions.get(m_driversection, "jdbcurl")
                        except (configparser.NoSectionError, configparser.NoOptionError):
                            m_JDBCURL = None
                    if m_JDBCProp is None:
                        try:
                            m_JDBCProp = self.AppOptions.get(m_driversection, "jdbcprop")
                        except (configparser.NoSectionError, configparser.NoOptionError):
                            m_JDBCProp = None
                    if m_jar_filename is None:
                        try:
                            m_jar_filename = self.AppOptions.get(m_driversection, "filename")
                            if os.path.exists(os.path.join(m_jlib_directory, m_jar_filename)):
                                m_JarFullFileName.append(os.path.join(m_jlib_directory, m_jar_filename))
                                if "TESTCLI_DEBUG" in os.environ:
                                    print("Load jar ..! [" +
                                          os.path.join(m_jlib_directory, m_jar_filename) + "]")
                                m_jar_filename = None
                            else:
                                if "TESTCLI_DEBUG" in os.environ:
                                    print("Driver file does not exist! [" +
                                          os.path.join(m_jlib_directory, m_jar_filename) + "]")
                        except (configparser.NoSectionError, configparser.NoOptionError):
                            m_jar_filename = None
                jarConfig = {"ClassName": m_DriverName,
                             "FullName": m_JarFullFileName,
                             "JDBCURL": m_JDBCURL,
                             "JDBCProp": m_JDBCProp,
                             "Database": m_DatabaseType}
                self.db_connectionConf.append(jarConfig)

        # 设置Meta连接时候需要用到的JarList1
        m_JarList = []
        for jarConfig in self.db_connectionConf:
            m_JarList.extend(jarConfig["FullName"])
        self.MetaHandler.setJVMJarList(m_JarList)

        # 对于子进程，连接到JOB管理服务
        if "TESTCLI_JOBMANAGERURL" in os.environ:
            m_JobManagerURL = os.environ["TESTCLI_JOBMANAGERURL"]
            # 对于被主进程调用的进程，则不需要考虑, 连接到主进程的Meta服务商
            self.MetaHandler.ConnectServer(m_JobManagerURL)
            self.JobHandler.setMetaConn(self.MetaHandler.dbConn)
            self.testOptions.set("JOBMANAGER_METAURL", m_JobManagerURL)

        # 处理传递的映射文件, 首先加载参数的部分，如果环境变量里头有设置，则环境变量部分会叠加参数部分
        self.testOptions.set("TESTREWRITE", "OFF")
        if self.commandMap is not None:  # 如果传递的参数，有Mapping，以参数为准，先加载参数中的Mapping文件
            self.cmdMappingHandler.loadCommandMappings(self.commandScript, self.commandMap)
            self.testOptions.set("TESTREWRITE", "ON")
        if "SQLCLI_COMMANDMAPPING" in os.environ:  # 如果没有参数，则以环境变量中的信息为准
            if len(os.environ["SQLCLI_COMMANDMAPPING"].strip()) > 0:
                self.cmdMappingHandler.loadCommandMappings(self.commandScript, os.environ["SQLCLI_COMMANDMAPPING"])
                self.testOptions.set("TESTREWRITE", "ON")

        # 给Page做准备，PAGE显示的默认换页方式.
        if not os.environ.get("LESS"):
            os.environ["LESS"] = "-RXF"

        # 如果参数要求不显示版本，则不再显示版本
        if not self.nologo:
            self.echo("TestCli Release " + __version__)

        # 处理初始化启动文件，如果需要的话，在处理的过程中不打印任何日志信息
        if len(self.profile) != 0:
            self.testOptions.set('OUTPUT_PREFIX', 'PROFILE')
            self.SQLPrefix = "PROFILE "
            for m_Profile in self.profile:
                if "TESTCLI_DEBUG" in os.environ:
                    print("DEBUG:: Begin SQL profile [" + m_Profile + "] ...")
                self.DoCommand('_start ' + m_Profile)
                if "TESTCLI_DEBUG" in os.environ:
                    print("DEBUG:: End SQL profile [" + m_Profile + "]")
            self.testOptions.set('OUTPUT_PREFIX', '')

    def __del__(self):
        # 关闭LogFile
        if self.logfile is not None:
            self.logfile.flush()
            self.logfile.close()
            self.logfile = None

        # 关闭Meta服务
        if self.MetaHandler is not None:
            self.MetaHandler.ShutdownServer()
            self.MetaHandler = None

        # 关闭xlog的文件句柄
        if self.xlogFileHandle is not None:
            self.xlogFileHandle.close()

    # 执行特殊的命令
    @staticmethod
    def execute_internal_command(cls, arg, **_):
        # 处理并发JOB
        match_obj = re.match(r"(\s+)?job(.*)$", arg, re.IGNORECASE | re.DOTALL)
        if match_obj:
            (title, result, headers, columnTypes, status) = cls.JobHandler.Process_Command(arg)
            yield {
                "title": title,
                "rows": result,
                "headers": headers,
                "columnTypes": columnTypes,
                "status": status
            }
            return

        # 处理Transaction
        match_obj = re.match(r"(\s+)?transaction(.*)$", arg, re.IGNORECASE | re.DOTALL)
        if match_obj:
            (title, result, headers, columnTypes, status) = cls.TransactionHandler.Process_Command(arg)
            yield {
                "title": title,
                "rows": result,
                "headers": headers,
                "columnTypes": columnTypes,
                "status": status
            }
            return

        # 测试管理
        match_obj = re.match(r"(\s+)?test(.*)$", arg, re.IGNORECASE | re.DOTALL)
        if match_obj:
            (title, result, headers, columnTypes, status) = cls.TestHandler.Process_SQLCommand(arg)
            yield {
                "title": title,
                "rows": result,
                "headers": headers,
                "columnTypes": columnTypes,
                "status": status
            }
            return

        # 处理HDFS数据
        match_obj = re.match(r"(\s+)?hdfs(.*)$", arg, re.IGNORECASE | re.DOTALL)
        if match_obj:
            if cls.cmdExecuteHandler.script is not None:
                cls.HdfsHandler.HDFS_LCD(os.path.dirname(cls.cmdExecuteHandler.script))
            (title, result, headers, columnTypes, status) = cls.HdfsHandler.Process_SQLCommand(arg)
            yield {
                "title": title,
                "rows": result,
                "headers": headers,
                "columnTypes": columnTypes,
                "status": status
            }
            return

        # 处理随机数据文件
        match_obj = re.match(r"(\s+)?data(.*)$", arg, re.IGNORECASE | re.DOTALL)
        if match_obj:
            for (title, result, headers, columnTypes, status) in \
                    cls.DataHandler.Process_SQLCommand(arg):
                yield {
                    "title": title,
                    "rows": result,
                    "headers": headers,
                    "columnTypes": columnTypes,
                    "status": status
                }
            return

        # 处理远程主机命令
        match_obj = re.match(r"(\s+)?ssh(.*)$", arg, re.IGNORECASE | re.DOTALL)
        if match_obj:
            for (title, result, headers, columnTypes, status) in \
                    cls.sshHandler.processCommand(arg):
                yield {
                    "title": title,
                    "rows": result,
                    "headers": headers,
                    "columnTypes": columnTypes,
                    "status": status
                }
            return

        # 不认识的internal命令
        raise TestCliException("Unknown internal Command [" + str(arg) + "]. Please double check.")

    # 逐条处理语句
    # 如果执行成功，返回true
    # 如果执行失败，返回false
    def DoCommand(self, text=None):
        if text is None:
            # 判断传入的测试语句， 如果没有传递，则表示控制台程序，需要用户逐行输入语句
            full_text = None
            # 用户一行一行的输入测试语句，一直到输入发生了截止符, 最后的文件截止符号内容就是full_text
            while True:
                try:
                    bottomToolbar = HTML('<b><style bg="ansired">' + saxutils.escape(
                                            'Version: ' + self.Version + ' | ' +
                                            (
                                                "Not Connected." if self.db_conn is None
                                                else "Connected with " + self.db_username + "/******@" + self.db_url
                                            )) + ' | ' +
                                         '</style></b>')
                    self.prompt_app.bottom_toolbar = bottomToolbar
                    if full_text is None:
                        text = self.prompt_app.prompt(self.testOptions.get('NAMESPACE') + '> ')
                    else:
                        text = self.prompt_app.prompt('   > ')
                except KeyboardInterrupt:
                    # KeyboardInterrupt 表示用户输入了CONTROL+C
                    return True
                except PermissionError:
                    self.echo("TestCli Can't work without valid terminal. "
                              "Use \"--execute\" in case you need run script", err=True, fg="red")
                    return False

                # 拼接语句
                if full_text is None:
                    full_text = text
                else:
                    full_text = full_text + '\n' + text
                if self.testOptions.get('NAMESPACE') == "SQL":
                    # 判断SQL语句是否已经结束
                    (ret_bCommandCompleted, ret_CommandSplitResults, ret_errorCode, ret_errorMsg) = \
                        SQLAnalyze(full_text)
                    if ret_errorCode != 0:
                        # 即使出错（可能是解析规则未覆盖导致，并不一定是真的SQL语句错误），那么除非看到截止符号，就认为语句没有结束
                        if full_text.strip().endswith(';') or full_text.strip().endswith('\n/'):
                            # 语句已经发生错误，没有必要继续运行下去
                            text = full_text
                            break
                    if ret_bCommandCompleted and ret_CommandSplitResults is not None:
                        # 语句已经结束
                        text = full_text
                        break
                elif self.testOptions.get('NAMESPACE') == "API":
                    # 判断API语句是否已经结束
                    (ret_bCommandCompleted, ret_CommandSplitResults,
                     ret_CommandSplitResultsWithComments, ret_CommandHints,
                     ret_errorCode, ret_errorMsg) = APIAnalyze(full_text)
                    if ret_errorCode != 0:
                        if full_text.strip().endswith(';') or full_text.strip().endswith('\n/'):
                            # 语句已经发生错误，没有必要继续运行下去
                            text = full_text
                            break
                    if ret_bCommandCompleted and ret_CommandSplitResults is not None:
                        # 语句已经结束
                        text = full_text
                        break

        # 执行需要处理的语句
        try:
            def show_result(p_result):
                # 输出显示结果
                if "type" in p_result.keys():
                    if p_result["type"] == "echo":
                        message = p_result["message"]
                        m_EchoFlag = OFLAG_LOGFILE | OFLAG_LOGGER | OFLAG_CONSOLE | OFLAG_ECHO | OFLAG_SPOOL
                        if re.match(r'echo\s+off', p_result["message"], re.IGNORECASE):
                            # Echo Off这个语句，不打印到Echo文件中
                            m_EchoFlag = m_EchoFlag & ~OFLAG_ECHO
                        if p_result["script"] is None:
                            # 控制台应用，不再打印SQL语句到控制台（因为用户已经输入了)
                            m_EchoFlag = m_EchoFlag & ~OFLAG_CONSOLE
                        self.echo(message, m_EchoFlag)
                    elif p_result["type"] == "parse":
                        if self.testOptions.get("ECHO").upper() == 'ON':
                            # 首先打印原始SQL
                            m_EchoFlag = OFLAG_LOGFILE | OFLAG_LOGGER | OFLAG_CONSOLE | OFLAG_SPOOL
                            # Spool off这个语句，不打印到Spool中
                            if p_result["rawCommand"] is not None:
                                if p_result["rawCommand"]["name"] == "SPOOL":
                                    if p_result["rawCommand"]["file"].strip().upper() == "OFF":
                                        m_EchoFlag = m_EchoFlag & ~OFLAG_SPOOL
                            if p_result["script"] is None:
                                # 控制台应用，不再打印SQL语句到控制台（因为用户已经输入了)
                                m_EchoFlag = m_EchoFlag & ~OFLAG_CONSOLE
                            if p_result["formattedCommand"] is not None:
                                self.echo(p_result["formattedCommand"], m_EchoFlag)
                            # 打印改写后的SQL
                            if "rewrotedCommand" in p_result.keys() and p_result["rewrotedCommand"] is not None:
                                if len(p_result["rewrotedCommand"]) != 0:
                                    m_EchoFlag = OFLAG_LOGFILE | OFLAG_LOGGER | OFLAG_CONSOLE | OFLAG_SPOOL
                                    message = "\n".join(p_result["rewrotedCommand"])
                                    self.echo(message, m_EchoFlag)
                    elif p_result["type"] == "result":
                        title = p_result["title"]
                        cur = p_result["rows"]
                        headers = p_result["headers"]
                        columnTypes = p_result["columnTypes"]
                        status = p_result["status"]

                        # 不控制每行的长度
                        max_width = None

                        # title 包含原有语句的SQL信息，如果ECHO打开的话
                        # headers 包含原有语句的列名
                        # cur 是语句的执行结果
                        # output_format 输出格式
                        #   ascii              默认，即表格格式(第三方工具实现，暂时保留以避免不兼容现象)
                        #   csv                csv格式显示
                        #   tab                表格形式（用format_output_tab自己编写)
                        formatted = self.format_output(
                            title, cur, headers, columnTypes,
                            self.testOptions.get("OUTPUT_FORMAT").lower(),
                            max_width
                        )

                        # 输出显示信息
                        try:
                            if self.testOptions.get('FEEDBACK').upper() == 'ON':
                                self.output(formatted, status)
                            else:
                                # 关闭FeedBack的情况下不回显Status信息
                                self.output(formatted, None)
                        except KeyboardInterrupt:
                            # 显示过程中用户按下了CTRL+C
                            pass
                    elif p_result["type"] == "error":
                        if self.testOptions.get('OUTPUT_ERROR_PREFIX') != '':
                            m_ErrorLines = p_result["message"].splitlines()
                            m_ErrorPrefix = self.testOptions.get('OUTPUT_ERROR_PREFIX')
                            for nPos in range(0, len(m_ErrorLines)):
                                m_ErrorLines[nPos] = m_ErrorPrefix + ":  " + m_ErrorLines[nPos]
                            self.echo("\n".join(m_ErrorLines))
                        else:
                            self.echo(p_result["message"])
                    elif p_result["type"] == "statistics":
                        self.writeExtendLog(p_result)
                    else:
                        raise TestCliException("internal error. unknown sql type error. " + str(p_result["type"]))
                else:
                    raise TestCliException("internal error. incomplete return. missed type" + str(p_result))
            # End Of show_result

            # 执行指定的SQL
            for result in \
                    self.cmdExecuteHandler.runStatement(
                        statement=text,
                        commandScriptFile="Console",
                        nameSpace=self.nameSpace):
                # 打印结果
                show_result(result)

                # 记录语句的统计信息
                if result["type"] == "statistics":
                    if self.testOptions.get('TIMING').upper() == 'ON':
                        self.echo('Running time elapsed: %9.2f seconds' % result["elapsed"])
                    if self.testOptions.get('TIME').upper() == 'ON':
                        self.echo('Current clock time  :' + strftime("%Y-%m-%d %H:%M:%S", localtime()))
                if result["type"] == "error":
                    # 如果遇到了错误，且设置了breakWithError，则立刻退出
                    if self.breakWithError:
                        self.exitValue = self.breakErrorCode
                        raise EOFError

            # 返回正确执行的消息
            return True
        except EOFError as e:
            # 当调用了exit或者quit的时候，会收到EOFError，这里直接抛出
            raise e
        except TestCliException as e:
            if "TESTCLI_DEBUG" in os.environ:
                print('traceback.print_exc():\n%s' % traceback.print_exc())
                print('traceback.format_exc():\n%s' % traceback.format_exc())
            # 用户执行的SQL出了错误, 由于SQLExecute已经打印了错误消息，这里直接退出
            self.output(None, e.message)
        except Exception as e:
            if "TESTCLI_DEBUG" in os.environ:
                print('traceback.print_exc():\n%s' % traceback.print_exc())
                print('traceback.format_exc():\n%s' % traceback.format_exc())
            self.echo(repr(e), err=True, fg="red")
            return False

    # 下载程序所需要的各种Jar包
    def syncdriver(self):
        # 加载程序的配置文件
        self.AppOptions = configparser.ConfigParser()
        m_conf_filename = os.path.join(os.path.dirname(__file__), "conf", "testcli.ini")
        if os.path.exists(m_conf_filename):
            self.AppOptions.read(m_conf_filename)

        # 下载运行需要的各种Jar包
        for row in self.AppOptions.items("driver"):
            print("Checking driver [" + row[0] + "] ... ")
            for m_driversection in str(row[1]).split(','):
                m_driversection = m_driversection.strip()
                try:
                    m_driver_filename = self.AppOptions.get(m_driversection, "filename")
                    m_driver_downloadurl = self.AppOptions.get(m_driversection, "downloadurl")
                    m_driver_filemd5 = self.AppOptions.get(m_driversection, "md5")

                    m_LocalJarFile = os.path.join(os.path.dirname(__file__), "jlib", m_driver_filename)
                    m_LocalJarPath = os.path.join(os.path.dirname(__file__), "jlib")
                    if not os.path.isdir(m_LocalJarPath):
                        os.makedirs(m_LocalJarPath)

                    if os.path.exists(m_LocalJarFile):
                        with open(m_LocalJarFile, 'rb') as fp:
                            data = fp.read()
                        file_md5 = hashlib.md5(data).hexdigest()
                        if "TESTCLI_DEBUG" in os.environ:
                            print("File=[" + m_driver_filename + "], MD5=[" + file_md5 + "]")
                    else:
                        if "TESTCLI_DEBUG" in os.environ:
                            print("File=[" + m_driver_filename + "] does not exist!")
                        file_md5 = ""
                    if file_md5 != m_driver_filemd5.strip():
                        print("Driver [" + m_driversection + "], need upgrade ...")
                        # 重新下载新的文件到本地
                        try:
                            http = urllib3.PoolManager()
                            with http.request('GET', m_driver_downloadurl, preload_content=False) as r, \
                                    open(m_LocalJarFile, 'wb') as out_file:
                                shutil.copyfileobj(r, out_file)
                        except URLError:
                            print('traceback.print_exc():\n%s' % traceback.print_exc())
                            print('traceback.format_exc():\n%s' % traceback.format_exc())
                            print("")
                            print("Driver [" + m_driversection + "] download failed.")
                            continue
                        with open(m_LocalJarFile, 'rb') as fp:
                            data = fp.read()
                        file_md5 = hashlib.md5(data).hexdigest()
                        if file_md5 != m_driver_filemd5.strip():
                            print("Driver [" + m_driversection + "] consistent check failed. "
                                                                 "Remote MD5=[" + str(file_md5) + "]")
                        else:
                            print("Driver [" + m_driversection + "] is up-to-date.")
                    else:
                        print("Driver [" + m_driversection + "] is up-to-date.")
                except (configparser.NoSectionError, configparser.NoOptionError):
                    print("Bad driver config [" + m_driversection + "], Skip it ...")

    # 主程序
    def run_cli(self):
        # 如果运行在脚本方式下，不再调用PromptSession
        # 运行在无终端的模式下，也不会调用PromptSession
        # 对于脚本程序，在执行脚本完成后就会自动退出
        if self.commandScript is None and not self.HeadlessMode:
            # 如果可能，在用户的当前目录下生成sqlcli-history.txt隐含文件
            user_home = os.path.expanduser('~')
            m_HistoryFile = os.path.join(user_home, '.testcli-history.txt')
            if os.access(user_home, os.W_OK):
                history = FileHistory(m_HistoryFile)
                enable_history_search = True
            else:
                if "TESTCLI_DEBUG" in os.environ:
                    print("No write access to [" + str(m_HistoryFile) + "]. disable command history feature.")
                history = None
                enable_history_search = False

            self.prompt_app = PromptSession(history=history,
                                            enable_history_search=enable_history_search)

        # 设置主程序的标题，随后开始运行程序
        cliProcessTitleBak = setproctitle.getproctitle()
        setproctitle.setproctitle('TestCli MAIN ' + " Script:" + str(self.commandScript))

        # 由于外界的classpath可能被后来的JPYPE加载，所以这里不能看外界的classpath
        for s in os.environ:
            if s.lower() == 'classpath':
                if "TESTCLI_DEBUG" in os.environ:
                    print("Ignore user classpath setting.")
                os.environ.pop(s)

        try:
            # 开始依次处理控制台送来的语句
            if not self.commandScript:
                while True:
                    # 循环从控制台读取命令
                    if not self.DoCommand():
                        raise EOFError

            # 如果用户指定了用户名，口令，尝试直接进行数据库连接
            if self.logon:
                if not self.DoCommand("_connect " + str(self.logon)):
                    raise EOFError

            # 如果传递的参数中有脚本文件，先执行脚本文件, 执行完成后自动退出
            try:
                # 如果有脚本目录，则运行的时候切换到脚本所在的目录下，运行结束后要返回当前目录
                currentPwd = os.getcwd()
                scriptDir = os.path.dirname(str(self.commandScript))
                scriptBase = os.path.basename(str(self.commandScript))
                if scriptDir.strip() != "":
                    # 如果脚本不是当前目录，需要切换到脚本目录下
                    # 如果脚本是当前目录，切换到空目录会报错，所以不能切换
                    os.chdir(scriptDir)
                self.DoCommand('_start ' + scriptBase)
                if scriptDir.strip() != "":
                    # 如果发生了脚本切换，则执行脚本后要返回切换前的目录
                    os.chdir(currentPwd)
            except TestCliException:
                raise EOFError
            self.DoCommand('_exit')
        except (TestCliException, EOFError):
            pass

        # 退出进程, 如果要求不显示logo，则也不会显示Disconnected字样
        if self.exitValue == 0:
            if not self.nologo:
                self.echo("Disconnected.")
        else:
            if not self.nologo:
                self.echo("Disconnected with [" + str(self.exitValue) + "].")

        # 关闭LogFile
        if self.logfile is not None:
            self.logfile.flush()
            self.logfile.close()
            self.logfile = None

        # 还原进程标题
        setproctitle.setproctitle(cliProcessTitleBak)

        # 取消进程共享服务的注册信息
        self.JobHandler.unregisterjob()
        self.JobHandler.unregisterAgent()

        # 关闭Meta服务
        if self.MetaHandler is not None:
            self.MetaHandler.ShutdownServer()
            self.MetaHandler = None

        # 退出runCli
        return self.exitValue

    def echo(self, s,
             Flags=OFLAG_LOGFILE | OFLAG_LOGGER | OFLAG_CONSOLE | OFLAG_SPOOL | OFLAG_ECHO,
             **kwargs):
        # 输出目的地
        # 1：  程序日志文件 logfile
        # 2：  程序的logger，用于在第三方调用时候的Console显示
        # 3：  当前屏幕控制台
        # 4：  程序的Spool文件
        # 5:   程序的ECHO回显文件
        if self.testOptions.get("SILENT").upper() != 'ON':
            if len(self.testOptions.get('OUTPUT_PREFIX')) != 0:
                m_OutputPrefix = self.testOptions.get('OUTPUT_PREFIX') + " "
            else:
                m_OutputPrefix = ''
            match_obj = re.match(self.nameSpace + r">(\s+)?set(\s+)?OUTPUT_PREFIX(\s+)?$", s, re.IGNORECASE | re.DOTALL)
            if match_obj:
                m_OutputPrefix = ''
            if Flags & OFLAG_LOGFILE:
                if self.logfile is not None:
                    print(m_OutputPrefix + s, file=self.logfile)
                    self.logfile.flush()
            if Flags & OFLAG_SPOOL:
                if self.SpoolFileHandler is not None:
                    for m_SpoolFileHandler in self.SpoolFileHandler:
                        print(m_OutputPrefix + s, file=m_SpoolFileHandler)
                        m_SpoolFileHandler.flush()
            if Flags & OFLAG_LOGGER:
                if self.logger is not None:
                    self.logger.info(m_OutputPrefix + s)
            if Flags & OFLAG_ECHO:
                if self.EchoFileHandler is not None:
                    print(m_OutputPrefix + s, file=self.EchoFileHandler)
                    self.EchoFileHandler.flush()
            if Flags & OFLAG_CONSOLE:
                try:
                    click.secho(m_OutputPrefix + s, **kwargs, file=self.Console)
                except UnicodeEncodeError as ue:
                    # Unicode Error, This is console issue, Skip
                    if "TESTCLI_DEBUG" in os.environ:
                        print("Console output error:: " + repr(ue))

    def output(self, output, status=None):
        if output:
            # size    记录了 每页输出最大行数，以及行的宽度。  Size(rows=30, columns=119)
            # margin  记录了每页需要留下多少边界行，如状态显示信息等 （2 或者 3）
            m_size_rows = 30
            m_size_columns = 119
            margin = 3

            # 打印输出信息
            fits = True
            buf = []
            output_via_pager = (self.testOptions.get("PAGE").upper() == "ON")
            for i, line in enumerate(output, 1):
                if fits or output_via_pager:
                    # buffering
                    buf.append(line)
                    if len(line) > m_size_columns or i > (m_size_rows - margin):
                        # 如果行超过页要求，或者行内容过长，且没有分页要求的话，直接显示
                        fits = False
                        if not output_via_pager:
                            # doesn't fit, flush buffer
                            for bufline in buf:
                                self.echo(bufline)
                            buf = []
                else:
                    self.echo(line)

            if buf:
                if output_via_pager:
                    click.echo_via_pager("\n".join(buf))
                else:
                    for line in buf:
                        self.echo(line)

        if status:
            self.echo(status)

    def format_output_csv(self, headers, columnTypes, cur):
        # 将屏幕输出按照CSV格式进行输出
        m_csv_delimiter = self.testOptions.get("CSV_DELIMITER")
        m_csv_quotechar = self.testOptions.get("CSV_QUOTECHAR")
        if m_csv_delimiter.find("\\t") != -1:
            m_csv_delimiter = m_csv_delimiter.replace("\\t", '\t')
        if m_csv_delimiter.find("\\s") != -1:
            m_csv_delimiter = m_csv_delimiter.replace("\\s", ' ')

        # 打印字段名称
        if self.testOptions.get("CSV_HEADER") == "ON":
            m_row = ""
            for pos in range(0, len(headers)):
                m_row = m_row + str(headers[pos])
                if pos != len(headers) - 1:
                    m_row = m_row + m_csv_delimiter
            yield str(m_row)

        # 打印字段内容
        for row in cur:
            m_row = ""
            for pos in range(0, len(row)):
                if row[pos] is None:
                    if columnTypes is not None:
                        if columnTypes[pos] in ("VARCHAR", "LONGVARCHAR", "CHAR", "CLOB", "NCLOB"):
                            m_row = m_row + m_csv_quotechar + m_csv_quotechar
                else:
                    if columnTypes is None:
                        m_row = m_row + str(row[pos])
                    else:
                        if columnTypes[pos] in ("VARCHAR", "LONGVARCHAR", "CHAR", "CLOB", "NCLOB"):
                            m_row = m_row + m_csv_quotechar + str(row[pos]) + m_csv_quotechar
                        else:
                            m_row = m_row + str(row[pos])
                if pos != len(row) - 1:
                    m_row = m_row + m_csv_delimiter
            yield str(m_row)

    def format_output_leagcy(self, headers, cur):
        # 这个函数完全是为了兼容旧的tab格式
        def wide_chars(s):
            # 判断字符串中包含的中文字符数量
            if isinstance(s, str):
                # W  宽字符
                # F  全角字符
                # H  半角字符
                # Na  窄字符
                # A   不明确的
                # N   正常字符
                return sum(unicodedata.east_asian_width(x) in ['W', 'F'] for x in s)
            else:
                return 0

        if self:
            pass
        # 将屏幕输出按照表格进行输出
        # 记录每一列的最大显示长度
        m_ColumnLength = []
        # 首先将表头的字段长度记录其中
        for m_Header in headers:
            m_ColumnLength.append(len(m_Header) + wide_chars(m_Header))
        # 查找列的最大字段长度
        for m_Row in cur:
            for pos in range(0, len(m_Row)):
                if m_Row[pos] is None:
                    # 空值打印为<null>
                    if m_ColumnLength[pos] < len('<null>'):
                        m_ColumnLength[pos] = len('<null>')
                elif isinstance(m_Row[pos], str):
                    m_PrintValue = m_Row[pos]
                    m_PrintValue = m_PrintValue.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
                    if len(m_PrintValue) + wide_chars(m_PrintValue) > m_ColumnLength[pos]:
                        # 为了保持长度一致，长度计算的时候扣掉中文的显示长度
                        m_ColumnLength[pos] = len(m_PrintValue) + wide_chars(m_PrintValue)
                else:
                    if len(str(m_Row[pos])) + wide_chars(m_Row[pos]) > m_ColumnLength[pos]:
                        m_ColumnLength[pos] = len(str(m_Row[pos])) + wide_chars(m_Row[pos])
        # 打印表格上边框
        # 计算表格输出的长度, 开头有一个竖线，随后每个字段内容前有一个空格，后有一个空格加上竖线
        # 1 + [（字段长度+3） *]
        m_TableBoxLine = '+'
        for m_Length in m_ColumnLength:
            m_TableBoxLine = m_TableBoxLine + (m_Length + 2) * '-' + '+'
        yield m_TableBoxLine
        # 打印表头以及表头下面的分割线
        m_TableContentLine = '|'
        for pos in range(0, len(headers)):
            m_TableContentLine = m_TableContentLine + ' ' + \
                                 str(headers[pos]).ljust(m_ColumnLength[pos] - wide_chars(headers[pos])) + ' |'
        yield m_TableContentLine
        yield m_TableBoxLine
        # 打印字段内容
        for m_Row in cur:
            m_output = [m_Row]
            for m_iter in m_output:
                m_TableContentLine = '|'
                for pos in range(0, len(m_iter)):
                    if m_iter[pos] is None:
                        m_PrintValue = '<null>'
                    elif isinstance(m_iter[pos], str):
                        m_PrintValue = m_Row[pos]
                        m_PrintValue = m_PrintValue.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
                    else:
                        m_PrintValue = str(m_iter[pos])
                    # 所有内容字符串左对齐
                    m_TableContentLine = \
                        m_TableContentLine + ' ' + \
                        m_PrintValue.ljust(m_ColumnLength[pos] - wide_chars(m_PrintValue)) + ' |'
                yield m_TableContentLine
        # 打印表格下边框
        yield m_TableBoxLine

    def format_output_tab(self, headers, columnTypes, cur):
        def wide_chars(s):
            # 判断字符串中包含的中文字符数量
            if isinstance(s, str):
                # W  宽字符
                # F  全角字符
                # H  半角字符
                # Na  窄字符
                # A   不明确的
                # N   正常字符
                return sum(unicodedata.east_asian_width(x) in ['W', 'F'] for x in s)
            else:
                return 0

        if self:
            pass
        # 将屏幕输出按照表格进行输出
        # 记录每一列的最大显示长度
        m_ColumnLength = []
        # 首先将表头的字段长度记录其中
        for m_Header in headers:
            m_ColumnLength.append(len(m_Header) + wide_chars(m_Header))
        # 查找列的最大字段长度
        for m_Row in cur:
            for pos in range(0, len(m_Row)):
                if m_Row[pos] is None:
                    # 空值打印为<null>
                    if m_ColumnLength[pos] < len('<null>'):
                        m_ColumnLength[pos] = len('<null>')
                elif isinstance(m_Row[pos], str):
                    for m_iter in m_Row[pos].split('\n'):
                        if len(m_iter) + wide_chars(m_iter) > m_ColumnLength[pos]:
                            # 为了保持长度一致，长度计算的时候扣掉中文的显示长度
                            m_ColumnLength[pos] = len(m_iter) + wide_chars(m_iter)
                else:
                    if len(str(m_Row[pos])) + wide_chars(m_Row[pos]) > m_ColumnLength[pos]:
                        m_ColumnLength[pos] = len(str(m_Row[pos])) + wide_chars(m_Row[pos])
        # 打印表格上边框
        # 计算表格输出的长度, 开头有一个竖线，随后每个字段内容前有一个空格，后有一个空格加上竖线
        # 1 + [（字段长度+3） *]
        m_TableBoxLine = '+--------+'
        for m_Length in m_ColumnLength:
            m_TableBoxLine = m_TableBoxLine + (m_Length + 2) * '-' + '+'
        yield m_TableBoxLine
        # 打印表头以及表头下面的分割线
        m_TableContentLine = '|   ##   |'
        for pos in range(0, len(headers)):
            m_TableContentLine = \
                m_TableContentLine + \
                ' ' + str(headers[pos]).center(m_ColumnLength[pos] - wide_chars(headers[pos])) + ' |'
        yield m_TableContentLine
        yield m_TableBoxLine
        # 打印字段内容
        m_RowNo = 0
        for m_Row in cur:
            m_RowNo = m_RowNo + 1
            # 首先计算改行应该打印的高度（行中的内容可能右换行符号）
            m_RowHeight = 1
            for pos in range(0, len(m_Row)):
                if isinstance(m_Row[pos], str):
                    if len(m_Row[pos].split('\n')) > m_RowHeight:
                        m_RowHeight = len(m_Row[pos].split('\n'))
            # 首先构造一个空的结果集，行数为计划打印的行高
            m_output = []
            if m_RowHeight == 1:
                m_output.append(m_Row)
            else:
                for m_iter in range(0, m_RowHeight):
                    m_output.append(())
                # 依次填入数据
                for pos in range(0, len(m_Row)):
                    if isinstance(m_Row[pos], str):
                        m_SplitColumnValue = m_Row[pos].split('\n')
                    else:
                        m_SplitColumnValue = [m_Row[pos], ]
                    for m_iter in range(0, m_RowHeight):
                        if len(m_SplitColumnValue) > m_iter:
                            if str(m_SplitColumnValue[m_iter]).endswith('\r'):
                                m_SplitColumnValue[m_iter] = m_SplitColumnValue[m_iter][:-1]
                            m_output[m_iter] = m_output[m_iter] + (m_SplitColumnValue[m_iter],)
                        else:
                            m_output[m_iter] = m_output[m_iter] + ("",)
            m_RowNoPrinted = False
            for m_iter in m_output:
                m_TableContentLine = '|'
                if not m_RowNoPrinted:
                    m_TableContentLine = m_TableContentLine + str(m_RowNo).rjust(7) + ' |'
                    m_RowNoPrinted = True
                else:
                    m_TableContentLine = m_TableContentLine + '        |'
                for pos in range(0, len(m_iter)):
                    if m_iter[pos] is None:
                        m_PrintValue = '<null>'
                    else:
                        m_PrintValue = str(m_iter[pos])
                    if columnTypes is not None:
                        if columnTypes[pos] in \
                                ("VARCHAR", "LONGVARCHAR", "CHAR", "CLOB", "NCLOB", "STRUCT", "ARRAY", "DATE"):
                            # 字符串左对齐
                            m_TableContentLine = \
                                m_TableContentLine + ' ' + \
                                m_PrintValue.ljust(m_ColumnLength[pos] - wide_chars(m_PrintValue)) + ' |'
                        else:
                            # 数值类型右对齐, 不需要考虑wide_chars
                            m_TableContentLine = m_TableContentLine + ' ' + \
                                                 m_PrintValue.rjust(m_ColumnLength[pos]) + ' |'
                    else:
                        # 没有返回columntype, 按照字符串处理
                        m_TableContentLine = \
                            m_TableContentLine + ' ' + \
                            m_PrintValue.ljust(m_ColumnLength[pos] - wide_chars(m_PrintValue)) + ' |'
                yield m_TableContentLine
        # 打印表格下边框
        yield m_TableBoxLine

    def format_output(self, title, cur, headers, columnTypes, p_format_name, max_width=None):
        output = []

        if title:  # Only print the title if it's not None.
            output = itertools.chain(output, [title])

        if cur:
            if max_width is not None:
                cur = list(cur)

            if p_format_name.upper() == 'CSV':
                # 按照CSV格式输出查询结果
                formatted = self.format_output_csv(headers, columnTypes, cur)
            elif p_format_name.upper() == 'TAB':
                # 按照TAB格式输出查询结果
                formatted = self.format_output_tab(headers, columnTypes, cur)
            elif p_format_name.upper() == 'LEGACY':
                # 按照TAB格式输出查询结果
                formatted = self.format_output_leagcy(headers, cur)
            else:
                raise TestCliException("SQLCLI-0000: Unknown output_format. CSV|TAB|LEGACY only")
            if isinstance(formatted, str):
                formatted = formatted.splitlines()
            formatted = iter(formatted)

            # 获得输出信息的首行
            first_line = next(formatted)
            # 获得输出信息的格式控制
            formatted = itertools.chain([first_line], formatted)
            # 返回输出信息
            output = itertools.chain(output, formatted)

        return output

    def writeExtendLog(self, commandResult):
        # 开始时间         StartedTime
        # 消耗时间         elapsed
        # SQL的前20个字母  SQLPrefix
        # 运行状态         SQLStatus
        # 错误日志         ErrorMessage
        # 线程名称         thread_name

        # 如果没有打开性能日志记录文件，直接跳过
        if self.xlogFile is None:
            return

        # 初始化文件加锁机制
        if self.xlogFileLocker is None:
            self.xlogFileLocker = Lock()

        # 多进程，多线程写入，考虑锁冲突
        try:
            self.xlogFileLocker.acquire()
            if self.xlogFileHandle is None:
                # 如果文件已经存在，则删除当前文件
                if os.path.exists(self.xlogFile):
                    os.remove(self.xlogFile)
                # 创建文件，并写入文件头信息
                self.xlogFileHandle = sqlite3.connect(self.xlogFile)
                cursor = self.xlogFileHandle.cursor()
                cursor.execute("Create Table TestCli_Xlog "
                               "("
                               "  Script          TEXT,"
                               "  Started         DATETIME,"
                               "  Elapsed         NUMERIC,"
                               "  RawCommand      TEXT,"
                               "  CommandType     TEXT,"
                               "  Command         TEXT,"
                               "  CommandStatus   TEXT,"
                               "  ErrorCode       TEXT,"
                               "  WorkerName      TEXT,"
                               "  SuiteName       TEXT,"
                               "  CaseName        TEXT,"
                               "  ScenarioName    TEXT"
                               ")"
                               "")
                cursor.close()

            # 对于多线程运行，这里的thread_name格式为JOB_NAME#副本数-完成次数
            # 对于单线程运行，这里的thread_name格式为固定的MAIN
            threadName = str(commandResult["thread_name"])

            # 写入内容信息
            if self.commandScript is None:
                script = "Console"
            else:
                script = str(os.path.basename(self.commandScript))

            # 打开xLog文件
            if self.xlogFileHandle is not None:
                self.xlogFileHandle = sqlite3.connect(self.xlogFile)
            cursor = self.xlogFileHandle.cursor()
            data = (
                script,
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(commandResult["startedTime"])),
                "%8.2f" % commandResult["elapsed"],
                str(commandResult["rawCommand"]),
                str(commandResult["commandType"]),
                str(commandResult["command"]),
                str(commandResult["commandStatus"]),
                str(commandResult["errorCode"]),
                str(threadName),
                str(self.suitename),
                str(self.casename),
                str(commandResult["scenario"])
            )
            cursor.execute(
                "Insert Into TestCli_Xlog(Script,Started,Elapsed,RawCommand,"
                "CommandType,Command,CommandStatus,ErrorCode,WorkerName,SuiteName,CaseName,ScenarioName) "
                "Values(?,?,?,?, ?,?,?,?,?,?,?,?)",
                data
            )
            cursor.close()
            self.xlogFileHandle.commit()
        except Exception as ex:
            print("Internal error:: xlog file [" + str(self.xlogFile) + "] write not complete. " + repr(ex))
        finally:
            self.xlogFileLocker.release()
