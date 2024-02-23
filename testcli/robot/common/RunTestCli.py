# -*- coding: UTF-8 -*-
import json
import os
import sys
import html
import traceback
from robot.api import logger
from robot.errors import ExecutionFailed
from robot.running.context import EXECUTION_CONTEXTS


class TestCliContinuableError(RuntimeError):
    # 即使当前测试执行失败，也要继续运行下去。不退出
    ROBOT_CONTINUE_ON_FAILURE = True


class TestCliFatalError(RuntimeError):
    # 若当前测试执行失败，不再继续运行后面的关键字
    ROBOT_CONTINUE_ON_FAILURE = False


class RunTestCli(object):
    # TEST SUITE 在suite中引用，只会实例化一次
    # 也就是说多test case都引用了这个类的方法，但是只有第一个test case调用的时候实例化
    # 如果一个Suite多个Case引用设置类的方法，要注意先后的影响
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    __BreakWithError = False                # 是否遇到错误就退出，默认是不退出
    __EnableConsoleOutPut = False           # 是否关闭在Console上的显示，默认是不关闭
    __enableExtendLog = False               # 是否打开扩展的日志记录，默认是不打开
    __CommandMapping = None                 # 映射文件列表
    __failWithAssertOrScriptError = False   # 是否在遇到Assert或者Script错误的时候，就认为脚本运行失败。默认不严格判断
    __clientCharSet = "UTF-8"               # 设置客户端输入字符集
    __resultCharSet = "UTF-8"               # 设置客户端输出字符集

    def TestCli_Set_ClientCharset(self, p_ClientCharset):
        """ 设置脚本执行时候的客户端输入字符集  """
        """
        输入参数：
             p_ClientCharset:        任何有效的字符集，如UTF-8,GBK
        返回值：
            无
        """
        self.__clientCharSet = p_ClientCharset

    def TestCli_Set_ResultCharset(self, p_ResultCharset):
        """ 设置脚本执行时候的客户端输出字符集  """
        """
        输入参数：
             p_ResultCharset:        任何有效的字符集，如UTF-8,GBK
        返回值：
            无
        """
        self.__resultCharSet = p_ResultCharset

    def TestCli_Break_When_Error(self, p_BreakWithError):
        """ 设置是否在遇到错误的时候中断该Case的后续运行  """
        """
        输入参数：
             p_BreakWithError:        是否在遇到错误的时候中断，默认为不中断
        返回值：
            无

        如果设置为True，则TestCli运行会中断，Case会被判断执行失败
        如果设置为False，则TestCli运行不会中断，运行结果文件中有错误信息，供参考
        """
        if str(p_BreakWithError).upper() == 'TRUE':
            self.__BreakWithError = True
        if str(p_BreakWithError).upper() == 'FALSE':
            self.__BreakWithError = False

    def TestCli_Enable_ExtendLog(self, enableExtendLog):
        """ 设置是否额外的扩展日志，默认是不启用  """
        """
        输入参数：
             enableExtendLog:    是否启用额外的扩展日志，默认是不启用
        返回值：
            无

        如果设置为True，则所有命令操作都会记录在一个扩展的日志文件中
        """
        if str(enableExtendLog).upper() == 'TRUE':
            self.__enableExtendLog = True
        if str(enableExtendLog).upper() == 'FALSE':
            self.__enableExtendLog = False

    def TestCli_Enable_ConsoleOutput(self, p_ConsoleOutput):
        """ 设置是否在在屏幕上显示SQL的执行过程  """
        """
        输入参数：
             p_ConsoleOutput:        是否在在屏幕上显示SQL的执行过程， 默认是不显示
        返回值：
            无

        如果设置为True，则所有SQL执行的过程不仅仅会记录在日之内，也会显示在控制台上
        如果设置为False，则所有SQL执行的过程仅仅会记录在日之内，不会显示在控制台上
        """
        if str(p_ConsoleOutput).upper() == 'TRUE':
            self.__EnableConsoleOutPut = True
        if str(p_ConsoleOutput).upper() == 'FALSE':
            self.__EnableConsoleOutPut = False

    def TestCli_Set_CommandMapping(self, p_szCommandMapping):
        """ 设置CommandMapping文件  """
        """
        输入参数：
             p_szCommandMapping:      CommandMapping文件，如果包括多个文件，用，分割
        返回值：
            无
        """
        self.__CommandMapping = p_szCommandMapping

    def Logon_And_Execute_TestCli_Script(self, logonString, scriptFileName, logFileName=None):
        self.Logon_And_Execute_TestCli_Script_With_Reference(
            logonString=logonString,
            scriptFileName=scriptFileName,
            logFileName=logFileName,
            referenceFileName=None
        )

    def Execute_TestCli_Script(self, scriptFileName, logFileName=None):
        """ 执行TEST脚本  """
        """
        输入参数：
            p_szScript_FileName         脚本文件名称
            p_szLogOutPutFileName       结果日志文件名称, 如果没有提供，则默认和脚本同名的.log文件
        输出参数：
            无
        例子：
            Execute Test Script         test.sql test.log
        """
        self.Execute_TestCli_Script_With_Reference(
            scriptFileName=scriptFileName,
            logFileName=logFileName,
            referenceFileName=None
        )

    def Logon_And_Execute_TestCli_Script_With_Reference(
            self,
            logonString,
            scriptFileName,
            logFileName=None,
            referenceFileName=None
    ):
        """ 执行TEST脚本  """
        """
        输入参数：
            logonString                连接用户名，口令； 如果LogonString为N/A，则不运行相关操作
            p_szScript_FileName            脚本文件名称
            p_szLogOutPutFileName          结果日志文件名称, 如果没有提供，则默认和脚本同名的.log文件
        输出参数：
            无
        例子：
            Logon And Execute TEST Script     admin/123456 test.sql test.log
            Logon And Execute TEST Script     admin/123456 test.api test.log
        """
        # 记录当前目录，执行完后用来还原
        current_dir = os.getcwd()
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
            # 如果Log目录不存在，则创建Log目录
            if not os.path.exists(os.path.dirname(logOutPutFullFileName)):
                os.makedirs(os.path.dirname(logOutPutFullFileName))

            # ExtendLog文件默认存放在log文件目录下
            if self.__enableExtendLog:
                if "T_WORK" in os.environ:
                    xlogFileName = os.path.basename(scriptFileName).split('.')[0] + ".xdb"
                    xlogFullFileName = os.path.join(os.environ["T_WORK"], xlogFileName)
                else:
                    xlogFileName = os.path.basename(scriptFileName).split('.')[0] + ".xdb"
                    xlogFullFileName = os.path.join(os.getcwd(), xlogFileName)
            else:
                xlogFullFileName = None
            if referenceFileName is not None:
                if "T_WORK" in os.environ:
                    rptFileName = os.path.basename(logFileName).split('.')[0] + ".rpt"
                    rptFullFileName = os.path.join(os.environ["T_WORK"], rptFileName)
                else:
                    rptFileName = os.path.basename(logFileName).split('.')[0] + ".rpt"
                    rptFullFileName = os.path.join(os.getcwd(), rptFileName)
            else:
                rptFullFileName = None

            logger.info('<b>===== Execute</b>     [' + scriptFileName + ']', html=True)
            logger.info('<b>===== LogFile</b>     [' + str(logOutPutFullFileName) + ']', html=True)
            logger.info('<b>===== Reference</b>   [' + str(referenceFileName) + ']', html=True)
            logger.info('<b>===== ScenarioRpt</b> [' + str(rptFullFileName) + ']', html=True)
            logger.info('<b>===== BreakMode</b>   [' + str(self.__BreakWithError) + ']', html=True)
            logger.info('<b>===== SQLMAP1</b>     [' + str(self.__CommandMapping) + ']', html=True)
            logger.info('<b>===== SQLMAP2</b>     [' + str(os.environ.get("SQLCLI_SQLMAPPING")) + ']', html=True)
            logger.info('<b>===== Logon</b>       [' + str(logonString) + ']', html=True)

            sys.__stdout__.write('\n')  # 打印一个空行，好保证在Robot上Console显示不错行
            sys.__stdout__.write('===== Execute     [' + scriptFileName + ']\n')
            sys.__stdout__.write('===== LogFile     [' + logOutPutFullFileName + ']\n')
            sys.__stdout__.write('===== Reference   [' + str(referenceFileName) + ']\n')
            sys.__stdout__.write('===== ScenarioRpt [' + str(rptFullFileName) + ']\n',)
            sys.__stdout__.write('===== BreakMode   [' + str(self.__BreakWithError) + ']\n')
            sys.__stdout__.write('===== SQLMAP1     [' + str(self.__CommandMapping) + ']\n')
            sys.__stdout__.write('===== SQLMAP2     [' + str(os.environ.get("SQLCLI_SQLMAPPING")) + ']\n')

            sys.__stdout__.write('===== Starting .....\n')
            sys.__stdout__.flush()
            if not self.__EnableConsoleOutPut:
                myConsole = None
                myHeadLessMode = True
                mylogger = None
            else:
                myConsole = sys.__stdout__
                myHeadLessMode = False
                mylogger = logger
            if EXECUTION_CONTEXTS.current is None:
                m_SuiteName = "--------"
                m_TestName = "--------"
            else:
                m_SuiteName = str(EXECUTION_CONTEXTS.current.suite)
                if hasattr(EXECUTION_CONTEXTS.current.test, "name"):
                    m_TestName = str(EXECUTION_CONTEXTS.current.test.name)
                else:
                    m_TestName = "--------"  # Setup Or TearDown

            logger.info('<b>===== Script</b>    [' + str(scriptFileName) + '] ', html=True)
            if scriptFileName.endswith("sql"):
                nameSpace = "SQL"
            elif scriptFileName.endswith("api"):
                nameSpace = "API"
            else:
                nameSpace = "N/A"

            # 将当前路径作为系统的Moule路径
            packagePath = str(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../.."))
            if packagePath not in sys.path:
                sys.path.append(packagePath)
            modulePath = str(os.path.dirname(os.path.realpath(__file__)))
            if modulePath not in sys.path:
                sys.path.append(modulePath)
            from testcli.testcli import TestCli

            # 如果存在之前的扩展日志，则先删除文件
            if os.path.exists(xlogFullFileName):
                os.unlink(xlogFullFileName)

            # 运行TestCli
            cli = TestCli(logon=logonString,
                          script=scriptFileName,
                          logfilename=logOutPutFullFileName,
                          referenceFile=referenceFileName,
                          Console=myConsole,
                          headlessMode=myHeadLessMode,
                          namespace=nameSpace,
                          logger=mylogger,
                          commandMap=self.__CommandMapping,
                          breakWithError=self.__BreakWithError,
                          clientCharset=self.__clientCharSet,
                          resultCharset=self.__resultCharSet,
                          xlog=xlogFullFileName,
                          xlogoverwrite=False,
                          suitename=m_SuiteName,
                          casename=m_TestName)
            sys.__stdout__.write('===== Start TestCli [' + str(cli.version) +
                                 '] with script [' + str(scriptFileName) + '] \n')
            sys.__stdout__.flush()
            logger.info('<b>===== Start TestCli [' + str(cli.version) +
                        '] with script</b> [' + str(scriptFileName) + '] ', html=True)
            if not self.__EnableConsoleOutPut:
                logger.info('  ... suppressed testcli console output ...')
                logger.info("  ... you can enable testcli console output "
                            "with \"TestCli Enable ConsoleOutput    True|False\" ...")
            cliResult = cli.run_cli()

            # 判断运行结果，先假设运行是成功的，如果发现错误信息，则标记为失败
            if cliResult == 0:
                testSuccessful = True
            else:
                testSuccessful = False

            if rptFullFileName is not None:
                # 读取rpt信息，包含了详细的运行情况报告
                logger.info("<b>>>>>>>>>>>>>>>> Test Result Summary <<<<<<<<<<<<< </b>", html=True)
                logger.info("<b>SuiteName    :</b> [" + m_SuiteName + "]", html=True)
                logger.info("<b>CaseName     :</b> [" + m_TestName + "]", html=True)
                rptFileHandler = open(rptFullFileName, mode='r', encoding='UTF-8')
                rptResult = dict(json.load(rptFileHandler))
                rptFileHandler.close()
                for scenarioId, scenarioResult in rptResult.items():
                    if scenarioResult["Status"] != "Failed":
                        logger.info("<b>Scenario:[" + scenarioResult["Name"] + "]</b>", html=True)
                        logger.info("<b>Status: [<font color=\"green\">" + "Successful" + "</font>]</b>", html=True)
                    else:
                        testSuccessful = False  # 有失败的场景，那就标记为失败吧
                        logger.info("<b>Scenario:[" + scenarioResult["Name"] + "]</b>", html=True)
                        logger.info("<b>Status: [<font color=\"red\">" + "Failed" + "</font>]</b>", html=True)
                        for line in scenarioResult["Message"].split('\n'):
                            if line.startswith('-'):
                                logger.write('<font style="color:Black;background-color:#E0E0E0">' +
                                             html.escape(line[0:7]) + '</font>' +
                                             '<font style="color:white;background-color:Red">' +
                                             html.escape(line[7:]) + '</font>',
                                             html=True)
                            elif line.startswith('+'):
                                logger.write('<font style="color:Black;background-color:#E0E0E0">' +
                                             html.escape(line[0:7]) + '</font>' +
                                             '<font style="color:white;background-color:Green">' +
                                             html.escape(line[7:]) + '</font>',
                                             html=True)
                            elif line.startswith('S'):
                                logger.write('<font style="color:Black;background-color:#E0E0E0">' +
                                             html.escape(line) + '</font>',
                                             html=True)
                            else:
                                logger.write('<font style="color:Black;background-color:#E0E0E0">' +
                                             html.escape(line[0:7]) + '</font>' +
                                             '<font style="color:Black;background-color:white">' +
                                             html.escape(line[7:]) + '</font>',
                                             html=True)
                    logger.info(r'<hr style="border:6 outset #ff0033" width="100%" SIZE=6>', html=True)
                logger.info("<b>>>>>>>>>>>>>>>> Test Result Summary <<<<<<<<<<<<< </b>", html=True)

            else:
                logger.info("<b>>>>>>>>>>>>>>>> Test Result Summary <<<<<<<<<<<<< </b>", html=True)
                logger.info("<b>SuiteName          :</b> [" + m_SuiteName + "]", html=True)
                logger.info("<b>CaseName           :</b> [" + m_TestName + "]", html=True)
                logger.info("<b>ScenarioResult     :</b> [N/A(No extend and reference log available.]", html=True)
                logger.info("<b>>>>>>>>>>>>>>>> Test Result Summary <<<<<<<<<<<<< </b>", html=True)

            logger.info('<b>===== End TestCli with result</b> [' + str(cliResult) + '] ', html=True)
            sys.__stdout__.write('===== End TestCli with result [' + str(cliResult) + '] \n')
            sys.__stdout__.flush()
            if self.__BreakWithError and (cliResult != 0) and not self.__EnableConsoleOutPut:
                # 如果日志信息少于30K，则全部打印
                # 只有在没有打印日志的时候，才有必要把最后的失败日志给打印出来，否则不打印
                m_Results = []
                with open(logOutPutFullFileName, "rb") as f:
                    size = f.seek(0, 2)
                    if size < 30 * 1024:  # 如果文件不足30K，则全部读入
                        # 回到文件开头
                        f.seek(0, 0)
                        for row in f.readlines():
                            m_Results.append(row.decode('utf-8'))
                    else:
                        # 回到文件开头
                        f.seek(0, 0)
                        m_ReadBuf = f.readlines(10 * 1024)
                        for row in m_ReadBuf[0:10]:
                            m_Results.append(row.decode('utf-8'))
                        m_Results.append(" .......................   ")
                        # 来到文件末尾
                        f.seek(- 20 * 1024, 2)
                        m_ReadBuf = f.readlines()
                        for row in m_ReadBuf[-30:]:
                            m_Results.append(row.decode('utf-8'))
                sys.__stdout__.write(' =====  Test Break with Error ========\n')
                logger.info(' =====  Test Break with Error ========')
                for row in m_Results:
                    sys.__stdout__.write(row)
                    logger.info(row.replace("\n", ""))
                logger.info(' =====  Test Break with Error ========')
                sys.__stdout__.write(' =====  Test Break with Error ========\n')
                sys.__stdout__.flush()
                raise RuntimeError("Test Execute failed.")

            # 运行失败，标记错误信息
            if not testSuccessful:
                raise ExecutionFailed(
                    message="Test failed. Please check dif file for more information.",
                    continue_on_failure=self.__BreakWithError
                )
        except RuntimeError as ex:
            raise ex
        except ExecutionFailed:
            # 根据标志判断退出的类型，决定后续的Case是否继续操作
            if self.__BreakWithError:
                raise TestCliFatalError()
            else:
                raise TestCliContinuableError()
        except Exception as ex:
            logger.info('str(e):  ', str(ex))
            logger.info('repr(e):  ', repr(ex))
            logger.info('traceback.print_exc():\n%s' % traceback.print_exc())
            logger.info('traceback.format_exc():\n%s' % traceback.format_exc())
            raise RuntimeError("TEST Execute failed.")
        finally:
            # 不能在Cli脚本内部切换目录，即使内部切换了，外部也必须变更回来
            os.chdir(current_dir)

    def Execute_TestCli_Script_With_Reference(
            self,
            scriptFileName,
            logFileName=None,
            referenceFileName=None
    ):
        """ 执行TEST脚本  """
        """
        输入参数：
            p_szScript_FileName         脚本文件名称
            p_szLogOutPutFileName       结果日志文件名称, 如果没有提供，则默认和脚本同名的.log文件
        输出参数：
            无
        例子：
            Execute Test Script         test.sql test.log
        """
        self.Logon_And_Execute_TestCli_Script_With_Reference(
            logonString=None,
            scriptFileName=scriptFileName,
            logFileName=logFileName,
            referenceFileName=referenceFileName,
        )
