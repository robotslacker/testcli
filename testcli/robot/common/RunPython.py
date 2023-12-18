# -*- coding: UTF-8 -*-
import os
import sys
import traceback
import pytest
import sqlite3
import time
import multiprocessing
from robot.errors import ExecutionFailed
from robot.api import logger
from robot.running.context import EXECUTION_CONTEXTS
try:
    from .common.xmltodict import XmlFileToDict
except ImportError:
    from common.xmltodict import XmlFileToDict


def runPythonScript(scriptFileName, logFileName, pythonPathList):
    # 切换输出到指定的文件中
    sys.stdout = open(logFileName, mode="a")
    sys.stderr = open(logFileName, mode="a")
    sys.__stdout__ = open(logFileName, mode="a")
    sys.__stderr__ = open(logFileName, mode="a")

    # 增加Python的执行路径
    for pythonPath in pythonPathList:
        if pythonPath not in sys.path:
            sys.path.append(pythonPath)

    # 开始运行指定的Python程序
    try:
        with open(scriptFileName, mode='r', encoding="utf-8") as f:
            scriptContent = f.read()
            exec(scriptContent)
    except Exception:
        print('traceback.print_exc():\n%s' % traceback.print_exc())
        print('traceback.format_exc():\n%s' % traceback.format_exc())

    # 关闭输出文件
    sys.stdout.close()
    sys.stderr.close()
    sys.__stderr__.close()
    sys.__stdout__.close()


