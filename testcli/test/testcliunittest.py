# -*- coding: utf-8 -*-
import json
import time
import unittest
import os
import jpype
import tempfile
from testcli.sqlparse import SQLAnalyze
from testcli.apiparse import APIAnalyze
from testcli.testcli import TestCli
from testcli.compare import POSIXCompare
from testcli.sqlclijdbc import connect as jdbcconnect


class TestSynatx(unittest.TestCase):
    def test_SQLAnalyze_ConnectLocalMem(self):
        (isFinished, ret_CommandSplitResult, _, _, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("connect /mem")
        self.assertTrue(isFinished)
        self.assertEqual({'localService': 'mem', 'name': 'CONNECT'}, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_ConnectLocalMeta(self):
        (isFinished, ret_CommandSplitResult, _, _, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("connect /metadata")
        self.assertTrue(isFinished)
        self.assertEqual({'localService': 'metadata', 'name': 'CONNECT'}, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_ConnectWithoutServer(self):
        (isFinished, ret_CommandSplitResult, _, _, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("connect admin/123456")
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'CONNECT',
                          'password': '123456',
                          'username': 'admin'
                          }, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_ConnectOracle8(self):
        (isFinished, ret_CommandSplitResult, _, _, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("connect \"工具人1号\"/123456@jdbc:oracle:thin://192.168.1.72:1521:xe")
        self.assertTrue(isFinished)
        self.assertEqual({'driver': 'jdbc',
                          'driverSchema': 'oracle',
                          'driverType': 'thin',
                          'host': '192.168.1.72',
                          'name': 'CONNECT',
                          'password': '123456',
                          'port': 1521,
                          'username': '"工具人1号"',
                          'service': 'xe'
                          }, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_ConnectOracle11(self):
        (isFinished, ret_CommandSplitResult, _, _, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("connect system/123456@jdbc:oracle:thin://192.168.1.72:1521/xe")
        self.assertTrue(isFinished)
        self.assertEqual({'driver': 'jdbc',
                          'driverSchema': 'oracle',
                          'driverType': 'thin',
                          'host': '192.168.1.72',
                          'name': 'CONNECT',
                          'password': '123456',
                          'port': 1521,
                          'service': 'xe',
                          'username': 'system'}, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_ConnectTeradata(self):
        (isFinished, ret_CommandSplitResult, _, _, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("connect testdblink/testdblink@jdbc:teradata://192.168.1.136/testbase")
        self.assertTrue(isFinished)
        self.assertEqual({'driver': 'jdbc',
                          'driverSchema': 'teradata',
                          'host': '192.168.1.136',
                          'name': 'CONNECT',
                          'password': 'testdblink',
                          'service': 'testbase',
                          'username': 'testdblink'}, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_ConnectH2Mem(self):
        (isFinished, ret_CommandSplitResult, _, _, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("connect sa/sa@jdbc:h2tcp:tcp://127.0.0.1:19091/mem:test")
        self.assertTrue(isFinished)
        self.assertEqual({'driver': 'jdbc',
                          'driverSchema': 'h2tcp',
                          'driverType': 'tcp',
                          'host': '127.0.0.1',
                          'name': 'CONNECT',
                          'password': 'sa',
                          'port': 19091,
                          'service': 'mem:test',
                          'username': 'sa'}, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_ExitWithCode(self):
        (isFinished, ret_CommandSplitResult, _, _, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("exit 3")
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'EXIT',
                          'exitValue': 3}, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_ExitWithoutCode(self):
        (isFinished, ret_CommandSplitResult, _, _, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("exit ")
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'EXIT',
                          'exitValue': 0}, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_QuitWithCode(self):
        (isFinished, ret_CommandSplitResult, _, _, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("quit 3")
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'QUIT',
                          'exitValue': 3}, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_QuitWithoutCode(self):
        (isFinished, ret_CommandSplitResult, _, _, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("quit ")
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'QUIT',
                          'exitValue': 0}, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_Disconnect(self):
        (isFinished, ret_CommandSplitResult, _, _, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("disconnect")
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'DISCONNECT'}, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_Assert(self):
        (isFinished, ret_CommandSplitResult, _, _, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("Assert {% assert expresssion %}")
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'ASSERT', 'expression': ' assert expresssion '}, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_Set(self):
        (isFinished, ret_CommandSplitResult, _, _, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("set")
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'SET', 'scope': 'local'}, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_SetVariable(self):
        (isFinished, ret_CommandSplitResult, _, _, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("set @aa bbb")
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'SET',
                          'scope': 'global',
                          'optionName': 'aa',
                          'optionValue': 'bbb'}, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_Set2Parameter(self):
        (isFinished, ret_CommandSplitResult, _, _, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("set XX YY")
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'SET',
                          'optionName': 'XX',
                          'optionValue': 'YY',
                          'scope': 'local'}, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_Set3Parameter(self):
        (isFinished, ret_CommandSplitResult, _, _, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("set ZZ DD FF")
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'SET',
                          'optionName': 'ZZ',
                          'optionValue': 'DD FF',
                          'scope': 'local'
                          }, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_Sleep(self):
        (isFinished, ret_CommandSplitResult, _, _, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("sleep 3")
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'SLEEP', 'sleepTime': 3}, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_CommitAndRollback(self):
        (isFinished, ret_CommandSplitResult, _, _, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("commit")
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'COMMIT', 'statement': 'commit'}, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

        (isFinished, ret_CommandSplitResult, _, _, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("rollback")
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'ROLLBACK', 'statement': 'rollback'}, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_Echo(self):
        strEchoContent = "aaa" + "\n" + \
                         "bbb" + "\n" + \
                         "-- fasdfads" + "\n" + \
                         "# fdsfdasfdsafdsa"
        strEcho = "echo aa.txt \n" + strEchoContent + "\n" + "echo off"
        (isFinished, ret_CommandSplitResult, _, _, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze(strEcho)
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'ECHO',
                          'param': 'aa.txt',
                          'block': strEchoContent
                          }, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_Select(self):
        (isFinished, ret_CommandSplitResult, _, _, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("Select 1+2 from dual;")
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'SELECT',
                          'statement': 'Select 1+2 from dual',
                          }, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_SelectNotFinish(self):
        (isFinished, ret_CommandSplitResult, _, _, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("Select 1+2 from dual")
        self.assertFalse(isFinished)
        self.assertEqual('SELECT', ret_CommandSplitResult["name"])
        self.assertEqual(1, ret_errorCode)
        self.assertEqual("missing SQL_END at '<EOF>'", ret_errorMsg)

    def test_SQLAnalyze_SelectWithSlash(self):
        (isFinished, ret_CommandSplitResult, _, _, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("Select 1+2 from dual\n/")
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'SELECT', 'statement': 'Select 1+2 from dual'}, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_SelectMultiLine(self):
        (isFinished, ret_CommandSplitResult, _, _, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("Select 1+2,\n 3+4 \n from dual\n/")
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'SELECT', 'statement': 'Select 1+2,\n 3+4 \n from dual'}, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_USERAPI(self):
        (isFinished, ret_CommandSplitResult, _, _, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("use api")
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'USE', 'nameSpace': 'API'}, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_USERSQL(self):
        (isFinished, ret_CommandSplitResult, _, _, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("use sql")
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'USE', 'nameSpace': 'SQL'}, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_USERXXX(self):
        (isFinished, ret_CommandSplitResult, _, _, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("use XXX")
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'USE', 'nameSpace': None}, ret_CommandSplitResult)
        self.assertEqual(1, ret_errorCode)
        self.assertEqual("line1:4  mismatched input 'XXX' expecting {'API', 'SQL'}", ret_errorMsg.strip())

    def test_SQLAnalyze_CreateProcedure(self):
        (isFinished, ret_CommandSplitResult, _, _, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("Create Procedure proc \n test ..;\n/")
        self.assertTrue(isFinished)
        self.assertEqual(
            {'name': 'PROCEDURE', 'statement': 'Create Procedure proc \n test ..;'},
            ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_Start(self):
        (isFinished, ret_CommandSplitResult, _, _, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("start c:\\abcd\\defg.sql")
        self.assertTrue(isFinished)
        self.assertEqual(
            {'loopTimes': 1, 'name': 'START', 'scriptList': ['c:\\abcd\\defg.sql']},
            ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_Declare(self):
        (isFinished, ret_CommandSplitResult, _, _, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("Declare Begin xxx \n end;\n/")
        self.assertTrue(isFinished)
        self.assertEqual(
            {'name': 'DECLARE', 'statement': 'Declare Begin xxx \n end;'},
            ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_Begin(self):
        (isFinished, ret_CommandSplitResult, _, _, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("Begin xxx \n end;\n/")
        self.assertTrue(isFinished)
        self.assertEqual(
            {'name': 'BEGIN', 'statement': 'Begin xxx \n end;'},
            ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_Spool(self):
        (isFinished, ret_CommandSplitResult, _, _, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("Spool aa.txt")
        self.assertTrue(isFinished)
        self.assertEqual(
            {'file': 'aa.txt', 'name': 'SPOOL'},
            ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

        (isFinished, ret_CommandSplitResult, _, _, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("Spool off")
        self.assertTrue(isFinished)
        self.assertEqual(
            {'file': 'off', 'name': 'SPOOL'},
            ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_Script(self):
        scriptHeader = "> {%\n"
        script = "Hello World"
        scriptEnd = "\n%}\n"
        (isFinished, ret_CommandSplitResult, _, _, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze(scriptHeader + script + scriptEnd)
        self.assertTrue(isFinished)
        self.assertEqual(
            {'block': script, 'name': 'SCRIPT'},
            ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_Session(self):
        (isFinished, ret_CommandSplitResult, _, _, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("Session save xxx")
        self.assertTrue(isFinished)
        self.assertEqual(
            {'action': 'SAVE', 'name': 'SESSION', 'sessionName': 'xxx'},
            ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

        (isFinished, ret_CommandSplitResult, _, _, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("Session release xxx")
        self.assertTrue(isFinished)
        self.assertEqual(
            {'action': 'RELEASE', 'name': 'SESSION', 'sessionName': 'xxx'},
            ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

        (isFinished, ret_CommandSplitResult, _, _, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("Session restore xxx")
        self.assertTrue(isFinished)
        self.assertEqual(
            {'action': 'RESTORE', 'name': 'SESSION', 'sessionName': 'xxx'},
            ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

        (isFinished, ret_CommandSplitResult, _, _, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("Session saveurl xxx")
        self.assertTrue(isFinished)
        self.assertEqual(
            {'action': 'SAVEURL', 'name': 'SESSION', 'sessionName': 'xxx'},
            ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

        (isFinished, ret_CommandSplitResult, _, _, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("Session show xxx")
        self.assertTrue(isFinished)
        self.assertEqual(
            {'action': 'SHOW', 'name': 'SESSION', 'sessionName': 'xxx'},
            ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

        (isFinished, ret_CommandSplitResult, _, _, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("Session yyy xxx")
        self.assertTrue(isFinished)
        self.assertEqual(
            {'action': '', 'name': 'SESSION', 'sessionName': 'yyy'},
            ret_CommandSplitResult)
        self.assertEqual(1, ret_errorCode)
        self.assertEqual("line1:12  extraneous input 'xxx' expecting <EOF> ", ret_errorMsg)

    def test_SQLExecute(self):
        scriptFile = "testsqlsanity.sql"

        scriptBaseFile = os.path.splitext(scriptFile)[0]
        fullScriptFile = os.path.abspath(os.path.join(os.path.dirname(__file__), "", scriptFile))
        fullRefFile = os.path.abspath(os.path.join(os.path.dirname(__file__), "", scriptBaseFile + ".ref"))
        fullLogFile = os.path.abspath(os.path.join(tempfile.gettempdir(), scriptBaseFile + ".log"))

        # 运行测试程序，开启无头模式(不再控制台上显示任何内容),同时不打印Logo
        testcli = TestCli(
            logfilename=fullLogFile,
            HeadlessMode=True,
            nologo=True,
            script=fullScriptFile
        )
        retValue = testcli.run_cli()
        # 脚本中包含了Exit的字样，所以判断是否等于exitValue （3）
        self.assertEqual(3, retValue)

        # 对文件进行比对，判断返回结果是否吻合
        compareHandler = POSIXCompare()
        compareResult, compareReport = compareHandler.compare_text_files(
            file1=fullLogFile,
            file2=fullRefFile,
            CompareIgnoreTailOrHeadBlank=True
        )
        if not compareResult:
            for line in compareReport:
                if line.startswith("-") or line.startswith("+"):
                    print(line)
        self.assertTrue(compareResult)

    def test_SQLExecuteWithSQLCLI_CONNECTION_URL(self):
        h2JarFile = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "jlib", "h2-1.4.200.jar"))
        jarList = [h2JarFile, ]
        jdbcconnect(jclassname="org.h2.Driver",
                    url="jdbc:h2:mem:test;TRACE_LEVEL_SYSTEM_OUT=0;TRACE_LEVEL_FILE=0",
                    driverArgs={'user': 'sa', 'password': 'sa'},
                    jars=jarList)
        tcpServer = jpype.JClass("org.h2.tools.Server").\
            createTcpServer("-tcp", "-tcpAllowOthers", "-tcpPort", str(19091))
        tcpServer.start()
        os.environ["SQLCLI_CONNECTION_URL"] = "jdbc:h2tcp:tcp://127.0.0.1:19091/mem:test"

        scriptFile = "testsqlwithurl.sql"
        scriptBaseFile = os.path.splitext(scriptFile)[0]
        fullScriptFile = os.path.abspath(os.path.join(os.path.dirname(__file__), "", scriptFile))
        fullRefFile = os.path.abspath(os.path.join(os.path.dirname(__file__), "", scriptBaseFile + ".ref"))
        fullLogFile = os.path.abspath(os.path.join(tempfile.gettempdir(), scriptBaseFile + ".log"))

        # 运行测试程序，开启无头模式(不再控制台上显示任何内容),同时不打印Logo
        testcli = TestCli(
            logfilename=fullLogFile,
            HeadlessMode=True,
            nologo=True,
            script=fullScriptFile
        )
        retValue = testcli.run_cli()
        self.assertEqual(0, retValue)

        tcpServer.stop()
        tcpServer.shutdown()

        # 对文件进行比对，判断返回结果是否吻合
        compareHandler = POSIXCompare()
        compareResult, compareReport = compareHandler.compare_text_files(
            file1=fullLogFile,
            file2=fullRefFile,
            CompareIgnoreTailOrHeadBlank=True
        )
        if not compareResult:
            for line in compareReport:
                if line.startswith("-") or line.startswith("+"):
                    print(line)
        self.assertTrue(compareResult)

    def test_SQLSleep(self):
        # 记录开始时间
        start = time.time()

        scriptFile = "testsqlsleep.sql"

        scriptBaseFile = os.path.splitext(scriptFile)[0]
        fullScriptFile = os.path.abspath(os.path.join(os.path.dirname(__file__), "", scriptFile))
        fullRefFile = os.path.abspath(os.path.join(os.path.dirname(__file__), "", scriptBaseFile + ".ref"))
        fullLogFile = os.path.abspath(os.path.join(tempfile.gettempdir(), scriptBaseFile + ".log"))

        # 运行测试程序，开启无头模式(不再控制台上显示任何内容),同时不打印Logo
        testcli = TestCli(
            logfilename=fullLogFile,
            HeadlessMode=True,
            nologo=True,
            script=fullScriptFile
        )
        retValue = testcli.run_cli()
        self.assertEqual(0, retValue)

        # 记录截止时间
        end = time.time()
        self.assertTrue((end - start) > 1)

        # 对文件进行比对，判断返回结果是否吻合
        compareHandler = POSIXCompare()
        compareResult, compareReport = compareHandler.compare_text_files(
            file1=fullLogFile,
            file2=fullRefFile,
            CompareIgnoreTailOrHeadBlank=True
        )
        if not compareResult:
            for line in compareReport:
                if line.startswith("-") or line.startswith("+"):
                    print(line)
        self.assertTrue(compareResult)

    def test_SQLEmbeddScript(self):
        scriptFile = "testsqlembeddscript.sql"

        scriptBaseFile = os.path.splitext(scriptFile)[0]
        fullScriptFile = os.path.abspath(os.path.join(os.path.dirname(__file__), "", scriptFile))
        fullRefFile = os.path.abspath(os.path.join(os.path.dirname(__file__), "", scriptBaseFile + ".ref"))
        fullLogFile = os.path.abspath(os.path.join(tempfile.gettempdir(), scriptBaseFile + ".log"))

        # 运行测试程序，开启无头模式(不再控制台上显示任何内容),同时不打印Logo
        testcli = TestCli(
            logfilename=fullLogFile,
            HeadlessMode=True,
            nologo=True,
            script=fullScriptFile
        )
        retValue = testcli.run_cli()
        self.assertEqual(0, retValue)

        # 对文件进行比对，判断返回结果是否吻合
        compareHandler = POSIXCompare()
        compareResult, compareReport = compareHandler.compare_text_files(
            file1=fullLogFile,
            file2=fullRefFile,
            CompareIgnoreTailOrHeadBlank=True
        )
        if not compareResult:
            for line in compareReport:
                if line.startswith("-") or line.startswith("+"):
                    print(line)
        self.assertTrue(compareResult)

    def test_SQLSessionManage(self):
        scriptFile = "testsessionmanage.sql"

        scriptBaseFile = os.path.splitext(scriptFile)[0]
        fullScriptFile = os.path.abspath(os.path.join(os.path.dirname(__file__), "", scriptFile))
        fullRefFile = os.path.abspath(os.path.join(os.path.dirname(__file__), "", scriptBaseFile + ".ref"))
        fullLogFile = os.path.abspath(os.path.join(tempfile.gettempdir(), scriptBaseFile + ".log"))

        # 运行测试程序，开启无头模式(不再控制台上显示任何内容),同时不打印Logo
        testcli = TestCli(
            logfilename=fullLogFile,
            HeadlessMode=True,
            nologo=True,
            script=fullScriptFile
        )
        retValue = testcli.run_cli()
        self.assertEqual(0, retValue)

        # 对文件进行比对，判断返回结果是否吻合
        compareHandler = POSIXCompare()
        compareResult, compareReport = compareHandler.compare_text_files(
            file1=fullLogFile,
            file2=fullRefFile,
            CompareIgnoreTailOrHeadBlank=True
        )
        if not compareResult:
            for line in compareReport:
                if line.startswith("-") or line.startswith("+"):
                    print(line)
        self.assertTrue(compareResult)

    def test_APIAnalyze_MultiPart(self):
        scriptFile = "testapisynatx-multipart.api"

        scriptBaseFile = os.path.splitext(scriptFile)[0]
        fullScriptFile = os.path.abspath(os.path.join(os.path.dirname(__file__), "", scriptFile))
        fullRefFile = os.path.abspath(os.path.join(os.path.dirname(__file__), "", scriptBaseFile + ".ref"))
        fullLogFile = os.path.abspath(os.path.join(tempfile.gettempdir(), scriptBaseFile + ".log"))

        scriptFileHandler = open(fullScriptFile, "r")
        script = "".join(scriptFileHandler.readlines())
        scriptFileHandler.close()

        (isFinished, ret_CommandSplitResult, _, _, ret_errorCode, ret_errorMsg) \
            = APIAnalyze(script)
        self.assertTrue(isFinished)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

        data = json.dumps(obj=ret_CommandSplitResult,
                          sort_keys=True,
                          indent=4,
                          separators=(',', ': '),
                          ensure_ascii=False)
        logFileHandler = open(fullLogFile, "w")
        logFileHandler.write(data)
        logFileHandler.close()

        # 对文件进行比对，判断返回结果是否吻合
        compareHandler = POSIXCompare()
        compareResult, compareReport = compareHandler.compare_text_files(
            file1=fullLogFile,
            file2=fullRefFile,
            CompareIgnoreTailOrHeadBlank=True
        )
        if not compareResult:
            for line in compareReport:
                if line.startswith("-") or line.startswith("+"):
                    print(line)
        self.assertTrue(compareResult)

    def test_APIAnalyze_Get(self):
        scriptFile = "testapisynatx-get.api"

        scriptBaseFile = os.path.splitext(scriptFile)[0]
        fullScriptFile = os.path.abspath(os.path.join(os.path.dirname(__file__), "", scriptFile))
        fullRefFile = os.path.abspath(os.path.join(os.path.dirname(__file__), "", scriptBaseFile + ".ref"))
        fullLogFile = os.path.abspath(os.path.join(tempfile.gettempdir(), scriptBaseFile + ".log"))

        scriptFileHandler = open(fullScriptFile, "r")
        script = "".join(scriptFileHandler.readlines())
        scriptFileHandler.close()

        (isFinished, ret_CommandSplitResult, _, _, ret_errorCode, ret_errorMsg) \
            = APIAnalyze(script)
        self.assertTrue(isFinished)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

        data = json.dumps(obj=ret_CommandSplitResult,
                          sort_keys=True,
                          indent=4,
                          separators=(',', ': '),
                          ensure_ascii=False)
        logFileHandler = open(fullLogFile, "w")
        logFileHandler.write(data)
        logFileHandler.close()

        # 对文件进行比对，判断返回结果是否吻合
        compareHandler = POSIXCompare()
        compareResult, compareReport = compareHandler.compare_text_files(
            file1=fullLogFile,
            file2=fullRefFile,
            CompareIgnoreTailOrHeadBlank=True
        )
        if not compareResult:
            for line in compareReport:
                if line.startswith("-") or line.startswith("+"):
                    print(line)
        self.assertTrue(compareResult)


if __name__ == '__main__':
    unittest.main()
