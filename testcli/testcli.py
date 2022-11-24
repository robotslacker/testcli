# -*- coding: utf-8 -*-
import os
import sys
import traceback
import re
import time
from xml.sax import saxutils

import setproctitle
import click
import configparser
import hashlib
import codecs
import subprocess
import unicodedata
import itertools
import urllib3
import shutil
from multiprocessing import Lock
from time import strftime, localtime
from urllib.error import URLError
import jpype

from prompt_toolkit.history import FileHistory
from prompt_toolkit.shortcuts import PromptSession
from prompt_toolkit.formatted_text import HTML

# 加载JDBC驱动和ODBC驱动
from .sqlclijdbc import connect as jdbcconnect
from .sqlclijdbc import SQLCliJDBCTimeOutException
from .sqlclijdbc import SQLCliJDBCException

from .cmdexecute import CmdExecute
from .cmdmapping import CmdMapping
from .testwrapper import TestWrapper
from .hdfswrapper import HDFSWrapper
from .sshwrapper import SshWrapper
from .testcliexception import TestCliException
from .testclimeta import TestCliMeta
from .sqlclijobmanager import JOBManager
from .sqlclitransactionmanager import TransactionManager
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

# 定义执行内嵌脚本时候的全局环境变量
globalEmbeddScriptScope = {}
localEmbeddScriptScope = {}