class RunPython(object):
    # TEST SUITE 在suite中引用，只会实例化一次
    # 也就是说多test case都引用了这个类的方法，但是只有第一个test case调用的时候实例化
    # 如果一个Suite多个Case引用设置类的方法，要注意先后的影响
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    __BreakWithError = False                # 是否遇到错误就退出，默认是不退出
    xlogFileHandle = None                   # 扩展日志的句柄
    pythonPathList = []                     # Python的执行包路径

    def Append_Python_Path(self, pythonPath):
        pythonPath = os.path.abspath(pythonPath)
        if os.path.exists(pythonPath):
            if pythonPath not in self.pythonPathList:
                self.pythonPathList.append(pythonPath)
                logger.info("<b>Append Python Path : " + str(pythonPath) + ". </b>", html=True)
        else:
            logger.warn(
                "<b>Append Python Path : " + str(pythonPath) + ". Directory does not exist!</b>",
                html=True)

    def Execute_Python_Script(self, scriptFileName, logFileName=None):
        try:
            logger.info('<b>===== Logon_And_Execute_Script</b> [' + str(scriptFileName) + '] ', html=True)

            # 判断文件是否存在
            if not os.path.exists(scriptFileName):
                raise RuntimeError("Script [" + scriptFileName + "] does not exist.")

            # 如果路径名中包含空格，则需要用单引号包括起来
            if str(scriptFileName).find(' ') != -1 and not str(scriptFileName).startswith("'"):
                scriptFileName = "'" + scriptFileName + "'"

            # 处理日志文件名
            # 如果没有提供文件名， 有T_WORK，   日志是T_WORK下和SQL同名的.log文件
            # 如果没有提供文件名， 没有T_WORK， 日志是当前目录下和SQL同名的.log文件
            # 如果提供了文件名，   并且是全路径名， 用提供的名字
            # 如果提供了文件名，   但不是全路径名，有T_WORK下，在T_WORK下生成提供的文件名
            # 如果提供了文件名，   但不是全路径名，没有T_WORK下，在当前目录下生成提供的文件名
            if logFileName is None:
                if "T_WORK" in os.environ:
                    m_szLogOutPutFileName = os.path.join(
                        os.environ["T_WORK"],
                        os.path.basename(scriptFileName).split('.')[0] + ".log")
                    logOutPutFullFileName = os.path.join(os.environ["T_WORK"], m_szLogOutPutFileName)
                else:
                    m_szLogOutPutFileName = os.path.join(
                        os.getcwd(),
                        os.path.basename(scriptFileName).split('.')[0] + ".log")
                    logOutPutFullFileName = os.path.join(os.getcwd(), m_szLogOutPutFileName)
            else:
                if "T_WORK" in os.environ:
                    logOutPutFullFileName = os.path.join(os.environ["T_WORK"], logFileName)
                else:
                    logOutPutFullFileName = os.path.join(os.getcwd(), logFileName)
            xdbReportFile = logOutPutFullFileName[:-4] + ".xdb"

            # 如果Log目录不存在，则创建Log目录
            if not os.path.exists(os.path.dirname(logOutPutFullFileName)):
                os.makedirs(os.path.dirname(logOutPutFullFileName))

            logger.info('<b>===== Execute</b>     [' + scriptFileName + ']', html=True)
            logger.info('<b>===== LogFile</b>     [' + str(logOutPutFullFileName) + ']', html=True)

            sys.__stdout__.write('\n')  # 打印一个空行，好保证在Robot上Console显示不错行
            sys.__stdout__.write('===== Execute     [' + scriptFileName + ']\n')
            sys.__stdout__.write('===== LogFile     [' + logOutPutFullFileName + ']\n')
            sys.__stdout__.write('===== Starting .....\n')

            # 备份当前的系统输出和错误输出
            stdout_bak = sys.stdout
            stderr_bak = sys.stderr
            internal_stdout_bak = sys.__stdout__
            internal_stderr_bak = sys.__stderr__

            # 在子进程中运行，以确保子进程的失败不会影响到主程序
            processManagerContext = multiprocessing.get_context("spawn")
            process = processManagerContext.Process(
                target=runPythonScript,
                args=(scriptFileName, logOutPutFullFileName, self.pythonPathList)
            )
            processStartTime = time.time()
            process.start()
            process.join()
            processEndTime = time.time()
            exitCode = process.exitcode

            # 还原当前的系统输出和错误输出
            sys.stdout = stdout_bak
            sys.stderr = stderr_bak
            sys.__stdout__ = internal_stdout_bak
            sys.__stderr__ = internal_stderr_bak

            sys.__stdout__.write("===== Finished with ret [" + str(exitCode) + "] .....\n")

            # 记录扩展日志
            if EXECUTION_CONTEXTS.current is None:
                suiteName = "--------"
                caseName = "--------"
            else:
                suiteName = str(EXECUTION_CONTEXTS.current.suite)
                if hasattr(EXECUTION_CONTEXTS.current.test, "name"):
                    caseName = str(EXECUTION_CONTEXTS.current.test.name)
                else:
                    caseName = "--------"  # Setup Or TearDown

            self.xlogFileHandle = sqlite3.connect(
                database=xdbReportFile,
                check_same_thread=False,
            )
            cursor = self.xlogFileHandle.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS TestCli_Xlog "
                           "("
                           "  Id              INTEGER PRIMARY KEY AUTOINCREMENT,"
                           "  Script          TEXT,"
                           "  Started         DATETIME,"
                           "  Elapsed         NUMERIC,"
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
            cursor = self.xlogFileHandle.cursor()
            # 对于单体的Python测试，scenarioId, scenarioName同时为caseName
            data = (
                scriptFileName,
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(processStartTime)),
                "%8.2f" % (processEndTime - processStartTime),
                str(exitCode),
                os.path.basename(scriptFileName) + "-" + str(os.getpid()),
                str(suiteName),
                str(caseName),
                "PYTHONSCRIPT",
                str(os.environ['T_RUNID']),
                caseName,
                caseName
            )
            cursor.execute(
                "Insert Into TestCli_Xlog(Script,Started,Elapsed,"
                "ErrorCode,WorkerName,SuiteName,CaseName, "
                "CommandType, TestRunId, ScenarioId, ScenarioName) "
                "Values(?,?,?,  ?,?,?,?, ?,?,?,?)",
                data
            )
            cursor.close()
            self.xlogFileHandle.commit()
            self.xlogFileHandle.close()

            # 如果有失败信息，则直接退出
            if exitCode != 0:
                raise ExecutionFailed(
                    message="Test failed. Please check more information.",
                    continue_on_failure=self.__BreakWithError
                )
        except RuntimeError as ex:
            raise ex
        except Exception as ex:
            logger.info('str(e):  ', str(ex))
            logger.info('repr(e):  ', repr(ex))
            logger.info('traceback.print_exc():\n%s' % traceback.print_exc())
            logger.info('traceback.format_exc():\n%s' % traceback.format_exc())
            raise RuntimeError("TEST Execute failed.")

    def Execute_Pytest_Script(self, scriptFileName, logFileName=None):
        try:
            logger.info('<b>===== Logon_And_Execute_Script</b> [' + str(scriptFileName) + '] ', html=True)

            # 判断文件是否存在
            if not os.path.exists(scriptFileName):
                raise RuntimeError("Script [" + scriptFileName + "] does not exist.")

            # 如果路径名中包含空格，则需要用单引号包括起来
            if str(scriptFileName).find(' ') != -1 and not str(scriptFileName).startswith("'"):
                scriptFileName = "'" + scriptFileName + "'"

            # 处理日志文件名
            # 如果没有提供文件名， 有T_WORK，   日志是T_WORK下和SQL同名的.log文件
            # 如果没有提供文件名， 没有T_WORK， 日志是当前目录下和SQL同名的.log文件
            # 如果提供了文件名，   并且是全路径名， 用提供的名字
            # 如果提供了文件名，   但不是全路径名，有T_WORK下，在T_WORK下生成提供的文件名
            # 如果提供了文件名，   但不是全路径名，没有T_WORK下，在当前目录下生成提供的文件名
            if logFileName is None:
                if "T_WORK" in os.environ:
                    m_szLogOutPutFileName = os.path.join(
                        os.environ["T_WORK"],
                        os.path.basename(scriptFileName).split('.')[0] + ".log")
                    logOutPutFullFileName = os.path.join(os.environ["T_WORK"], m_szLogOutPutFileName)
                else:
                    m_szLogOutPutFileName = os.path.join(
                        os.getcwd(),
                        os.path.basename(scriptFileName).split('.')[0] + ".log")
                    logOutPutFullFileName = os.path.join(os.getcwd(), m_szLogOutPutFileName)
            else:
                if "T_WORK" in os.environ:
                    logOutPutFullFileName = os.path.join(os.environ["T_WORK"], logFileName)
                else:
                    logOutPutFullFileName = os.path.join(os.getcwd(), logFileName)
            htmlReportFile = logOutPutFullFileName[:-4] + ".html"
            junitReportFile = logOutPutFullFileName[:-4] + ".xml"
            xdbReportFile = logOutPutFullFileName[:-4] + ".xdb"

            # 如果Log目录不存在，则创建Log目录
            if not os.path.exists(os.path.dirname(logOutPutFullFileName)):
                os.makedirs(os.path.dirname(logOutPutFullFileName))

            logger.info('<b>===== Execute</b>     [' + scriptFileName + ']', html=True)
            logger.info('<b>===== LogFile</b>     [' + str(logOutPutFullFileName) + ']', html=True)
            logger.info('<b>===== PytestLog</b>   [<a href="' + os.path.basename(htmlReportFile) + '">Pytest report: ' +
                        os.path.basename(htmlReportFile) + '</a>].', html=True)

            sys.__stdout__.write('\n')  # 打印一个空行，好保证在Robot上Console显示不错行
            sys.__stdout__.write('===== Execute     [' + scriptFileName + ']\n')
            sys.__stdout__.write('===== LogFile     [' + logOutPutFullFileName + ']\n')
            sys.__stdout__.write('===== Starting .....\n')

            # 备份当前的系统输出和错误输出
            stdout_bak = sys.stdout
            stderr_bak = sys.stderr
            internal_stdout_bak = sys.__stdout__
            internal_stderr_bak = sys.__stderr__

            # 切换输出到指定的文件中
            sys.stdout = open(logOutPutFullFileName, mode="a")
            sys.stderr = open(logOutPutFullFileName, mode="a")
            sys.__stdout__ = open(logOutPutFullFileName, mode="a")
            sys.__stderr__ = open(logOutPutFullFileName, mode="a")
            myargs = [
                "-vs",
                "--capture=sys",
                "--html=" + htmlReportFile,
                "--junitxml=" + junitReportFile,
                scriptFileName,
            ]
            logger.info('<b>===== args</b>     [' + str(myargs) + ']', html=True)
            logger.info('<b>=====  pwd</b>     [' + str(os.getcwd()) + ']', html=True)

            # 追加新的Python路径
            for pythonPath in self.pythonPathList:
                if pythonPath not in sys.path:
                    logger.info('<b>Add Python Path' + str(pythonPath) + '</b>', html=True)
                    sys.path.append(pythonPath)

            # 打印当前的Python执行路径，便于调试
            logger.info('<b>Python Path</b>', html=True)
            print("Python Path:")
            for modulePath in sys.path:
                logger.info("<b>    " + modulePath + "</b>", html=True)
                print("    " + str(modulePath))

            processStartTime = time.time()
            # 运行pytest脚本
            try:
                exitCode = pytest.main(args=myargs, )
            except Exception:
                exitCode = 255
                print('traceback.print_exc():\n%s' % traceback.print_exc())
                print('traceback.format_exc():\n%s' % traceback.format_exc())

            # 关闭输出文件
            sys.stdout.close()
            sys.stderr.close()
            sys.__stderr__.close()
            sys.__stdout__.close()

            # 还原当前的系统输出和错误输出
            sys.stdout = stdout_bak
            sys.stderr = stderr_bak
            sys.__stdout__ = internal_stdout_bak
            sys.__stderr__ = internal_stderr_bak

            sys.__stdout__.write("===== Finished with ret [" + str(exitCode) + "] .....\n")

            # 记录扩展日志
            if EXECUTION_CONTEXTS.current is None:
                suiteName = "--------"
                caseName = "--------"
            else:
                suiteName = str(EXECUTION_CONTEXTS.current.suite)
                if hasattr(EXECUTION_CONTEXTS.current.test, "name"):
                    caseName = str(EXECUTION_CONTEXTS.current.test.name)
                else:
                    caseName = "--------"  # Setup Or TearDown

            self.xlogFileHandle = sqlite3.connect(
                database=xdbReportFile,
                check_same_thread=False,
            )
            cursor = self.xlogFileHandle.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS TestCli_Xlog "
                           "("
                           "  Id              INTEGER PRIMARY KEY AUTOINCREMENT,"
                           "  Script          TEXT,"
                           "  Started         DATETIME,"
                           "  Elapsed         NUMERIC,"
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
            cursor = self.xlogFileHandle.cursor()
            # 对于Pytest测试，读取junitReportFile作为结果
            testResultJson = XmlFileToDict(junitReportFile).get_dict()
            testCases = testResultJson["testsuites"]["testsuite"]["testcase"]
            failureMessages = ""
            if isinstance(testCases, dict):
                if "error" in testCases.keys():
                    failureMessages = (failureMessages + "\nmessage:\n" + testCases["error"]["@message"] +
                                       "\n" + "text:\n" + testCases["error"]["#text"])
            if isinstance(testCases, list):
                for testCase in testCases:
                    if "skipped" in testCase.keys():
                        continue
                    if "failure" in testCase.keys():
                        failureMessages = (failureMessages + "\nmessage:\n" + testCase["failure"]["@message"] +
                                           "\n" + "text:\n" + testCase["failure"]["#text"])
                        commandStatus = "Failure"
                    else:
                        commandStatus = "Failure"
                    scenarioName = testCase["@name"]
                    # 这里有一个隐含的规则，即假设case的名称为 xxx_123，即最后为数字，则将数字作为scenarioId
                    if str(scenarioName).split('_')[-1].isdigit():
                        scenarioId = str(scenarioName).split('_')[-1]
                    else:
                        scenarioId = scenarioName
                    elapsedTime = str(testCase["@time"])
                    data = (
                        scriptFileName,
                        time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(processStartTime)),
                        elapsedTime,
                        "PYTEST",
                        str(caseName),
                        commandStatus,
                        str(exitCode),
                        os.path.basename(scriptFileName) + "-" + str(os.getpid()),
                        str(suiteName),
                        str(caseName),
                        str(os.environ['T_RUNID']),
                        scenarioId,
                        scenarioName
                    )
                    cursor.execute(
                        "Insert Into TestCli_Xlog(Script,Started,Elapsed,"
                        "CommandType, Command, CommandStatus,"
                        "ErrorCode, WorkerName, SuiteName, CaseName,"
                        "ScenarioId, TestRunId, ScenarioName) "
                        "Values(?,?,?, ?,?,?,  ?,?,?,?, ?,?,?)",
                        data
                    )
                cursor.close()
                self.xlogFileHandle.commit()
            self.xlogFileHandle.close()

            # 如果有失败信息，则打印错误消息，直接退出
            if len(failureMessages) != 0:
                print(failureMessages)
            if exitCode != 0:
                raise ExecutionFailed(
                    message="Test failed. Please check more information.",
                    continue_on_failure=self.__BreakWithError
                )
        except ExecutionFailed as ex:
            raise RuntimeError("TEST Execute failed. " + str(ex.message))
        except Exception as ex:
            logger.info('str(e):  ', str(ex))
            logger.info('repr(e):  ', repr(ex))
            logger.info('traceback.print_exc():\n%s' % traceback.print_exc())
            logger.info('traceback.format_exc():\n%s' % traceback.format_exc())
            raise RuntimeError("TEST Execute failed.")
