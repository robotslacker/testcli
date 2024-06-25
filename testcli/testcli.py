# -*- coding: utf-8 -*-
import json
import os
import sys
import traceback
import re
import time
import sqlite3
import setproctitle
import click
import configparser
import unicodedata
import itertools
import urllib3
from time import strftime, localtime
from xml.sax import saxutils

from prompt_toolkit.history import FileHistory
from prompt_toolkit.shortcuts import PromptSession
from prompt_toolkit.formatted_text import HTML

from .cmdexecute import CmdExecute
from .cmdmapping import CmdMapping
from .testcliexception import TestCliException
from .testclijobmanager import TestCliMeta
from .testclijobmanager import JOBManager
from .testoption import TestOptions
from .globalvar import lastCommandResult
from .__init__ import __version__
from .sqlparse import SQLAnalyze
from .apiparse import APIAnalyze
from .commands.compare import POSIXCompare
from .commands.compare import compareMaskLines
from .commands.compare import compareSkipLines
from .commands.compare import compareOption
from .commands.compare import compareDefaultOption
from .commands.monitor import stopMonitorManager

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

    logfile = None        # 程序输出日志文件
    logger = None         # 程序的第三方输出日志，用于第三方调用
    HeadlessMode = False  # 没有显示输出，即不需要回显，用于子进程的显示

    exitValue = 0  # 程序退出状态位

    def __init__(
            self,
            logon=None,                             # 默认登录信息，None表示不需要
            logfilename=None,                       # 程序输出文件名，None表示不需要
            script=None,                            # 脚本文件名，None表示命令行模式
            referenceFile=None,                     # 脚本运行参考日志文件，用来校验数据是否正确
            commandMap=None,                        # 脚本变量映射文件名，None表示不存在
            nologo=False,                           # 是否不打印登陆时的Logo信息，True的时候不打印
            breakWithError=False,                   # 遇到命令行错误，是否中断脚本后续执行，立刻退出
            breakErrorCode=255,                     # 遇到命令行错误时候的退出代码
            xlog=None,                              # 扩展日志信息文件输出名，None表示不需要
            xlogoverwrite=False,                    # 是否覆盖之前的扩展日志
            Console=sys.stdout,                     # 控制台输出，默认为sys.stdout,即标准输出
            headlessMode=False,                     # 是否为无终端模式，无终端模式下，任何屏幕信息都不会被输出
            workerName='MAIN',                      # 程序别名，可用来区分不同的应用程序,
            logger=None,                            # 程序输出日志句柄
            clientCharset='UTF-8',                  # 客户端字符集，在读取SQL文件时，采纳这个字符集，默认为UTF-8
            resultCharset='UTF-8',                  # 输出字符集，在打印输出文件，日志的时候均采用这个字符集
            profile=None,                           # 程序初始化执行脚本
            scripttimeout=-1,                       # 程序的脚本超时时间，默认为不限制
            suitename=None,                         # 程序所在的SuiteName
            casename=None,                          # 程序所在的CaseName
            namespace=None,                         # 程序的默认命名空间
            testRunId=0,                            # 程序每次运行的唯一ID（便于统计，可以省略)
    ):
        self.version = __version__                      # 当前程序版本

        self.db_saved_conn = {}                         # 数据库Session对象，可能存在多个Session，并存在切换需要
        self.api_saved_conn = {}                        # HTTP请求Session对象，可能存在多个Session，并存在切换需要

        self.plugin = {}                                # 程序的外挂插件
        self.cmdMappingHandler = CmdMapping()           # 函数句柄，处理SQLMapping信息
        self.cmdExecuteHandler = CmdExecute()           # 函数句柄，具体来执行语句

        self.testOptions = TestOptions()                # 程序运行中各种参数
        self.JobHandler = JOBManager()                  # 并发任务管理器
        self.MetaHandler = TestCliMeta()                # TestCli元数据
        self.SpoolFileHandler = []                      # Spool文件句柄, 是一个数组，可能发生嵌套
        self.EchoFileHandler = None                     # 当前回显文件句柄
        self.appOptions = None                          # 应用程序的配置参数
        self.Encoding = None                            # 应用程序的Encoding信息
        self.prompt_app = None                          # PromptKit控制台
        self.ProcessPwd = os.getcwd()                   # 进程所在的目录
        self.xlogFile = None                            # xlog文件名
        self.xlogFileFullPath = None                    # xlog文件名-绝对路径
        self.xlogFileHandle = None                      # xlog文件句柄
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

        # 参考日志信息
        self.referenceFile = referenceFile              # 参考日志名称
        self.referenceContent = []                      # 参考日志文本信息
        self.referenceScenario = {}                     # 参考日志解析信息

        self.logfileContent = []                        # 程序执行日志文本信息
        self.logfileScenario = {}                       # 执行日志解析信息

        # 测试的运行ID，用来完成多次运行时候的比较
        self.testRunId = testRunId

        # 参考日志比对句柄
        self.referenceCompareHandler = POSIXCompare()

        # 当前Http请求的信息
        self.httpSessionName = "DEFAULT"                # 当前Http会话的名称

        # HTTP请求Session对象，可能存在多个Session，并存在切换需要
        self.api_saved_conn = {
            self.httpSessionName: {"https_verify": None, "http_proxy": None}
        }
        # 禁用urllib3的各种告警信息
        urllib3.disable_warnings()

        # 如果没有标准输出和标准错误输出，则不输出。不报错
        self.__sysstdout_origin = None
        if sys.stdout.closed or not sys.stdout.isatty():
            self.__sysstdout_origin = sys.stdout
            sys.stdout = open(os.devnull, mode="w")
        self.__sysstderr_origin = None
        if sys.stderr.closed or not sys.stderr.isatty():
            self.__sysstderr_origin = sys.stderr
            sys.stderr = open(os.devnull, mode="w")

        # 多语言集处理，设置字符集
        if clientCharset is not None:                   # 客户端脚本字符集
            self.testOptions.set("SCRIPT_ENCODING", clientCharset)
            self.testOptions.set("RESULT_ENCODING", resultCharset)
        if resultCharset is not None:                   # 客户端结果字符集
            self.testOptions.set("RESULT_ENCODING", resultCharset)

        # 设置Compare的默认算法
        compareDefaultOption["algorithm"] = self.testOptions.get("COMPARE_DEFAULT_METHOD")

        # 当前进程名称. 如果有参数传递，以参数为准.  如果没有，用MAIN加进程ID来标记
        if workerName == "MAIN":
            self.workerName = "MAIN-" + str(os.getpid())
        else:
            self.workerName = workerName
        self.profile = []                               # 程序的初始化脚本文件
        self.lastComment = None                         # 如果当前SQL之前的内容完全是注释，则注释带到这里

        # 传递各种参数
        self.commandScript = script                     # 初始化运行的脚本名称，即runCli的脚本名称
        self.executeScript = script                     # 当前正在执行的脚本名称。 可能会由于start命令而发生切换
        self.commandMap = commandMap
        self.nologo = nologo
        self.logon = logon
        self.logfilename = logfilename
        self.Console = Console
        self.headlessMode = headlessMode
        self.xlogFile = xlog
        self.xlogOverwrite = xlogoverwrite
        if headlessMode:
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
        self.JobHandler.setProcessContextInfo("processPwd", self.ProcessPwd)
        self.JobHandler.setProcessContextInfo("xlog", xlog)
        self.JobHandler.setProcessContextInfo("logfilename", self.logfilename)
        self.JobHandler.setProcessContextInfo("script", self.commandScript)

        # 设置其他的变量
        self.cmdExecuteHandler.cliHandler = self
        self.cmdExecuteHandler.script = script
        self.cmdExecuteHandler.testOptions = self.testOptions
        self.cmdExecuteHandler.workerName = self.workerName
        self.cmdExecuteHandler.cmdMappingHandler = self.cmdMappingHandler

        # 设置WHENEVER_ERROR
        if breakWithError:
            self.testOptions.set("WHENEVER_ERROR", "EXIT " + str(self.breakErrorCode))
        else:
            self.testOptions.set("WHENEVER_ERROR", "CONTINUE")

        # 加载程序的配置文件
        self.appOptions = None
        if "TESTCLI_CONF" in os.environ:
            # 首先尝试读取TESTCLI_CONF中的信息
            confFilename = str(os.environ["TESTCLI_CONF"]).strip()
            if os.path.exists(confFilename):
                self.appOptions = configparser.ConfigParser()
                self.appOptions.read(confFilename)
            else:
                raise TestCliException("Can not open config file [" + confFilename + "]")
        if self.appOptions is None and "TESTCLI_HOME" in os.environ:
            # 其次尝试读取TESTCLI_HOME/conf/testcli.ini中的信息，如果有，以TESTCLI_HOME/conf/testcli.ini信息为准
            confFilename = os.path.join(str(os.environ["TESTCLI_HOME"]).strip(), "conf", "testcli.ini")
            if os.path.exists(confFilename):
                self.appOptions = configparser.ConfigParser()
                self.appOptions.read(confFilename)
        if self.appOptions is None:
            # 之前的读取都没有找到，以系统默认目录为准
            confFilename = os.path.join(os.path.dirname(__file__), "conf", "testcli.ini")
            if os.path.exists(confFilename):
                self.appOptions = configparser.ConfigParser()
                self.appOptions.read(confFilename)
            else:
                raise TestCliException("Can not open config file [" + confFilename + "]")

        # 追加系统内部必须使用的h2mem、h2tcp、meta_driver
        h2JarFile = None
        for root, dirs, files in os.walk(
                os.path.join(os.path.dirname(__file__), "jlib")):
            for file in files:
                if file.startswith("h2-") and file.endswith(".jar"):
                    h2JarFile = os.path.abspath(os.path.join(root, str(file)))
                    break
            if h2JarFile is not None:
                break
        if h2JarFile is None:
            raise TestCliException("Corruptted jlib directory. H2 driver file missed.")
        if "driver" not in self.appOptions.sections():
            self.appOptions.add_section("driver")
        self.appOptions.add_section("meta_driver")
        self.appOptions.set("meta_driver", "driver", "org.h2.Driver")
        self.appOptions.set("meta_driver", "jdbcurl",
                            "jdbc:h2:mem:testclimeta;TRACE_LEVEL_SYSTEM_OUT=0;TRACE_LEVEL_FILE=0")
        self.appOptions.add_section("h2_memdriver")
        self.appOptions.set("h2_memdriver", "filename", h2JarFile)
        self.appOptions.set("h2_memdriver", "driver", "org.h2.Driver")
        self.appOptions.set("h2_memdriver", "jdbcurl", "jdbc:h2:mem:")
        self.appOptions.add_section("h2_tcpdriver")
        self.appOptions.set("h2_tcpdriver", "filename", h2JarFile)
        self.appOptions.set("h2_tcpdriver", "driver", "org.h2.Driver")
        self.appOptions.set("h2_tcpdriver", "jdbcurl", "jdbc:h2:${driverType}://${host}:${port}/${service}")
        self.appOptions.set("driver", "h2mem", "h2_memdriver")
        self.appOptions.set("driver", "h2tcp", "h2_tcpdriver")

        # 加载referenceFile文件
        if self.referenceFile is not None:
            if not os.path.isfile(self.referenceFile):
                raise TestCliException("Reference file [" + self.referenceFile + "] does not exist!")
            with open(file=self.referenceFile, mode="r", encoding="utf-8") as fp:
                self.referenceContent = fp.readlines()
            currentScenarioId = "__init__"
            currentScenarioContents = []
            linepos = 0
            referenceId = 1
            for reference in self.referenceContent:
                linepos = linepos + 1
                matchObj1 = re.search(r"--(\s+)?\[Hint](\s+)?Scenario:(.*)", reference,
                                      re.IGNORECASE | re.DOTALL)
                matchObj2 = re.search(r"--(\s+)?\[(\s+)?Scenario:(.*)]", reference,
                                      re.IGNORECASE | re.DOTALL)
                if matchObj1 or matchObj2:
                    if matchObj1:
                        senarioInfo = matchObj1.group(3).strip()
                    else:
                        senarioInfo = matchObj2.group(3).strip()
                    if len(senarioInfo.split(':')) >= 2:
                        scenarioId = senarioInfo.split(':')[0].strip()
                    else:
                        scenarioId = senarioInfo.split(':')[0].strip()
                    if scenarioId.lower() == "end":
                        # 测试场景已经结束
                        currentScenarioContents.append(reference.strip())
                        self.referenceScenario.update(
                            {
                                currentScenarioId: currentScenarioContents
                            }
                        )
                        currentScenarioId = "__REF__" + str(referenceId)
                        currentScenarioContents = []
                        referenceId = referenceId + 1
                        continue
                    if currentScenarioId != scenarioId:
                        # 测试场景已经结束
                        self.referenceScenario.update(
                            {
                                currentScenarioId: currentScenarioContents
                            }
                        )
                        currentScenarioId = scenarioId
                        currentScenarioContents = [reference.strip()]
                        continue

                currentScenarioContents.append(reference.strip())
            # 最后一个测试场景
            if currentScenarioId is not None:
                self.referenceScenario.update(
                    {
                        currentScenarioId: currentScenarioContents
                    }
                )

        # print("self.reference=" + json.dumps(self.reference, indent=4, ensure_ascii=False))
        # 打开输出日志, 如果打开失败，就直接退出
        try:
            if self.logfilename is not None:
                self.logfile = open(self.logfilename, mode="w", encoding=self.testOptions.get("RESULT_ENCODING"))
                self.cmdExecuteHandler.logfile = self.logfile
        except IOError:
            if "TESTCLI_DEBUG" in os.environ:
                print('traceback.print_exc():\n%s' % traceback.print_exc())
                print('traceback.format_exc():\n%s' % traceback.format_exc())
            raise TestCliException("Can not open logfile for write [" + self.logfilename + "]" + os.getcwd())

        # 如果要求打开扩展日志，则打开扩展日志
        if self.xlogFile is not None and self.xlogFile != "":
            # 创建文件，并写入文件头信息
            if self.xlogOverwrite:
                # 如果打开了覆盖模式，则删除之前的历史文件
                if os.path.exists(self.xlogFile):
                    os.remove(self.xlogFile)
            self.xlogFileFullPath = os.path.abspath(self.xlogFile)
            self.xlogFileHandle = sqlite3.connect(
                database=self.xlogFile,
                check_same_thread=False,
            )
            cursor = self.xlogFileHandle.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS TestCli_Xlog "
                           "("
                           "  Id              INTEGER PRIMARY KEY AUTOINCREMENT,"
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
                           "  ScenarioId      TEXT,"
                           "  TestRunId       TEXT,"
                           "  ScenarioName    TEXT"
                           ")"
                           "")
            cursor.execute("CREATE TABLE IF NOT EXISTS TestCli_PerfLog "
                           "("
                           "  Id              INTEGER PRIMARY KEY AUTOINCREMENT,"
                           "  MonitorTime     DATETIME,"
                           "  TaskId          NUMERIC,"
                           "  TaskName        TEXT,"
                           "  MonitorItem     TEXT,"
                           "  MonitorValue    TEXT"
                           ")")
            cursor.close()

        # 加载已经被隐式包含的数据库驱动，文件放置在testcli\jlib下
        # 首先尝试TESTCLI_JLIBDIR下的内容，其次查看安装目录下的东西
        jlibDirectory = None
        if "TESTCLI_JLIBDIR" in os.environ:
            # 如果定义了TESTCLI_JLIBDIR，则查找TESTCLLI_JLIBDIR的位置
            jlibDirectory = str(os.environ["TESTCLI_JLIBDIR"])
            if not os.path.isdir(jlibDirectory):
                raise TestCliException("Can not open jlib directory for read [" + jlibDirectory + "]")
        if jlibDirectory is None and "TESTCLI_HOME" in os.environ:
            # 如果定义了TESTCLI_HOME，则查找TESTCLI_HOME/jlib目录
            jlibDirectory = str(os.path.join(os.environ["TESTCLI_HOME"], "jlib"))
            if not os.path.isdir(jlibDirectory):
                jlibDirectory = None
        if jlibDirectory is None:
            # 如果仍然找不到，则查找安装目录的jlib目录
            jlibDirectory = os.path.join(os.path.dirname(__file__), "jlib")
        if not os.path.isdir(jlibDirectory):
            raise TestCliException("Can not open jlib directory for read [" + jlibDirectory + "]")

        if self.db_connectionConf is None:
            self.db_connectionConf = []
        if self.appOptions is not None:
            for row in self.appOptions.items("driver"):
                m_DriverName = None
                driverJarList = []
                m_JDBCURL = None
                m_JDBCProp = None
                driverJarFileName = None
                m_DatabaseType = row[0].strip()
                for m_driversection in str(row[1]).split(','):
                    m_driversection = m_driversection.strip()
                    if m_DriverName is None:
                        try:
                            m_DriverName = self.appOptions.get(m_driversection, "driver")
                        except (configparser.NoSectionError, configparser.NoOptionError):
                            m_DriverName = None
                    if m_JDBCURL is None:
                        try:
                            m_JDBCURL = self.appOptions.get(m_driversection, "jdbcurl")
                        except (configparser.NoSectionError, configparser.NoOptionError):
                            m_JDBCURL = None
                    if m_JDBCProp is None:
                        try:
                            m_JDBCProp = self.appOptions.get(m_driversection, "jdbcprop")
                        except (configparser.NoSectionError, configparser.NoOptionError):
                            m_JDBCProp = None
                    if driverJarFileName is None:
                        try:
                            for driverJarFileName in self.appOptions.get(m_driversection, "filename").split(','):
                                driverJarFileName = driverJarFileName.strip()
                                if os.path.exists(os.path.join(jlibDirectory, driverJarFileName)):
                                    driverJarList.append(os.path.abspath(os.path.join(jlibDirectory, driverJarFileName)))
                                    if "TESTCLI_DEBUG" in os.environ:
                                        print("Load jar ..! [" +
                                              os.path.join(jlibDirectory, driverJarFileName) + "]")
                                    driverJarFileName = None
                                else:
                                    if "TESTCLI_DEBUG" in os.environ:
                                        print("Driver file does not exist! [" +
                                              os.path.join(jlibDirectory, driverJarFileName) + "]")
                        except (configparser.NoSectionError, configparser.NoOptionError):
                            driverJarFileName = None
                jarConfig = {"ClassName": m_DriverName,
                             "FullName": driverJarList,
                             "JDBCURL": m_JDBCURL,
                             "JDBCProp": m_JDBCProp,
                             "Database": m_DatabaseType}
                self.db_connectionConf.append(jarConfig)

        # 设置Meta连接时候需要用到的JarList1
        jarList = []
        for jarConfig in self.db_connectionConf:
            jarFileNames = jarConfig["FullName"]
            for jarFileName in jarFileNames:
                if jarFileName not in jarList:
                    jarList.append(jarFileName)
        self.MetaHandler.setJVMJarList(jarList)
        self.MetaHandler.setAppOptions(self.appOptions)

        # 对于子进程，连接到JOB管理服务
        if "TESTCLI_JOBMANAGERURL" in os.environ:
            m_JobManagerURL = os.environ["TESTCLI_JOBMANAGERURL"]
            # 对于被主进程调用的进程，则不需要考虑, 连接到主进程的Meta服务商
            self.MetaHandler.ConnectServer(m_JobManagerURL)
            self.JobHandler.setMetaConn(self.MetaHandler.dbConn)
            self.testOptions.set("JOBMANAGER_METAURL", m_JobManagerURL)

        # 处理传递的映射文件, 首先加载参数的部分，如果环境变量里头有设置，则环境变量部分会叠加参数部分
        if self.commandMap is not None:
            # 如果传递的参数，有Mapping，以参数为准，先加载参数中的Mapping文件
            self.cmdMappingHandler.loadCommandMappings(self.commandScript, self.commandMap)
        if "SQLCLI_COMMANDMAPPING" in os.environ:
            # 如果没有参数，则以环境变量中的信息为准
            if len(os.environ["SQLCLI_COMMANDMAPPING"].strip()) > 0:
                self.cmdMappingHandler.loadCommandMappings(self.commandScript, os.environ["SQLCLI_COMMANDMAPPING"])
        if "TESTCLI_COMMANDMAPPING" in os.environ:
            # 如果没有参数，则以环境变量中的信息为准
            if len(os.environ["TESTCLI_COMMANDMAPPING"].strip()) > 0:
                self.cmdMappingHandler.loadCommandMappings(self.commandScript, os.environ["TESTCLI_COMMANDMAPPING"])

        # 给Page做准备，PAGE显示的默认换页方式.
        if not os.environ.get("LESS"):
            os.environ["LESS"] = "-RXF"

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

        # 还原sys.stdout和sys.stderr
        if self.__sysstdout_origin is not None:
            sys.stdout = self.__sysstdout_origin
        if self.__sysstderr_origin is not None:
            sys.stderr = self.__sysstderr_origin

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
                                            'Version: ' + self.version + ' | ' +
                                            (
                                                "Not Connected." if self.db_conn is None
                                                else "Connected with " + str(self.db_username) +
                                                     "/******@" + str(self.db_url)
                                            )) + ' | ' +
                                         ' Type "_HELP" to get help information.' + ' | ' +
                                         ' Type "_EXIT" to exit app.' + ' | ' +
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
            """
                显示输出结果
                
                根据OFLAG决定哪些内容需要打印到哪里去，而不是全部打印
            """
            def show_result(p_result):
                # 输出显示结果
                if "type" in p_result.keys():
                    if p_result["type"] == "echo":
                        message = p_result["message"]
                        m_EchoFlag = OFLAG_LOGFILE | OFLAG_LOGGER | OFLAG_CONSOLE | OFLAG_ECHO | OFLAG_SPOOL
                        if re.match(r'echo\s+off', p_result["message"], re.IGNORECASE):
                            # Echo Off这个语句，不打印到Echo文件中
                            m_EchoFlag = m_EchoFlag & ~OFLAG_ECHO
                        if p_result["script"] is None and sys.stdin.isatty():
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
                            if p_result["script"] == "Console" and sys.stdin.isatty():
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
                        if self.testOptions.get("TERMOUT").upper() == 'ON':
                            cur = p_result["rows"]
                        else:
                            cur = []
                        headers = p_result["headers"]
                        columnTypes = p_result["columnTypes"]
                        status = p_result["status"]

                        # 不控制每行的长度
                        max_width = None

                        # title 包含原有语句的SQL信息，如果ECHO打开的话
                        # headers 包含原有语句的列名
                        # cur 是语句的执行结果
                        # output_format 输出格式
                        #   csv                csv格式显示，自己实现
                        #   tab                默认，表格形式（用format_output_tab自己编写)
                        if "rowPos" in p_result.keys():
                            rowPos = p_result["rowPos"]
                        else:
                            rowPos = 0
                        formatted = self.format_output(
                            title, cur, headers, columnTypes,
                            self.testOptions.get("OUTPUT_FORMAT").lower(),
                            rowPos,
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

                # 如果遇到了错误，且设置了breakWithError，则立刻退出
                if result["type"] == "error":
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

    # 返回语句的上一次执行结果
    @staticmethod
    def getLastCommandResult():
        return lastCommandResult

    # 主程序
    def run_cli(self):
        # 如果参数要求不显示版本，则不再显示版本
        if not self.nologo:
            self.echo(
                s="TestCli Release " + __version__,
                Flags=OFLAG_LOGGER | OFLAG_CONSOLE | OFLAG_SPOOL | OFLAG_ECHO,
            )

        # 如果运行在脚本方式下，不再调用PromptSession
        # 运行在无终端的模式下，也不会调用PromptSession
        # 对于脚本程序，在执行脚本完成后就会自动退出
        if self.commandScript is None and not self.HeadlessMode and sys.stdin.isatty():
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
            # 如果用户指定了用户名，口令，尝试直接进行数据库连接
            if self.logon:
                if not self.DoCommand("_connect " + str(self.logon)):
                    raise EOFError

            # 开始依次处理控制台送来的语句
            if not self.commandScript and sys.stdin.isatty():
                while True:
                    # 循环从控制台读取命令
                    if not self.DoCommand():
                        raise EOFError

            # 如果传递的参数中有脚本文件，先执行脚本文件, 执行完成后自动退出
            try:
                if self.commandScript:
                    # 如果有脚本目录，则运行的时候切换到脚本所在的目录下，运行结束后要返回当前目录
                    currentPwd = os.getcwd()
                    scriptDir = os.path.dirname(str(self.commandScript))
                    scriptBase = os.path.basename(str(self.commandScript))
                    if scriptDir.strip() != "":
                        # 如果脚本不是当前目录，需要切换到脚本目录下
                        # 如果脚本是当前目录，切换到空目录会报错，所以不能切换
                        os.chdir(scriptDir)
                    self.DoCommand(text='_start ' + scriptBase)
                    if scriptDir.strip() != "":
                        # 如果发生了脚本切换，则执行脚本后要返回切换前的目录
                        os.chdir(currentPwd)
                else:
                    # 系统没有标准输入终端，那么从stdin中读取信息
                    #  not sys.stdin.isatty()
                    stdinCommand = ""
                    if not sys.stdin.isatty():
                        for line in sys.stdin:
                            stdinCommand = stdinCommand + "\n" + line
                    self.DoCommand(text=stdinCommand)
            except TestCliException:
                raise EOFError
            self.DoCommand(text='_exit')
        except (TestCliException, EOFError):
            pass

        # 关闭监控进程
        stopMonitorManager()

        # 退出进程, 如果要求不显示logo，则也不会显示Disconnected字样
        if self.exitValue == 0:
            if not self.nologo:
                self.echo("Disconnected.")
        else:
            if not self.nologo:
                self.echo("Disconnected with [" + str(self.exitValue) + "].")

        # 取消进程共享服务的注册信息
        self.JobHandler.unregisterjob()
        self.JobHandler.unregisterAgent()

        # 关闭Meta服务
        if self.MetaHandler is not None:
            self.MetaHandler.ShutdownServer()
            self.MetaHandler = None

        # 还原进程标题
        setproctitle.setproctitle(cliProcessTitleBak)

        # 如果需要，查看日志比对结果
        if self.referenceFile is not None:
            currentScenarioId = "__init__"
            currentScenarioContents = []
            self.logfileScenario = {}
            linepos = 0
            referenceId = 1
            for logContent in self.logfileContent:
                linepos = linepos + 1
                matchObj1 = re.search(r"--(\s+)?\[Hint](\s+)?Scenario:(.*)", logContent, re.IGNORECASE | re.DOTALL)
                matchObj2 = re.search(r"--(\s+)?\[(\s+)?Scenario:(.*)]", logContent, re.IGNORECASE | re.DOTALL)
                if matchObj1 or matchObj2:
                    if matchObj1:
                        senarioInfo = matchObj1.group(3).strip()
                    else:
                        senarioInfo = matchObj2.group(3).strip()
                    if len(senarioInfo.split(':')) >= 2:
                        scenarioId = senarioInfo.split(':')[0].strip()
                    else:
                        scenarioId = senarioInfo.split(':')[0].strip()
                    if scenarioId.lower() == "end":
                        # 测试场景已经结束
                        currentScenarioContents.append(logContent.strip())
                        self.logfileScenario.update(
                            {
                                currentScenarioId: currentScenarioContents
                            }
                        )
                        currentScenarioId = "__REF__" + str(referenceId)
                        currentScenarioContents = []
                        referenceId = referenceId + 1
                        continue
                    if currentScenarioId != scenarioId:
                        # 测试场景已经结束
                        self.logfileScenario.update(
                            {
                                currentScenarioId: currentScenarioContents
                            }
                        )
                        currentScenarioId = scenarioId
                        currentScenarioContents = [logContent.strip()]
                        continue
                currentScenarioContents.append(logContent.strip())
            # 最后一个测试场景
            if currentScenarioId is not None:
                self.logfileScenario.update(
                    {
                        currentScenarioId: currentScenarioContents
                    }
                )

            # 对比文件内容，并给出dif和suc内容
            compareResult, newCompareResultList = self.referenceCompareHandler.compare_text(
                lines1=self.logfileContent,
                lines2=self.referenceContent,
                CompareWithMask=compareOption["mask"],
                CompareIgnoreCase=not compareOption["case"],
                CompareIgnoreTailOrHeadBlank=not compareOption["trim"],
                compareAlgorithm=compareOption["algorithm"],
                ignoreEmptyLine=compareOption["igblank"],
                skipLines=compareSkipLines,
                maskLines=compareMaskLines
            )
            # 生成dif和suc文件
            if self.logfilename is not None:
                name, ext = os.path.splitext(self.logfilename)
            else:
                name, ext = os.path.splitext(self.commandScript)
            if "T_WORK" in os.environ:
                difFileName = os.path.join(os.environ["T_WORK"], os.path.basename(name + ".dif"))
                sucFileName = os.path.join(os.environ["T_WORK"], os.path.basename(name + ".suc"))
                rptFileName = os.path.join(os.environ["T_WORK"], os.path.basename(name + ".rpt"))
            else:
                difFileName = os.path.join(self.ProcessPwd, os.path.basename(name + ".dif"))
                sucFileName = os.path.join(self.ProcessPwd, os.path.basename(name + ".suc"))
                rptFileName = os.path.join(self.ProcessPwd, os.path.basename(name + ".rpt"))
            if os.path.exists(difFileName):
                os.remove(difFileName)
            if os.path.exists(sucFileName):
                os.remove(sucFileName)
            if os.path.exists(rptFileName):
                os.remove(rptFileName)
            if compareResult:
                resultFileName = sucFileName
            else:
                resultFileName = difFileName
            newCompareResultList = [s + "\n" for s in newCompareResultList]

            with open(file=resultFileName, mode="w", encoding="UTF-8") as fp:
                fp.writelines(newCompareResultList)

            # 生成xdb文件, 里头包含的信息有：
            # ScenarioId, ScenarioName, Elapsed, Status, MessageShort
            if self.xlogFileHandle is not None:
                cursor = self.xlogFileHandle.cursor()
                cursor.execute(
                    "SELECT     ScenarioId,ScenarioName,SuiteName,CaseName,"
                    "           Min(Started) Started, Sum(Elapsed) Elapsed "
                    "FROM       TestCli_Xlog "
                    "Group By   ScenarioId,ScenarioName,SuiteName,CaseName "
                    "Order by 1,2"
                )
                rs = cursor.fetchall()
                field_names = [i[0] for i in cursor.description]
                cursor.close()
                data = []
                for row in rs:
                    rowMap = {}
                    for i in range(0, len(row)):
                        rowMap[field_names[i]] = row[i]
                    data.append(rowMap)

                scenarioResult = {}
                for scenarioId in self.logfileScenario.keys():
                    if scenarioId in self.referenceScenario.keys():
                        compareResult, newCompareResultList = self.referenceCompareHandler.compare_text(
                            lines1=self.logfileScenario[scenarioId],
                            lines2=self.referenceScenario[scenarioId],
                            CompareWithMask=compareOption["mask"],
                            CompareIgnoreCase=not compareOption["case"],
                            CompareIgnoreTailOrHeadBlank=not compareOption["trim"],
                            compareAlgorithm=compareOption["algorithm"],
                            ignoreEmptyLine=compareOption["igblank"],
                            skipLines=compareSkipLines,
                            maskLines=compareMaskLines
                        )
                        if compareResult:
                            scenarioResult[scenarioId] = {
                                "Status": "Successed",
                                "Content": self.logfileScenario[scenarioId]
                            }
                        else:
                            scenarioResult[scenarioId] = {
                                "Status": "Failed",
                                "Content": newCompareResultList
                            }
                    else:
                        scenarioResult[scenarioId] = {
                            "Status": "Failed",
                            "Content": self.logfileScenario[scenarioId]
                        }
                rptInfo = {}
                for row in data:
                    scenarioId = row["ScenarioId"]
                    if scenarioId in scenarioResult.keys():
                        scenarioStatus = scenarioResult[scenarioId]["Status"]
                        scenarioMessage = "\n".join(scenarioResult[scenarioId]["Content"])
                    else:
                        scenarioStatus = "UNKNOWN"
                        scenarioMessage = ""
                    # 检查该Scenario是否顺利完成
                    rptInfo[scenarioId] = {
                        "Name": row["ScenarioName"],
                        "Started": row["Started"],
                        "Elapsed": float("%8.2f" % row["Elapsed"]),
                        "Status": scenarioStatus,
                        "Message": scenarioMessage,
                        "SuiteName": row["SuiteName"],
                        "CaseName": row["CaseName"]
                    }
                with open(file=rptFileName, mode='w', encoding="UTF-8") as f:
                    json.dump(obj=rptInfo, fp=f, indent=4, sort_keys=True, ensure_ascii=False)

        # 关闭LogFile
        if self.logfile is not None:
            self.logfile.flush()
            self.logfile.close()
            self.logfile = None

        # 关闭扩展日志的句柄
        if self.xlogFileHandle is not None:
            self.xlogFileHandle.close()
            self.xlogFileHandle = None

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
                outputPrefix = self.testOptions.get('OUTPUT_PREFIX') + " "
            else:
                outputPrefix = ''
            match_obj = re.match(self.nameSpace + r">(\s+)?set(\s+)?OUTPUT_PREFIX(\s+)?$", s, re.IGNORECASE | re.DOTALL)
            if match_obj:
                outputPrefix = ''
            if Flags & OFLAG_LOGFILE:
                self.logfileContent.append(outputPrefix + s)
                if self.logfile is not None:
                    print(outputPrefix + s, file=self.logfile)
                    self.logfile.flush()
            if Flags & OFLAG_SPOOL:
                if self.SpoolFileHandler is not None:
                    for m_SpoolFileHandler in self.SpoolFileHandler:
                        print(outputPrefix + s, file=m_SpoolFileHandler)
                        m_SpoolFileHandler.flush()
            if Flags & OFLAG_LOGGER:
                if self.logger is not None:
                    self.logger.info(outputPrefix + s)
            if Flags & OFLAG_ECHO:
                if self.EchoFileHandler is not None:
                    print(outputPrefix + s, file=self.EchoFileHandler)
                    self.EchoFileHandler.flush()
            if Flags & OFLAG_CONSOLE:
                try:
                    click.secho(outputPrefix + s, **kwargs, file=self.Console)
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
        m_csv_delimiter = self.testOptions.get("OUTPUT_CSV_DELIMITER")
        m_csv_quotechar = self.testOptions.get("OUTPUT_CSV_QUOTECHAR")
        if m_csv_delimiter.find("\\t") != -1:
            m_csv_delimiter = m_csv_delimiter.replace("\\t", '\t')
        if m_csv_delimiter.find("\\s") != -1:
            m_csv_delimiter = m_csv_delimiter.replace("\\s", ' ')

        # 打印字段名称
        if self.testOptions.get("OUTPUT_CSV_HEADER") == "ON":
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

    def format_output_tab(self, headers, columnTypes, cur, startIter: int):
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
        m_RowNo = startIter
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
                                ("NVARCHAR", "NCHAR", "VARCHAR", "LONGVARCHAR", "CHAR",
                                 "CLOB", "NCLOB", "STRUCT", "ARRAY", "DATE"):
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

    def format_output(self, title, cur, headers, columnTypes, p_format_name, startIter, max_width=None):
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
                formatted = self.format_output_tab(headers, columnTypes, cur, startIter)
            else:
                raise TestCliException("SQLCLI-0000: Unknown output_format. CSV|TAB only")
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
        # 线程名称         processName

        # 如果没有打开性能日志记录文件，直接跳过
        if self.xlogFileHandle is None:
            return

        # 多进程，多线程写入，考虑锁冲突
        try:
            # 对于多线程运行，这里的processName格式为JOB_NAME#副本数-完成次数
            # 对于单线程运行，这里的processName格式为固定的MAIN
            processName = str(commandResult["processName"])

            # 写入内容信息
            if self.executeScript is None:
                script = "Console"
            else:
                script = str(os.path.basename(self.executeScript))
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
                str(processName),
                str(self.suitename),
                str(self.casename),
                str(self.testRunId),
                str(commandResult["scenarioId"]),
                str(commandResult["scenarioName"])
            )
            cursor.execute(
                "Insert Into TestCli_Xlog(Script,Started,Elapsed,RawCommand,"
                "CommandType,Command,CommandStatus,ErrorCode,WorkerName,SuiteName,CaseName,"
                "TestRunId, ScenarioId, ScenarioName) "
                "Values(?,?,?,?,  ?,?,?,?,?,?,?,  ?,?,?)",
                data
            )
            cursor.close()
            self.xlogFileHandle.commit()
        except Exception as ex:
            print("Internal error:: xlog file [" + str(self.xlogFile) + "] write not complete. " + repr(ex))