class TestCli(object):
    # 从配置文件中加载的连接配置信息
    db_connectionConf = None

    # SQLCli的初始化参数
    logon = None
    logfilename = None
    script = None
    sqlmap = None
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
            sqlmap=None,                            # SQL映射文件名，None表示不存在
            nologo=False,                           # 是否不打印登陆时的Logo信息，True的时候不打印
            breakwitherror=False,                   # 遇到SQL错误，是否中断脚本后续执行，立刻退出
            sqlperf=None,                           # SQL审计文件输出名，None表示不需要
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
        self.TestHandler = TestWrapper()                # 测试管理
        self.HdfsHandler = HDFSWrapper()                # HDFS文件操作
        self.JobHandler = JOBManager()                  # 并发任务管理器
        self.TransactionHandler = TransactionManager()  # 事务管理器
        self.DataHandler = DataWrapper()                # 随机临时数处理
        self.MetaHandler = TestCliMeta()                # SQLCli元数据
        self.sshHandler = SshWrapper()                  # 处理SSH连接
        self.SpoolFileHandler = []                      # Spool文件句柄, 是一个数组，可能发生嵌套
        self.EchoFileHandler = None                     # 当前回显文件句柄
        self.AppOptions = None                          # 应用程序的配置参数
        self.Encoding = None                            # 应用程序的Encoding信息
        self.prompt_app = None                          # PromptKit控制台
        self.echofilename = None                        # 当前回显文件的文件名称
        self.Version = __version__                      # 当前程序版本
        self.ClientID = None                            # 远程连接时的客户端ID
        self.SQLPerfFile = None                         # SQLPerf文件名
        self.SQLPerfFileHandle = None                   # SQLPerf文件句柄
        self.PerfFileLocker = None                      # 进程锁, 用来在输出perf文件的时候控制并发写文件
        self.xlogfilename = None                        # xlog文件名

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
        self.sqlmap = sqlmap
        self.nologo = nologo
        self.logon = logon
        self.logfilename = logfilename
        self.Console = Console
        self.HeadlessMode = HeadlessMode
        self.SQLPerfFile = sqlperf
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
        self.JobHandler.setProcessContextInfo("sqlmap", self.sqlmap)
        self.JobHandler.setProcessContextInfo("sqlperf", sqlperf)
        self.JobHandler.setProcessContextInfo("logfilename", self.logfilename)
        self.JobHandler.setProcessContextInfo("script", self.commandScript)
        self.TransactionHandler.cmdExecuteHandler = self.cmdExecuteHandler

        # 设置其他的变量
        self.cmdExecuteHandler.cliHandler = self
        self.cmdExecuteHandler.script = script
        self.cmdExecuteHandler.testOptions = self.testOptions
        self.cmdExecuteHandler.workerName = self.WorkerName
        self.cmdExecuteHandler.cmdMappingHandler = self.cmdMappingHandler

        self.TestHandler.SQLOptions = self.testOptions
        self.DataHandler.SQLOptions = self.testOptions

        # 设置WHENEVER_SQLERROR
        if breakwitherror:
            self.testOptions.set("WHENEVER_SQLERROR", "EXIT")

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
                m_ODBCURL = None
                m_JDBCProp = None
                m_jar_filename = None
                m_DatabaseType = row[0].strip()
                for m_driversection in str(row[1]).split(','):
                    m_driversection = m_driversection.strip()
                    if m_ODBCURL is None:
                        try:
                            m_ODBCURL = self.AppOptions.get(m_driversection, "odbcurl")
                        except (configparser.NoSectionError, configparser.NoOptionError):
                            m_ODBCURL = None
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
                             "Database": m_DatabaseType,
                             "ODBCURL": m_ODBCURL}
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
            self.TransactionHandler.setMetaConn(self.MetaHandler.dbConn)
            self.testOptions.set("JOBMANAGER_METAURL", m_JobManagerURL)

        # 处理传递的映射文件, 首先加载参数的部分，如果环境变量里头有设置，则环境变量部分会叠加参数部分
        self.testOptions.set("TESTREWRITE", "OFF")
        if self.sqlmap is not None:  # 如果传递的参数，有Mapping，以参数为准，先加载参数中的Mapping文件
            self.cmdMappingHandler.Load_Command_Mappings(self.commandScript, self.sqlmap)
            self.testOptions.set("TESTREWRITE", "ON")
        if "SQLCLI_SQLMAPPING" in os.environ:  # 如果没有参数，则以环境变量中的信息为准
            if len(os.environ["SQLCLI_SQLMAPPING"].strip()) > 0:
                self.cmdMappingHandler.Load_Command_Mappings(self.commandScript, os.environ["SQLCLI_SQLMAPPING"])
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
                self.DoCommand('start ' + m_Profile)
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

    # 退出当前应用程序
    @staticmethod
    def exit(cls, exitValue):
        if cls.script is not None:
            # 运行在脚本模式下，会一直等待所有子进程退出后，再退出本程序
            while True:
                if not cls.JobHandler.isAllJobClosed():
                    # 如果还有没有退出的进程，则不会直接退出程序，会继续等待进程退出
                    time.sleep(3)
                else:
                    break

            # 等待那些已经Running的进程完成， 但是只有Submitted的不考虑在内
            if cls.testOptions.get("JOBMANAGER") == "TRUE":
                cls.JobHandler.waitjob("all")

            # 断开数据库连接
            if cls.db_conn:
                cls.db_conn.close()
            cls.db_conn = None
            cls.cmdExecuteHandler.sqlConn = None

            # 断开之前保存的其他数据库连接
            for m_conn in cls.db_saved_conn.values():
                m_conn[0].close()

            # 退出应用程序
            cls.exitValue = exitValue
            raise EOFError
        else:
            if cls.testOptions.get("JOBMANAGER") == "ON":
                # 运行在控制台模式下
                if not cls.JobHandler.isAllJobClosed():
                    yield {
                        "title": None,
                        "rows": None,
                        "headers": None,
                        "columnTypes": None,
                        "status": "Please wait all background process complete."
                    }
                else:
                    # 退出应用程序
                    cls.exitValue = exitValue
                    raise EOFError
            else:
                # 退出应用程序
                cls.exitValue = exitValue
                raise EOFError

    # 加载数据库驱动
    # 标准的默认驱动程序并不需要使用这个函数，这个函数是用来覆盖标准默认驱动程序的加载信息
    @staticmethod
    def load_driver(cls, arg, **_):
        if arg == "":  # 显示当前的Driver配置
            m_Result = []
            for row in cls.db_connectionConf:
                m_Result.append([row["Database"], row["ClassName"], row["FullName"],
                                 row["JDBCURL"], row["ODBCURL"], row["JDBCProp"]])
            yield {
                "title": "Current Drivers: ",
                "rows": m_Result,
                "headers": ["Database", "ClassName", "FileName", "JDBCURL", "ODBCURL", "JDBCProp"],
                "columnTypes": None,
                "status": "Driver loaded."
            }
            return

        # 解析命令参数
        options_parameters = str(arg).split()

        # 只有一个参数，打印当前Database的Driver情况
        if len(options_parameters) == 1:
            m_DriverName = str(options_parameters[0])
            m_Result = []
            for row in cls.db_connectionConf:
                if row["Database"] == m_DriverName:
                    m_Result.append([row["Database"], row["ClassName"], row["FullName"],
                                     row["JDBCURL"], row["ODBCURL"], row["JDBCProp"]])
                    break
            yield {
                "title": "Current Drivers: ",
                "rows": m_Result,
                "headers": ["Database", "ClassName", "FileName", "JDBCURL", "ODBCURL", "JDBCProp"],
                "columnTypes": None,
                "status": "Driver loaded."
            }
            return

        # 两个参数，替换当前Database的Driver
        if len(options_parameters) == 2:
            m_DriverName = str(options_parameters[0])
            m_DriverFullName = str(options_parameters[1])
            if cls.script is None:
                m_DriverFullName = os.path.join(sys.path[0], m_DriverFullName)
            else:
                m_DriverFullName = os.path.abspath(os.path.join(os.path.dirname(cls.script), m_DriverFullName))
            if not os.path.isfile(m_DriverFullName):
                raise TestCliException("Driver not loaded. file [" + m_DriverFullName + "] does not exist!")
            found = False
            for nPos in range(0, len(cls.db_connectionConf)):
                if cls.db_connectionConf[nPos]["Database"].upper() == m_DriverName.strip().upper():
                    m_Config = cls.db_connectionConf[nPos]
                    m_Config["FullName"] = [m_DriverFullName, ]
                    found = True
                    cls.db_connectionConf[nPos] = m_Config
            if not found:
                raise TestCliException("Driver not loaded. Please config it in configfile first.")
            yield {
                "title": None,
                "rows": None,
                "headers": None,
                "columnTypes": None,
                "status": "Driver [" + m_DriverName.strip() + "] loaded."
            }
            return

        raise TestCliException("Bad command.  loaddriver [database] [new jar name]")

    # 加载数据库SQL映射
    @staticmethod
    def load_sqlmap(cls, arg, **_):
        cls.testOptions.set("TESTREWRITE", "ON")
        cls.SQLMappingHandler.Load_SQL_Mappings(cls.script, arg)
        cls.sqlmap = arg
        yield {
            "title": None,
            "rows": None,
            "headers": None,
            "columnTypes": None,
            "status": 'Mapping file loaded.'
        }

    # 连接数据库
    @staticmethod
    def connect_db(cls, connectProperties, timeout: int = -1):
        # 如果当前的连接存在，且当前连接没有被保存，则断开当前的连接
        # 如果当前连接已经被保存，这里不做任何操作
        if cls.db_conn is not None:
            if cls.db_sessionName is None:
                # 如果之前数据库连接没有被保存，则强制断开连接
                cls.db_conn.close()
                cls.db_conn = None
                cls.cmdExecuteHandler.sqlConn = None
            else:
                if cls.db_saved_conn[cls.db_sessionName][0] is None:
                    # 之前并没有保留数据库连接
                    cls.db_conn.close()
                    cls.db_conn = None
                    cls.cmdExecuteHandler.sqlConn = None

        # 一旦开始数据库连接，则当前连接会被置空，以保证连接错误的影响能够对后续的语句产生作用
        cls.db_conn = None
        cls.cmdExecuteHandler.sqlConn = None

        if cls.db_connectionConf is None:
            raise TestCliException("Please load driver first.")

        # 如果连接内容仅仅就一个mem，则连接到memory db上
        if "localService" in connectProperties:
            if connectProperties["localService"] == "mem":
                # 内置一个mem，用户调试需要
                connectProperties["service"] = "X"
                connectProperties["username"] = "sa"
                connectProperties["password"] = "sa"
                connectProperties["driver"] = "jdbc"
                connectProperties["driverSchema"] = "h2mem"
                connectProperties["driverType"] = "mem"
                connectProperties["host"] = "0.0.0.0"
                connectProperties["port"] = 0
                connectProperties["parameters"] = {}
            elif connectProperties["localService"] == "meta":
                # 如果连接内容仅仅就一个META，则连接到内置的jobmanager db
                connectProperties["service"] = "mem:testclimeta"
                connectProperties["username"] = "sa"
                connectProperties["password"] = "sa"
                connectProperties["driver"] = "jdbc"
                connectProperties["driverSchema"] = "h2tcp"
                connectProperties["driverType"] = "tcp"
                connectProperties["host"] = "0.0.0.0"
                connectProperties["port"] = 0
                connectProperties["parameters"] = {}
            else:
                raise TestCliException("Invalid localservice. MEM|METADATA only.")

        # 连接数据库
        try:
            # 如果当前未指定参数，缺省为上一次连接的参数
            if "driverSchema" not in connectProperties:
                connectProperties["driverSchema"] = cls.db_driverSchema
            if "username" not in connectProperties:
                connectProperties["username"] = cls.db_username
            if "password" not in connectProperties:
                connectProperties["password"] = cls.db_password
            if "driver" not in connectProperties:
                connectProperties["driver"] = cls.db_driver
            if "driverSchema" not in connectProperties:
                connectProperties["driverSchema"] = cls.db_driverSchema
            if "driverType" not in connectProperties:
                connectProperties["driverType"] = cls.db_driverType
            if "host" not in connectProperties:
                connectProperties["host"] = cls.db_host
            if "port" not in connectProperties:
                if cls.db_port is not None:
                    connectProperties["port"] = int(cls.db_port)
                else:
                    connectProperties["port"] = None
            if "service" not in connectProperties:
                connectProperties["service"] = cls.db_service
            if "parameters" not in connectProperties:
                connectProperties["parameters"] = cls.db_parameters

            if connectProperties["driver"] == 'jdbc':  # JDBC 连接数据库
                if connectProperties["driverSchema"] is None:
                    # 必须指定数据库驱动类型
                    raise TestCliException("Unknown database [" + str(connectProperties["driverSchema"]) + "]." +
                                           "Connect Failed. Missed configuration in conf/testcli.ini.")

                # 读取配置文件，判断随后JPype连接的时候使用具体哪一个Jar包
                jarList = []
                driverClass = ""
                jdbcURL = None
                jdbcProp = ""
                for jarConfig in cls.db_connectionConf:
                    jarList.extend(jarConfig["FullName"])
                for jarConfig in cls.db_connectionConf:
                    if jarConfig["Database"].upper() == str(connectProperties["driverSchema"]).upper():
                        driverClass = jarConfig["ClassName"]
                        jdbcURL = jarConfig["JDBCURL"]
                        jdbcProp = jarConfig["JDBCProp"]
                        break
                if jdbcURL is None:
                    # 没有找到Jar包
                    raise TestCliException("Unknown database [" + str(connectProperties["driverSchema"]) + "]." +
                                           "Connect Failed. Missed configuration in conf/testcli.ini.")

                # 如果没有指定数据库类型，则无法进行数据库连接
                if driverClass is None:
                    raise TestCliException(
                        "Missed driver config [" + connectProperties["driverSchema"] + "]. Database Connect Failed. ")

                # 替换连接字符串中的变量信息
                # 连接字符串中可以出现的变量有：  ${host} ${port} ${service} ${driverType}
                jdbcURL = jdbcURL.replace("${host}", connectProperties["host"])
                jdbcURL = jdbcURL.replace("${port}", str(connectProperties["port"]))
                if cls.db_port is None:
                    jdbcURL = jdbcURL.replace(":${port}", "")
                else:
                    jdbcURL = jdbcURL.replace("${port}", str(cls.db_port))
                jdbcURL = jdbcURL.replace("${service}", connectProperties["service"])
                jdbcURL = jdbcURL.replace("${driverType}", connectProperties["driverType"])

                # 构造连接参数
                jdbcConnProp = {}
                if "username" in connectProperties:
                    jdbcConnProp['user'] = connectProperties["username"]
                if "password" in connectProperties:
                    jdbcConnProp['password'] = connectProperties["password"]
                # 处理连接参数中的属性信息，既包括配置文件中提供的参数，也包括连接命令行中输入的
                if jdbcProp is not None:
                    for row in jdbcProp.strip().split(','):
                        props = row.split(':')
                        if len(props) == 2:
                            propName = str(props[0]).strip()
                            propValue = str(props[1]).strip()
                            jdbcConnProp[propName] = propValue
                if connectProperties["parameters"] is not None:
                    for propName, propValue in connectProperties["parameters"].items():
                        jdbcConnProp[propName] = propValue

                # 尝试数据库连接，保持一定的重试次数，一直到连接上
                retryCount = 0
                while True:
                    try:
                        cls.db_conn = jdbcconnect(
                            jclassname=driverClass,
                            url=jdbcURL,
                            driverArgs=jdbcConnProp,
                            jars=jarList,
                            timeoutLimit=timeout)
                        break
                    except SQLCliJDBCTimeOutException as je:
                        raise je
                    except SQLCliJDBCException as je:
                        if "TESTCLI_DEBUG" in os.environ:
                            print('traceback.print_exc():\n%s' % traceback.print_exc())
                            print('traceback.format_exc():\n%s' % traceback.format_exc())
                        retryCount = retryCount + 1
                        if retryCount >= int(cls.testOptions.get("CONN_RETRY_TIMES")):
                            raise je
                        else:
                            time.sleep(2)
                            continue

                # 将当前DB的连接字符串备份到变量中， 便于SET命令展示
                cls.testOptions.set("CONNURL", str(jdbcURL))
                cls.testOptions.set("CONNSCHEMA", str(connectProperties["username"]))

                # 成功连接后，保留当前连接的所有信息，以便下一次连接
                cls.db_url = jdbcURL
                cls.db_username = connectProperties["username"]
                cls.db_password = connectProperties["password"]
                cls.db_driver = connectProperties["driver"]
                cls.db_driverSchema = connectProperties["driverSchema"]
                cls.db_driverType = connectProperties["driverType"]
                cls.db_host = connectProperties["host"]
                cls.db_port = connectProperties["port"]
                cls.db_service = connectProperties["service"]
                cls.db_parameters = connectProperties["parameters"]

                # 保存连接句柄
                cls.cmdExecuteHandler.sqlConn = cls.db_conn
            else:
                raise TestCliException("Current driver [" + str(connectProperties["driver"]) + "] is not supported.")
        except TestCliException as se:  # Connecting to a database fail.
            raise se
        except Exception as e:  # Connecting to a database fail.
            if "TESTCLI_DEBUG" in os.environ:
                print('traceback.print_exc():\n%s' % traceback.print_exc())
                print('traceback.format_exc():\n%s' % traceback.format_exc())
                print("db_sessionName = [" + str(cls.db_sessionName) + "]")
                print("db_user = [" + connectProperties["username"] + "]")
                print("db_pass = [" + connectProperties["password"] + "]")
                print("db_driver = [" + connectProperties["driver"] + "]")
                print("db_driverSchema = [" + connectProperties["driverSchema"] + "]")
                print("db_driverType = [" + connectProperties["driverType"] + "]")
                print("db_host = [" + connectProperties["host"] + "]")
                print("db_port = [" + str(connectProperties["port"]) + "]")
                print("db_service = [" + connectProperties["service"] + "]")
                print("db_parameters = [" + str(connectProperties["parameters"]) + "]")
                print("db_url = [" + str(cls.db_url) + "]")
                print("jar_file = [" + str(cls.db_connectionConf) + "]")
            if str(e).find("SQLInvalidAuthorizationSpecException") != -1:
                raise TestCliException(str(jpype.java.sql.SQLInvalidAuthorizationSpecException(e).getCause()))
            else:
                raise TestCliException(str(e))
        yield {
            "type": "result",
            "title": None,
            "rows": None,
            "headers": None,
            "columnTypes": None,
            "status": 'Database connected.'
        }

    # 断开数据库连接
    @staticmethod
    def disconnect_db(cls):
        if cls.db_conn:
            cls.db_conn.close()
        cls.db_conn = None
        cls.cmdExecuteHandler.sqlConn = None
        yield {
            "type": "result",
            "title": None,
            "rows": None,
            "headers": None,
            "columnTypes": None,
            "status": 'Database disconnected.'
        }

    # 执行主机的操作命令
    @staticmethod
    def host(cls, arg, **_):
        if arg is None or len(str(arg)) == 0:
            raise TestCliException(
                "Missing OS command\n." + "host xxx")
        Commands = str(arg)

        if 'win32' in str(sys.platform).lower():
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags = subprocess.CREATE_NEW_CONSOLE | subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            p = subprocess.Popen(Commands,
                                 shell=True,
                                 startupinfo=startupinfo,
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        else:
            p = subprocess.Popen(Commands,
                                 shell=True,
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        try:
            (stdoutdata, stderrdata) = p.communicate()
            summaryStatus = str(stdoutdata.decode(encoding=cls.testOptions.get("RESULT_ENCODING")))
            if len(str(stderrdata.decode(encoding=cls.testOptions.get("RESULT_ENCODING")))) != 0:
                summaryStatus = summaryStatus + "\n" + \
                                str(stderrdata.decode(encoding=cls.testOptions.get("RESULT_ENCODING")))
            yield {
                "title": None,
                "rows": None,
                "headers": None,
                "columnTypes": None,
                "status": summaryStatus
            }
        except UnicodeDecodeError:
            raise TestCliException("The character set [" + cls.testOptions.get("RESULT_ENCODING") + "]" +
                                   " does not match the terminal character set, " +
                                   "so the terminal information cannot be output correctly.")

    # 执行Python脚本
    @staticmethod
    def execute_embeddScript(cls, block: str):
        # 定义全局的环境信息，保证在多次执行嵌入式脚本的时候，环境信息能够被保留
        global globalEmbeddScriptScope
        global localEmbeddScriptScope

        sessionContext = {
            "dbConn": cls.db_conn.jconn if cls.db_conn is not None else None,
            "type": "result",
            "title": None,
            "rows": None,
            "headers": None,
            "columnTypes": None,
            "status": None
        }
        localEmbeddScriptScope["SessionContext"] = sessionContext
        exec(block, globalEmbeddScriptScope, localEmbeddScriptScope)

        yield {
            "type": sessionContext["type"],
            "title": sessionContext["title"],
            "rows": sessionContext["rows"],
            "headers": sessionContext["headers"],
            "columnTypes": sessionContext["columnTypes"],
            "status": sessionContext["status"],
        }

    @staticmethod
    def assert_expression(cls, expression: str):
        # 定义全局的环境信息，保证在多次执行嵌入式脚本的时候，环境信息能够被保留
        global globalEmbeddScriptScope
        global localEmbeddScriptScope

        sessionContext = {
            "dbConn": cls.db_conn.jconn if cls.db_conn is not None else None,
            "type": "result",
            "title": None,
            "rows": None,
            "headers": None,
            "columnTypes": None,
            "status": None
        }
        localEmbeddScriptScope["SessionContext"] = sessionContext
        ret = eval(expression, globalEmbeddScriptScope, localEmbeddScriptScope)
        if type(ret) == bool:
            yield {
                "type": "result",
                "title": "",
                "rows": "",
                "headers": "",
                "columnTypes": "",
                "status": "Assert " + ("successful." if ret else "fail.")
            }

    # 数据库会话管理
    @staticmethod
    def session_manage(cls, action: str, sessionName: str = None):
        # Session_Context:
        #   0:   Connection
        #   1:   UserName
        #   2:   Password
        #   3:   URL
        if action.strip().lower() == 'show':
            m_Result = []
            for m_Session_Name, m_Connection in cls.db_saved_conn.items():
                if m_Connection[0] is None:
                    m_Result.append(['None', str(m_Session_Name), str(m_Connection[1]), '******', str(m_Connection[3])])
                else:
                    m_Result.append(['Connection', str(m_Session_Name), str(m_Connection[1]),
                                     '******', str(m_Connection[3])])
            if cls.db_conn is not None:
                m_Result.append(['Current', str(cls.db_sessionName), str(cls.db_username), '******', str(cls.db_url)])
            if len(m_Result) == 0:
                yield {
                    "type": "result",
                    "title": None,
                    "rows": None,
                    "headers": None,
                    "columnTypes": None,
                    "status": "No saved sesssions."
                }
            else:
                yield {
                    "type": "result",
                    "title": "Saved Sessions:",
                    "rows": m_Result,
                    "headers": ["Session", "Sesssion Name", "User Name", "Password", "URL"],
                    "columnTypes": None,
                    "status": "Total " + str(len(m_Result)) + " saved sesssions."
                }
            return

        if action.strip().lower() == 'release':
            if cls.db_conn is None:
                raise TestCliException(
                    "You don't have a saved session.")
            del cls.db_saved_conn[sessionName]
            cls.db_sessionName = None
        elif action.strip().lower() == 'save':
            if cls.db_conn is None:
                raise TestCliException(
                    "Please connect session first before save.")
            cls.db_saved_conn[sessionName] = [cls.db_conn, cls.db_username, cls.db_password, cls.db_url]
            cls.db_sessionName = sessionName
        elif action.strip().lower() == 'saveurl':
            if cls.db_conn is None:
                raise TestCliException(
                    "Please connect session first before save.")
            cls.db_saved_conn[sessionName] = [None, cls.db_username, cls.db_password, cls.db_url]
            cls.db_sessionName = sessionName
        elif action.strip().lower() == 'restore':
            if sessionName in cls.db_saved_conn:
                cls.db_username = cls.db_saved_conn[sessionName][1]
                cls.db_password = cls.db_saved_conn[sessionName][2]
                cls.db_url = cls.db_saved_conn[sessionName][3]
                if cls.db_saved_conn[sessionName][0] is None:
                    result = cls.connect_db(cls.db_username + "/" + cls.db_password + "@" + cls.db_url)
                    for title, cur, headers, columnTypes, status in result:
                        yield {
                            "title": title,
                            "rows": cur,
                            "headers": headers,
                            "columnTypes": columnTypes,
                            "status": status
                        }
                else:
                    cls.db_conn = cls.db_saved_conn[sessionName][0]
                    cls.cmdExecuteHandler.sqlConn = cls.db_conn
                    cls.db_sessionName = sessionName
            else:
                raise TestCliException(
                    "Session [" + sessionName + "] does not exist. Please save it first.")
        else:
            raise TestCliException(
                "Wrong argument : " + "Session save/restore [session name]")
        if action.strip().lower() == 'save':
            yield {
                "type": "result",
                "title": None,
                "rows": None,
                "headers": None,
                "columnTypes": None,
                "status": "Session saved Successful."
            }
        if action.strip().lower() == 'release':
            yield {
                "type": "result",
                "title": None,
                "rows": None,
                "headers": None,
                "columnTypes": None,
                "status": "Session release Successful."
            }
        if action.strip().lower() == 'restore':
            cls.testOptions.set("CONNURL", cls.db_url)
            yield {
                "type": "result",
                "title": None,
                "rows": None,
                "headers": None,
                "columnTypes": None,
                "status": "Session restored Successful."
            }

    # 休息一段时间
    @staticmethod
    def sleep(cls, sleepTime: int):
        sleepTimeOut = -1

        nameSpace = cls.testOptions.get("NAMESPACE")
        scriptTimeOut = int(cls.testOptions.get("SCRIPT_TIMEOUT"))
        if nameSpace == "SQL":
            sqlTimeOut = int(cls.testOptions.get("SQL_TIMEOUT"))
            if scriptTimeOut != -1:
                if scriptTimeOut < sqlTimeOut:
                    sleepTimeOut = scriptTimeOut
            else:
                if sqlTimeOut != -1:
                    sleepTimeOut = sqlTimeOut
        if nameSpace == "API":
            apiTimeOut = int(cls.testOptions.get("API_TIMEOUT"))
            if scriptTimeOut != -1:
                if scriptTimeOut < apiTimeOut:
                    sleepTimeOut = scriptTimeOut
            else:
                if apiTimeOut != -1:
                    sleepTimeOut = apiTimeOut

        if sleepTime <= 0:
            message = "Parameter must be a valid number, sleep [seconds]."
            return [{
                "type": "result",
                "title": None,
                "rows": None,
                "headers": None,
                "columnTypes": None,
                "status": message
            }]
        if sleepTimeOut != -1 and sleepTimeOut < sleepTime:
            # 有超时限制，最多休息到超时的时间
            time.sleep(sleepTimeOut)
            raise SQLCliJDBCTimeOutException("TimeOut")
        else:
            time.sleep(sleepTime)
        return [{
            "type": "result",
            "title": None,
            "rows": None,
            "headers": None,
            "columnTypes": None,
            "status": None
        }]

    # 从文件中执行SQL
    @staticmethod
    def execute_from_file(cls, scriptFileList, loopTimes=1):
        for nPos in range(0, loopTimes):
            for scriptFile in scriptFileList:
                # 将scriptFile根据平台进行转义
                try:
                    if str(scriptFile).startswith("'"):
                        scriptFile = scriptFile[1:]
                    if str(scriptFile).endswith("'"):
                        scriptFile = scriptFile[:-1]
                    with open(os.path.expanduser(scriptFile), encoding=cls.testOptions.get("SCRIPT_ENCODING")) as f:
                        query = f.read()

                    # 空文件直接返回
                    if len(query) == 0:
                        continue

                    # 处理脚本文件头数据, 文件开头的0xFEFF,codecs.BOM_UTF8忽略不看
                    if ord(query[0]) == 0xFEFF:
                        # 去掉脚本文件可能包含的UTF-BOM
                        query = query[1:]
                    if query[:3] == codecs.BOM_UTF8:
                        # 去掉脚本文件可能包含的UTF-BOM
                        query = query[3:]

                    # Scenario, Transaction等Hint信息不会带入到下一个脚本文件中
                    cls.cmdExecuteHandler.scenario = ''
                    cls.cmdExecuteHandler.transaction = ''
                    cls.cmdExecuteHandler.setStartTime(time.time())

                    # 这里需要把command按照namespace分离，即不同的namespace分开执行
                    # 避免切换namespace后，解析导致的问题
                    # 其中：
                    #   __use__ namespace 为一段
                    #   两个 __use__ namespace之间为一段
                    commandList = []
                    lastCommand = None
                    lastNameSpace = cls.nameSpace
                    for commandLine in query.split("\n"):
                        match_obj = re.match(r"(\s+)?__USE__(\s+)NAMESPACE(\s+)(.*)$",
                                             commandLine, re.IGNORECASE | re.DOTALL)
                        if match_obj:
                            newNameSpace = match_obj.group(4).strip().upper()
                            if lastCommand is not None:
                                commandList.append({"nameSpace": lastNameSpace, "script": lastCommand})
                                lastCommand = None
                            commandList.append({"nameSpace": "GENERAL", "script": commandLine})
                            lastNameSpace = newNameSpace
                            lastNameSpace = lastNameSpace.strip().upper().strip(';')
                            continue
                        else:
                            if lastCommand is None:
                                lastCommand = commandLine
                            else:
                                lastCommand = lastCommand + "\n" + commandLine
                    if lastCommand is not None:
                        commandList.append({"nameSpace": lastNameSpace, "script": lastCommand})

                    # 分段执行执行的语句
                    for command in commandList:
                        for executeResult in \
                                cls.cmdExecuteHandler.runStatement(
                                    statement=command["script"],
                                    commandScriptFile=os.path.expanduser(scriptFile),
                                    nameSpace=command["nameSpace"]
                                ):
                            yield executeResult
                except IOError as e:
                    yield {
                        "type": "result",
                        "title": None,
                        "rows": None,
                        "headers": None,
                        "columnTypes": None,
                        "status": "Execute script [" + str(os.path.abspath(scriptFile)) + "] failed. " + repr(e)
                    }

    # 将当前及随后的输出打印到指定的文件中
    @staticmethod
    def spool(cls, fileName: str):
        if fileName.strip().upper() == 'OFF':
            # close spool file
            if len(cls.SpoolFileHandler) == 0:
                yield {
                    "type": "result",
                    "title": None,
                    "rows": None,
                    "headers": None,
                    "columnTypes": None,
                    "status": "not spooling currently"
                }
                return
            else:
                cls.SpoolFileHandler[-1].close()
                cls.SpoolFileHandler.pop()
                yield {
                    "type": "result",
                    "title": None,
                    "rows": None,
                    "headers": None,
                    "columnTypes": None,
                    "status": None
                }
                return

        if cls.logfilename is not None:
            # 如果当前主程序启用了日志，则spool日志的默认输出目录为logfile的目录
            spoolFileName = os.path.join(os.path.dirname(cls.logfilename), fileName.strip())
        else:
            # 如果主程序没有启用日志，则输出为当前目录
            spoolFileName = fileName.strip()

        # 如果当前有打开的Spool文件，关闭它
        try:
            cls.SpoolFileHandler.append(open(spoolFileName, "w", encoding=cls.testOptions.get("RESULT_ENCODING")))
        except IOError as e:
            raise TestCliException("SQLCLI-00000: IO Exception " + repr(e))
        yield {
            "type": "result",
            "title": None,
            "rows": None,
            "headers": None,
            "columnTypes": None,
            "status": None
        }
        return

    # 将当前及随后的屏幕输入存放到脚本文件中
    @staticmethod
    def echo_input(cls, fileName: str, block: str):
        try:
            f = open(fileName, "w", encoding=cls.testOptions.get("RESULT_ENCODING"))
            f.write(block)
            f.close()
            return [{
                "type": "result",
                "title": None,
                "rows": None,
                "headers": None,
                "columnTypes": None,
                "status": "File [" + str(fileName) + "] generated successful."
            }]
        except IOError as ie:
            return [{
                "type": "result",
                "title": None,
                "rows": None,
                "headers": None,
                "columnTypes": None,
                "status": "File [" + str(fileName) + "] generated failed. " + str(ie)
            }]

    # 设置一些选项
    @staticmethod
    def set_options(cls, options):
        if "optionName" in options:
            optionName = options["optionName"]
        else:
            optionName = None
        if "optionValue" in options:
            optionValue = options["optionValue"]
        else:
            optionValue = ""

        if optionName is None:
            # SET如果没有参数，则显示所有的选项出来
            result = []
            for row in cls.testOptions.getOptionList():
                if not row["Hidden"]:
                    result.append([row["Name"], row["Value"], row["Comments"]])
            yield {
                "type": "result",
                "title": "Current Options: ",
                "rows": result,
                "headers": ["Name", "Value", "Comments"],
                "columnTypes": None,
                "status": None
            }
            return

        # 处理DEBUG选项
        if optionName.upper() == "DEBUG":
            if optionValue.upper() == 'ON':
                os.environ['TESTCLI_DEBUG'] = "1"
            elif optionValue.upper() == 'OFF':
                if 'TESTCLI_DEBUG' in os.environ:
                    del os.environ['TESTCLI_DEBUG']
            else:
                raise TestCliException("SQLCLI-00000: "
                                       "Unknown option [" + str(optionValue) + "]. ON/OFF only.")
            return [{
                "type": "result",
                "title": None,
                "rows": None,
                "headers": None,
                "columnTypes": None,
                "status": None
            }, ]

        # 处理AUTOCOMMIT选项
        if optionName.upper() == "AUTOCOMMIT":
            if cls.db_conn is None:
                raise TestCliException("Not connected.")
            if optionValue.upper() == 'FALSE':
                cls.db_conn.setAutoCommit(False)
            elif optionValue.upper() == 'TRUE':
                cls.db_conn.setAutoCommit(True)
            else:
                raise TestCliException("SQLCLI-00000: "
                                       "Unknown option [" + str(optionValue) + "]. True/False only.")
            return [{
                "type": "result",
                "title": None,
                "rows": None,
                "headers": None,
                "columnTypes": None,
                "status": None
            }, ]

        # 处理JOBMANAGER选项
        if optionName.upper() == "JOBMANAGER":
            if optionValue.upper() == 'ON' and cls.testOptions.get("JOBMANAGER").upper() == "OFF":
                # 本次打开，之前为OFF
                # 连接到Meta服务上
                cls.MetaHandler.StartAsServer(p_ServerParameter=None)
                # 标记JOB队列管理使用的数据库连接
                if cls.MetaHandler.dbConn is not None:
                    os.environ["TESTCLI_JOBMANAGERURL"] = cls.MetaHandler.MetaURL
                    cls.JobHandler.setMetaConn(cls.MetaHandler.dbConn)
                    cls.TransactionHandler.setMetaConn(cls.MetaHandler.dbConn)
                    cls.testOptions.set("JOBMANAGER", "ON")
                    cls.testOptions.set("JOBMANAGER_METAURL", cls.MetaHandler.MetaURL)
            elif optionValue.upper() == 'OFF' and cls.testOptions.get("JOBMANAGER").upper() == "ON":
                del os.environ["TESTCLI_JOBMANAGERURL"]
                cls.testOptions.set("JOBMANAGER", "OFF")
                cls.testOptions.set("JOBMANAGER_METAURL", '')
                cls.MetaHandler.ShutdownServer()
            else:
                raise TestCliException("SQLCLI-00000: "
                                       "Unknown option [" + str(optionValue) + "] for JOBMANAGER. ON/OFF only.")
            return [{
                "type": "result",
                "title": None,
                "rows": None,
                "headers": None,
                "columnTypes": None,
                "status": None
            }, ]

        # 对于子进程，连接到JOB管理服务
        if optionName.upper() == "JOBMANAGER_METAURL":
            if cls.testOptions.get("JOBMANAGER") == "ON":
                raise TestCliException("SQLCLI-00000: "
                                       "You can't act as worker rule while option JOBMANAGER is ON")
            jobManagerURL = optionValue
            if len(jobManagerURL) == 0:
                # 退出Meta的连接
                cls.MetaHandler.DisConnectServer()
                cls.JobHandler.setMetaConn(None)
                cls.TransactionHandler.setMetaConn(None)
                cls.testOptions.set("JOBMANAGER_METAURL", "")
            else:
                # 对于被主进程调用的进程，则不需要考虑, 连接到主进程的Meta服务
                cls.MetaHandler.ConnectServer(jobManagerURL)
                cls.JobHandler.setMetaConn(cls.MetaHandler.db_conn)
                cls.TransactionHandler.setMetaConn(cls.MetaHandler.db_conn)
                cls.testOptions.set("JOBMANAGER_METAURL", jobManagerURL)
            return [{
                "type": "result",
                "title": None,
                "rows": None,
                "headers": None,
                "columnTypes": None,
                "status": None
            }, ]

        # 如果特殊的选项，有可能时用户自己定义的变量
        if optionName.startswith('@'):
            cls.testOptions.set(optionName[1], optionValue)
            return [{
                "type": "result",
                "title": None,
                "rows": None,
                "headers": None,
                "columnTypes": None,
                "status": None
            }, ]

        # 查看是否属于定义的选项
        if cls.testOptions.get(optionName.upper()) is not None:
            cls.testOptions.set(optionName.upper(), optionValue)
            return [{
                "type": "result",
                "title": None,
                "rows": None,
                "headers": None,
                "columnTypes": None,
                "status": None
            }, ]
        else:
            # 不认识的配置选项按照SQL命令处理
            raise TestCliException("SQLCLI-00000: "
                                   "Unknown option [" + str(optionValue) + "] .")

    # 切换程序运行空间
    @staticmethod
    def set_nameSpace(cls, nameSpace: str):
        cls.testOptions.set("NAMESPACE", nameSpace)
        yield {
            "type": "result",
            "title": None,
            "rows": None,
            "headers": None,
            "columnTypes": None,
            "status": "Current NameSpace: " + str(nameSpace) + "."
        }

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
        # 判断传入的测试语句， 如果没有传递，则表示控制台程序，需要用户逐行输入语句
        if text is None:
            full_text = None
            while True:
                # 用户一行一行的输入测试语句，一直到输入发生了截止符
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
                    self.echo("SQLCli Can't work without valid terminal. "
                              "Use \"--execute\" in case you need run script", err=True, fg="red")
                    return False

                # 拼接语句
                if full_text is None:
                    full_text = text
                else:
                    full_text = full_text + '\n' + text
                if self.testOptions.get('NAMESPACE') == "SQL":
                    # 判断SQL语句是否已经结束
                    (ret_bCommandCompleted, ret_CommandSplitResults,
                     ret_CommandSplitResultsWithComments, ret_CommandHints,
                     ret_errorCode, ret_errorMsg) = SQLAnalyze(full_text)
                    # print("SQL_fulltext:" + full_text)
                    # print("SQL_bCommandCompleted:" + str(ret_bCommandCompleted))
                    # print("SQL_CommandSplitResults:" + str(ret_CommandSplitResults))
                    # print("SQL_CommandSplitResultsWithComments:" + str(ret_CommandSplitResultsWithComments))
                    # print("SQL_CommandHints:" + str(ret_CommandHints))
                    # print("SQL_errorCode:" + str(ret_errorCode))
                    # print("SQL_errorMsg:" + str(ret_errorMsg))
                    if ret_bCommandCompleted:
                        # 语句已经结束
                        break
                elif self.testOptions.get('NAMESPACE') == "API":
                    # 判断API语句是否已经结束
                    (ret_bCommandCompleted, ret_CommandSplitResults,
                     ret_CommandSplitResultsWithComments, ret_CommandHints) = \
                        APIAnalyze(full_text)
                    # print("ret_bCommandCompleted:" + str(ret_bCommandCompleted))
                    # print("ret_CommandSplitResults:" + str(ret_CommandSplitResults))
                    # print("ret_CommandSplitResultsWithComments:" + str(ret_CommandSplitResultsWithComments))
                    # print("ret_CommandHints:" + str(ret_CommandHints))
                    if ret_bCommandCompleted:
                        # 语句已经结束
                        break
                else:
                    raise TestCliException("不支持的NAMESPACE。目前仅支持SQL|API")

            # 这是一个内部异常情况，在调试完成后会删除该语句
            if len(ret_CommandSplitResults) > 1:
                raise TestCliException("命令行模式下，每行只会返回一个校验结果。 INTERNAL-ERROR")
            
            # 并不存在实际的解析结果，应该把全部注释内容记录，并依次往下传递，直到有真正意义的语句
            if len(ret_CommandSplitResults) == 0:
                if self.lastComment is not None:
                    self.lastComment = self.lastComment + "\n" + "\n".join(text)
                else:
                    self.lastComment = "\n".join(text)
                return True
            else:
                # 如果文本是空行，直接跳过
                if not text.strip():
                    return True

                # 记录需要执行的SQL，包含之前保留的注释部分，传递给执行程序
                if self.lastComment is None:
                    text = full_text
                else:
                    text = self.lastComment + '\n' + full_text
                    self.lastComment = None

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
                        self.Log_Statistics(p_result)
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
                if result["type"] == "statistics":
                    if self.testOptions.get('TIMING').upper() == 'ON':
                        self.echo('Running time elapsed: %9.2f seconds' % result["elapsed"])
                    if self.testOptions.get('TIME').upper() == 'ON':
                        self.echo('Current clock time  :' + strftime("%Y-%m-%d %H:%M:%S", localtime()))
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
            if self.testOptions.get("WHENEVER_SQLERROR").upper() == "EXIT":
                raise e
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
                if not self.DoCommand("connect " + str(self.logon)):
                    raise EOFError

            # 如果传递的参数中有脚本文件，先执行脚本文件, 执行完成后自动退出
            try:
                self.DoCommand('start ' + self.commandScript)
            except TestCliException:
                raise EOFError
            self.DoCommand('exit')
        except (TestCliException, EOFError):
            if self.testOptions.get("JOBMANAGER") == "ON":
                # 如果还有活动的事务，标记事务为失败信息
                for m_Transaction in self.TransactionHandler.getAllTransactions():
                    self.TransactionHandler.TransactionFail(m_Transaction.Transaction_Name)
            # TestCliException只有在被设置了WHENEVER_SQLERROR为EXIT的时候，才会被捕获到

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

    def Log_Statistics(self, p_SQLResult):
        # 开始时间         StartedTime
        # 消耗时间         elapsed
        # SQL的前20个字母  SQLPrefix
        # 运行状态         SQLStatus
        # 错误日志         ErrorMessage
        # 线程名称         thread_name

        # 如果没有打开性能日志记录文件，直接跳过
        if self.SQLPerfFile is None:
            return

        # 初始化文件加锁机制
        if self.PerfFileLocker is None:
            self.PerfFileLocker = Lock()

        # 多进程，多线程写入，考虑锁冲突
        try:
            self.PerfFileLocker.acquire()
            if not os.path.exists(self.SQLPerfFile):
                # 如果文件不存在，创建文件，并写入文件头信息
                self.SQLPerfFileHandle = open(self.SQLPerfFile, "a", encoding="utf-8")
                self.SQLPerfFileHandle.write("Script\tStarted\telapsed\tRawCommand\tCommand\t"
                                             "CommandStatus\tErrorMessage\tWorkerName\t"
                                             "Suite\tCase\tScenario\tTransaction\n")
                self.SQLPerfFileHandle.close()

            # 对于多线程运行，这里的thread_name格式为JOB_NAME#副本数-完成次数
            # 对于单线程运行，这里的thread_name格式为固定的MAIN
            m_ThreadName = str(p_SQLResult["thread_name"])

            # 打开Perf文件
            self.SQLPerfFileHandle = open(self.SQLPerfFile, "a", encoding="utf-8")
            # 写入内容信息
            if self.commandScript is None:
                m_SQL_Script = "Console"
            else:
                m_SQL_Script = str(os.path.basename(self.commandScript))
            self.SQLPerfFileHandle.write(
                m_SQL_Script + "\t" +
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(p_SQLResult["startedTime"])) + "\t" +
                "%8.2f" % p_SQLResult["elapsed"] + "\t" +
                str(p_SQLResult["rawCommand"]).replace("\n", " ").replace("\t", "    ") + "\t" +
                str(p_SQLResult["command"]).replace("\n", " ").replace("\t", "    ") + "\t" +
                str(p_SQLResult["commandStatus"]) + "\t" +
                str(p_SQLResult["errorMessage"]).replace("\n", " ").replace("\t", "    ") + "\t" +
                str(m_ThreadName) + "\t" +
                str(self.suitename) + "\t" +
                str(self.casename) + "\t" +
                str(p_SQLResult["scenario"]) + "\t" +
                str(p_SQLResult["transaction"]) +
                "\n"
            )
            self.SQLPerfFileHandle.flush()
            self.SQLPerfFileHandle.close()
        except Exception as ex:
            print("Internal error:: perf file write not complete. " + repr(ex))
        finally:
            self.PerfFileLocker.release()
