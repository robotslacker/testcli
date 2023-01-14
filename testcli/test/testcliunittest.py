# -*- coding: utf-8 -*-
import json
import time
import unittest
import os
import jpype
import tempfile
from ..sqlparse import SQLAnalyze
from ..apiparse import APIAnalyze
from ..commands.compare import POSIXCompare
from ..sqlclijdbc import connect as jdbcconnect
from ..test.testmockserver import startServer
from ..test.testmockserver import stopServer
from ..test.testmockserver import waitServerRunning


class TestSynatx(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        startServer()
        waitServerRunning()

    @classmethod
    def tearDownClass(cls):
        stopServer()

    def test_SQLAnalyze_NullString(self):
        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("")
        self.assertTrue(isFinished)
        self.assertIsNone(ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_Connect(self):
        # connect with local h2 mem
        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_connect SYSDBA/Dameng123:62310jdbc:dm://10.15.1.19:6231/")
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'CONNECT', 'password': 'Dameng123', 'username': 'SYSDBA'}, ret_CommandSplitResult)
        self.assertEqual(1, ret_errorCode)
        self.assertEqual("line1:25  mismatched input ':62310' expecting <EOF> ", ret_errorMsg)

        # connect with local h2 mem
        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_connect /mem")
        self.assertTrue(isFinished)
        self.assertEqual({'localService': 'mem', 'name': 'CONNECT'}, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

        # Connect with testcli metadata
        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_connect /metadata")
        self.assertTrue(isFinished)
        self.assertEqual({'localService': 'metadata', 'name': 'CONNECT'}, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

        # connect without server url
        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_connect admin/123456")
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'CONNECT',
                          'password': '123456',
                          'username': 'admin'
                          }, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

        # Connect with Oracle8
        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_connect \"工具人1号\"/123456@jdbc:oracle:thin://192.168.1.72:1521:xe")
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

        # Connect with Oracle11
        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_connect system/123456@jdbc:oracle:thin://192.168.1.72:1521/xe")
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

        # connect with teradata
        # teradata与众不同，其没有serviceName的存在
        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_connect testdblink/testdblink@jdbc:teradata://192.168.1.136/testbase")
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

        # Connect with named h2 session
        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_connect sa/sa@jdbc:h2tcp:tcp://127.0.0.1:19091/mem:test")
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

        # Connect with IPV6
        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_connect sa/sa@jdbc:h2tcp:tcp://[0:0:0:0:0:ffff:192.1.56.10]:19091/mem:test")
        self.assertTrue(isFinished)
        self.assertEqual({'driver': 'jdbc',
                          'driverSchema': 'h2tcp',
                          'driverType': 'tcp',
                          'host': '[0:0:0:0:0:ffff:192.1.56.10]',
                          'name': 'CONNECT',
                          'password': 'sa',
                          'port': 19091,
                          'service': 'mem:test',
                          'username': 'sa'}, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

        # Connect with IPV6
        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_connect sa/sa@jdbc:h2tcp:tcp://[FE80::5689:98FF:FE14]:19091/mem:test")
        self.assertTrue(isFinished)
        self.assertEqual({'driver': 'jdbc',
                          'driverSchema': 'h2tcp',
                          'driverType': 'tcp',
                          'host': '[FE80::5689:98FF:FE14]',
                          'name': 'CONNECT',
                          'password': 'sa',
                          'port': 19091,
                          'service': 'mem:test',
                          'username': 'sa'}, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_Load(self):
        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_load plugin aaa")
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'LOAD', 'option': 'PLUGIN', 'pluginFile': 'aaa'}, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_load jdbcdriver name=oracle "
                         "class=oracle.jdbc.driver.OracleDriver file='d:\\temp\\aa.txt' "
                         "url='jdbc:oracle:thin:@${host}:${port}/${service}' "
                         "props='aaa,bbb'")
        self.assertTrue(isFinished)
        self.assertEqual(
            {'driverClass': 'oracle.jdbc.driver.OracleDriver',
             'driverFile': 'd:\\temp\\aa.txt',
             'driverName': 'oracle',
             'driverProps': 'aaa,bbb',
             'driverURL': 'jdbc:oracle:thin:@${host}:${port}/${service}',
             'name': 'LOAD',
             'option': 'JDBCDRIVER'
             },
            ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_load map '/abcd/efg/aa.txt' ")
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'LOAD', 'option': 'MAP', 'mapFile': '/abcd/efg/aa.txt'}, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_ExitWithCode(self):
        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_exit 3")
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'EXIT',
                          'exitValue': 3}, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = APIAnalyze("_exit 3")
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'EXIT',
                          'exitValue': 3}, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_ExitWithoutCode(self):
        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_exit ")
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'EXIT',
                          'exitValue': 0}, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_QuitWithCode(self):
        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_quit 3")
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'QUIT',
                          'exitValue': 3}, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_QuitWithoutCode(self):
        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_quit ")
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'QUIT',
                          'exitValue': 0}, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_Disconnect(self):
        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_disconnect")
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'DISCONNECT'}, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_Assert(self):
        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_Assert {% assert expresssion %}")
        self.assertTrue(isFinished)
        self.assertEqual(
            {
                'assertName': None,
                'name': 'ASSERT',
                'expression': ' assert expresssion '
            },
            ret_CommandSplitResult)
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)

    def test_SQLAnalyze_Set(self):
        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_set")
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'SET'}, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_SetVariable(self):
        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_set @aa bbb")
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'SET',
                          'optionName': '@aa',
                          'optionValue': 'bbb'}, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_Set2Parameter(self):
        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_set XX YY")
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'SET',
                          'optionName': 'XX',
                          'optionValue': 'YY'}, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_Set3Parameter(self):
        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_set ZZ DD FF")
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'SET',
                          'optionName': 'ZZ',
                          'optionValue': 'DD FF'
                          }, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_Sleep(self):
        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_sleep 3")
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'SLEEP', 'sleepTime': 3}, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_CommitAndRollback(self):
        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("commit")
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'COMMIT', 'statement': 'commit'}, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
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
        strEcho = "_echo aa.txt \n" + strEchoContent + "\n" + "echo off"
        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze(strEcho)
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'ECHO',
                          'param': 'aa.txt',
                          'block': strEchoContent
                          }, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_Select(self):
        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("Select 1+2 from dual;")
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'SELECT',
                          'statement': 'Select 1+2 from dual',
                          }, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_SelectNotFinish(self):
        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("Select 1+2 from dual")
        self.assertFalse(isFinished)
        self.assertEqual('SELECT', ret_CommandSplitResult["name"])
        self.assertEqual(1, ret_errorCode)
        self.assertEqual("missing SQL_END at '<EOF>'", ret_errorMsg)

    def test_SQLAnalyze_SelectWithSlash(self):
        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("Select 1+2 from dual\n/")
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'SELECT', 'statement': 'Select 1+2 from dual'}, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_SelectMultiLine(self):
        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("Select 1+2,\n 3+4 \n from dual\n/")
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'SELECT', 'statement': 'Select 1+2,\n 3+4 \n from dual'}, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_USE(self):
        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_use api")
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'USE', 'nameSpace': 'API'}, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_use sql")
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'USE', 'nameSpace': 'SQL'}, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_use XXX")
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'USE', 'nameSpace': None}, ret_CommandSplitResult)
        self.assertEqual(1, ret_errorCode)
        self.assertEqual("line1:8  missing {'API', 'SQL'} at '<EOF>'", ret_errorMsg.strip())

    def test_SQLAnalyze_CreateProcedure(self):
        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("Create Procedure proc \n test ..;\n/")
        self.assertTrue(isFinished)
        self.assertEqual(
            {'name': 'PROCEDURE', 'statement': 'Create Procedure proc \n test ..;'},
            ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_Start(self):
        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_start c:\\abcd\\defg.sql")
        self.assertTrue(isFinished)
        self.assertEqual(
            {'argv': [], 'name': 'START', 'script': 'c:\\abcd\\defg.sql'},
            ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_start c:\\abcd\\defg.sql  abc def")
        self.assertTrue(isFinished)
        self.assertEqual(
            {'argv': ['abc', 'def'], 'name': 'START', 'script': 'c:\\abcd\\defg.sql'},
            ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_Declare(self):
        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("Declare Begin xxx \n end;\n/")
        self.assertTrue(isFinished)
        self.assertEqual(
            {'name': 'DECLARE', 'statement': 'Declare Begin xxx \n end;'},
            ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_Begin(self):
        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("Begin xxx \n end;\n/")
        self.assertTrue(isFinished)
        self.assertEqual(
            {'name': 'BEGIN', 'statement': 'Begin xxx \n end;'},
            ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_Spool(self):
        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_Spool aa.txt")
        self.assertTrue(isFinished)
        self.assertEqual(
            {'file': 'aa.txt', 'name': 'SPOOL'},
            ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_Spool off")
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
        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze(scriptHeader + script + scriptEnd)
        self.assertTrue(isFinished)
        self.assertEqual(
            {'block': script, 'name': 'SCRIPT'},
            ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

        scriptHeader = "> {% "
        script = "i=i+1"
        scriptEnd = " %}\n"
        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze(scriptHeader + script + scriptEnd)
        self.assertTrue(isFinished)
        self.assertEqual(
            {'block': script, 'name': 'SCRIPT'},
            ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_Session(self):
        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_Session save xxx")
        self.assertTrue(isFinished)
        self.assertEqual(
            {'action': 'SAVE', 'name': 'SESSION', 'sessionName': 'xxx'},
            ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_Session release xxx")
        self.assertTrue(isFinished)
        self.assertEqual(
            {'action': 'RELEASE', 'name': 'SESSION', 'sessionName': 'xxx'},
            ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_Session restore xxx")
        self.assertTrue(isFinished)
        self.assertEqual(
            {'action': 'RESTORE', 'name': 'SESSION', 'sessionName': 'xxx'},
            ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_Session saveurl xxx")
        self.assertTrue(isFinished)
        self.assertEqual(
            {'action': 'SAVEURL', 'name': 'SESSION', 'sessionName': 'xxx'},
            ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_Session show xxx")
        self.assertTrue(isFinished)
        self.assertEqual(
            {'action': 'SHOW', 'name': 'SESSION', 'sessionName': 'xxx'},
            ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_Session yyy xxx")
        self.assertTrue(isFinished)
        self.assertEqual(
            {'action': '', 'name': 'SESSION', 'sessionName': 'yyy'},
            ret_CommandSplitResult)
        self.assertEqual(1, ret_errorCode)
        self.assertEqual("line1:13  extraneous input 'xxx' expecting <EOF> ", ret_errorMsg)

    def test_SQLAnalyze_Host(self):
        script = '"""' + "\n" + \
                 'help' + "\n" + \
                 'dir' + "\n" + \
                 '"""'
        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_HOST " + script)
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)
        self.assertTrue(isFinished)
        self.assertEqual(
            {
                'name': 'HOST',
                'script': "help & dir"
            },
            ret_CommandSplitResult)

        script = 'ls dir1'
        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_HOST " + script)
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)
        self.assertTrue(isFinished)
        self.assertEqual(
            {
                'name': 'HOST',
                'script': "ls dir1"
            },
            ret_CommandSplitResult)

    def test_SQLAnalyze_Loop(self):
        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_LOOP END")
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'LOOP', 'rule': 'END'}, ret_CommandSplitResult)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_LOOP BREAK")
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'LOOP', 'rule': 'BREAK'}, ret_CommandSplitResult)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_LOOP CONTINUE")
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'LOOP', 'rule': 'CONTINUE'}, ret_CommandSplitResult)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_LOOP BEGIN UNTIL {% i>=3 %}")
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)
        self.assertTrue(isFinished)
        self.assertEqual(
            {'UNTIL': 'i>=3', 'name': 'LOOP', 'rule': 'BEGIN'},
            ret_CommandSplitResult)

    def test_SQLAnalyze_Whenever(self):
        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_WHENEVER ERROR CONTINUE")
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)
        self.assertTrue(isFinished)
        self.assertEqual(
            {'action': 'continue', 'condition': 'error', 'exitCode': 0, 'name': 'WHENEVER'}, ret_CommandSplitResult)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_WHENEVER ERROR EXIT 3")
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)
        self.assertTrue(isFinished)
        self.assertEqual(
            {'action': 'exit', 'condition': 'error', 'exitCode': 3, 'name': 'WHENEVER'}, ret_CommandSplitResult)

    def test_SQLAnalyze_If(self):
        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_ENDIF")
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'ENDIF'}, ret_CommandSplitResult)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_IF {% aa=bb %}")
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)
        self.assertTrue(isFinished)
        self.assertEqual({'expression': 'aa=bb', 'name': 'IF'}, ret_CommandSplitResult)

    def test_SQLAnalyze_Ssh(self):
        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_SSH disconnect")
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)
        self.assertTrue(isFinished)
        self.assertEqual({'action': 'disconnect', 'name': 'SSH'}, ret_CommandSplitResult)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_SSH save node1")
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)
        self.assertTrue(isFinished)
        self.assertEqual({'action': 'save', 'name': 'SSH', 'sessionName': 'node1'},
                         ret_CommandSplitResult)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_SSH restore node1")
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)
        self.assertTrue(isFinished)
        self.assertEqual({'action': 'restore', 'name': 'SSH', 'sessionName': 'node1'},
                         ret_CommandSplitResult)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_SSH execute ls aa bb cc --dd --ex ")
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)
        self.assertTrue(isFinished)
        self.assertEqual({'action': 'execute', 'command': 'ls aa bb cc --dd --ex', 'name': 'SSH'},
                         ret_CommandSplitResult)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_SSH connect node1 with user root password PaSsW@rd926 ")
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)
        self.assertTrue(isFinished)
        self.assertEqual(
            {'action': 'connect',
             'host': 'node1',
             'name': 'SSH',
             'password': 'PaSsW@rd926',
             'user': 'root'},
            ret_CommandSplitResult)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_SSH connect node1 with user root")
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)
        self.assertTrue(isFinished)
        self.assertEqual(
            {'action': 'connect',
             'host': 'node1',
             'name': 'SSH',
             'user': 'root'},
            ret_CommandSplitResult)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_SSH connect node1 with user root keyfile aabcdef==fadsfsd")
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)
        self.assertTrue(isFinished)
        self.assertEqual(
            {'action': 'connect',
             'host': 'node1',
             'keyFile': 'aabcdef==fadsfsd',
             'name': 'SSH',
             'user': 'root'},
            ret_CommandSplitResult)

    def test_SQLAnalyze_Job(self):
        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_JOB JOBMANAGER ON")
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)
        self.assertTrue(isFinished)
        self.assertEqual({'action': 'startJobmanager', 'name': 'JOB'}, ret_CommandSplitResult)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_JOB JOBMANAGER OFF")
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)
        self.assertTrue(isFinished)
        self.assertEqual({'action': 'stopJobmanager', 'name': 'JOB'}, ret_CommandSplitResult)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_JOB WAIT abcd")
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)
        self.assertTrue(isFinished)
        self.assertEqual({'action': 'wait', 'jobName': 'abcd', 'name': 'JOB'}, ret_CommandSplitResult)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_JOB SHOW abcd")
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)
        self.assertTrue(isFinished)
        self.assertEqual({'action': 'show', 'jobName': 'abcd', 'name': 'JOB'}, ret_CommandSplitResult)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_JOB ABORT abcd")
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)
        self.assertTrue(isFinished)
        self.assertEqual({'action': 'abort', 'jobName': 'abcd', 'name': 'JOB'}, ret_CommandSplitResult)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_JOB SHUTDOWN abcd")
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)
        self.assertTrue(isFinished)
        self.assertEqual({'action': 'shutdown', 'jobName': 'abcd', 'name': 'JOB'}, ret_CommandSplitResult)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_JOB TIMER tp1")
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)
        self.assertTrue(isFinished)
        self.assertEqual({'action': 'timer', 'name': 'JOB', 'timerPoint': 'tp1'}, ret_CommandSplitResult)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_JOB START abcd")
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)
        self.assertTrue(isFinished)
        self.assertEqual({'action': 'start', 'jobName': 'abcd', 'name': 'JOB'}, ret_CommandSplitResult)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_JOB DEREGISTER WORKER")
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)
        self.assertTrue(isFinished)
        self.assertEqual({'action': 'deregister', 'name': 'JOB'}, ret_CommandSplitResult)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_JOB REGISTER WORKER TO ABCD")
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)
        self.assertTrue(isFinished)
        self.assertEqual({'action': 'register', 'jobName': 'ABCD', 'name': 'JOB'}, ret_CommandSplitResult)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_JOB SET ABCD Key1=Value1 Key2=Value2")
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)
        self.assertTrue(isFinished)
        self.assertEqual(
            {'action': 'set',
             'jobName': 'ABCD',
             'name': 'JOB',
             'param': {'Key1': 'Value1', 'Key2': 'Value2'}}, ret_CommandSplitResult)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_JOB CREATE ABCD Key1=Value1 Key2=Value2")
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)
        self.assertTrue(isFinished)
        self.assertEqual(
            {'action': 'create',
             'jobName': 'ABCD',
             'name': 'JOB',
             'param': {'Key1': 'Value1', 'Key2': 'Value2'}}, ret_CommandSplitResult)

    def test_SQLAnalyze_Compare(self):
        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_COMPARE aa.txt bb.txt MASK NOCASE")
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)
        self.assertTrue(isFinished)
        self.assertEqual(
            {'action': 'compare',
             'compareOptions': {'case': False, 'mask': True},
             'name': 'COMPARE',
             'referenceFile': 'bb.txt',
             'targetFile': 'aa.txt'}, ret_CommandSplitResult)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_COMPARE MASKLINE \"aa bb\"=>\"cc bb\"")
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)
        self.assertTrue(isFinished)
        self.assertEqual(
            {'action': 'mask',
             'compareOptions': {},
             'name': 'COMPARE',
             'source': '"aa bb"',
             'target': '"cc bb"'}, ret_CommandSplitResult)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_COMPARE NOMASKLINE \"aa bb\"")
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)
        self.assertTrue(isFinished)
        self.assertEqual(
            {'action': 'nomask',
             'compareOptions': {},
             'name': 'COMPARE',
             'source': '"aa bb"'}, ret_CommandSplitResult)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_COMPARE SKIPLINE \"aa*bb\"")
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)
        self.assertTrue(isFinished)
        self.assertEqual(
            {'action': 'skip',
             'compareOptions': {},
             'name': 'COMPARE',
             'source': '"aa*bb"'}, ret_CommandSplitResult)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_COMPARE NOSKIPLINE \"aa*bb\"")
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)
        self.assertTrue(isFinished)
        self.assertEqual(
            {'action': 'noskip',
             'compareOptions': {},
             'name': 'COMPARE',
             'source': '"aa*bb"'}, ret_CommandSplitResult)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_COMPARE RESET")
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)
        self.assertTrue(isFinished)
        self.assertEqual(
            {'action': 'reset',
             'compareOptions': {},
             'name': 'COMPARE'}, ret_CommandSplitResult)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_COMPARE SET")
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)
        self.assertTrue(isFinished)
        self.assertEqual(
            {'action': 'set',
             'compareOptions': {},
             'name': 'COMPARE'}, ret_CommandSplitResult)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_COMPARE SET MASK CASE IGBLANK NOTRIM")
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)
        self.assertTrue(isFinished)
        self.assertEqual(
            {'action': 'set',
             'compareOptions': {'case': True, 'igblank': True, 'mask': True, 'trim': False},
             'name': 'COMPARE'}, ret_CommandSplitResult)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_COMPARE SET OUTPUT CONSOLE")
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)
        self.assertTrue(isFinished)
        self.assertEqual(
            {'action': 'set', 'compareOptions': {'output': ['console']}, 'name': 'COMPARE'},
            ret_CommandSplitResult)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_COMPARE SET OUTPUT DIFFFILE")
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)
        self.assertTrue(isFinished)
        self.assertEqual(
            {'action': 'set', 'compareOptions': {'output': ['diffFile']}, 'name': 'COMPARE'},
            ret_CommandSplitResult)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_COMPARE SET OUTPUT CONSOLE DIFFFILE")
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)
        self.assertTrue(isFinished)
        self.assertEqual(
            {'action': 'set', 'compareOptions': {'output': ['console', 'diffFile']}, 'name': 'COMPARE'},
            ret_CommandSplitResult)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_COMPARE SET ALGORITHM LCS")
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)
        self.assertTrue(isFinished)
        self.assertEqual(
            {'action': 'set', 'compareOptions': {'algorithm': 'lcs'}, 'name': 'COMPARE'},
            ret_CommandSplitResult)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_COMPARE SET ALGORITHM MYERS")
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)
        self.assertTrue(isFinished)
        self.assertEqual(
            {'action': 'set', 'compareOptions': {'algorithm': 'myers'}, 'name': 'COMPARE'},
            ret_CommandSplitResult)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_COMPARE SET WORK ENCODING UTF-8")
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)
        self.assertTrue(isFinished)
        self.assertEqual(
            {'action': 'set',
             'compareOptions': {'workEncoding': 'UTF-8'},
             'name': 'COMPARE'},
            ret_CommandSplitResult)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_COMPARE SET REFERENCE ENCODING GBK")
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)
        self.assertTrue(isFinished)
        self.assertEqual(
            {'action': 'set', 'compareOptions': {'refEncoding': 'GBK'}, 'name': 'COMPARE'},
            ret_CommandSplitResult)

    def test_SQLAnalyze_Data(self):
        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_DATA SET SEEDFILE DIR d:\\temp\\aa.txt")
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)
        self.assertTrue(isFinished)
        self.assertEqual(
            {'action': 'set',
             'name': 'DATA',
             'option': 'seedDir',
             'seedDir': 'd:\\temp\\aa.txt'},
            ret_CommandSplitResult)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("_DATA CONVERT FS FILE aa.txt TO MEM FILE bb.dat")
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)
        self.assertTrue(isFinished)
        self.assertEqual(
            {
                'action': 'convert',
                'name': 'DATA',
                'sourceFile': 'aa.txt',
                'sourceFileType': 'FS',
                'targetFile': 'bb.dat',
                'targetFileType': 'MEM'
             },
            ret_CommandSplitResult)

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze(
            "_DATA CREATE FS FILE aa.txt \n" +
            "(\n" +
            "random_int(10), 'aaa'\n" +
            "bb, ccd"
            + ") rows 1000;"
        )
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)
        self.assertTrue(isFinished)
        self.assertEqual(
            {
                'action': 'create',
                'columnExpression': "random_int(10), 'aaa'\nbb, ccd",
                'fileType': 'FS',
                'name': 'DATA',
                'rowCount': 1000,
                'targetFile': 'aa.txt'
             },
            ret_CommandSplitResult)

    def test_SQLExecuteSanity(self):
        from ..testcli import TestCli

        scriptFile = "testsqlsanity.sql"

        scriptBaseFile = os.path.splitext(scriptFile)[0]
        fullScriptFile = os.path.abspath(os.path.join(os.path.dirname(__file__), "", scriptFile))
        fullRefFile = os.path.abspath(os.path.join(os.path.dirname(__file__), "", scriptBaseFile + ".ref"))
        fullLogFile = os.path.abspath(os.path.join(tempfile.gettempdir(), scriptBaseFile + ".log"))

        # 运行测试程序，开启无头模式(不再控制台上显示任何内容),同时不打印Logo
        testcli = TestCli(
            logfilename=fullLogFile,
            headlessMode=True,
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

    def test_SQLExecuteWithStartParameter(self):
        from ..testcli import TestCli

        scriptFile = "testsqlstart.sql"

        scriptBaseFile = os.path.splitext(scriptFile)[0]
        fullScriptFile = os.path.abspath(os.path.join(os.path.dirname(__file__), "", scriptFile))
        fullRefFile = os.path.abspath(os.path.join(os.path.dirname(__file__), "", scriptBaseFile + ".ref"))
        fullLogFile = os.path.abspath(os.path.join(tempfile.gettempdir(), scriptBaseFile + ".log"))

        # 运行测试程序，开启无头模式(不再控制台上显示任何内容),同时不打印Logo
        testcli = TestCli(
            logfilename=fullLogFile,
            headlessMode=True,
            script=fullScriptFile
        )
        retValue = testcli.run_cli()
        # 脚本中包含了Exit的字样，所以判断是否等于exitValue （3）
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

    def test_SQLExecuteWithSQLCLI_CONNECTION_URL(self):
        from ..testcli import TestCli

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
            headlessMode=True,
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
        from ..testcli import TestCli

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
            headlessMode=True,
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
        from ..testcli import TestCli

        scriptFile = "testsqlembeddscript.sql"

        scriptBaseFile = os.path.splitext(scriptFile)[0]
        fullScriptFile = os.path.abspath(os.path.join(os.path.dirname(__file__), "", scriptFile))
        fullRefFile = os.path.abspath(os.path.join(os.path.dirname(__file__), "", scriptBaseFile + ".ref"))
        fullLogFile = os.path.abspath(os.path.join(tempfile.gettempdir(), scriptBaseFile + ".log"))

        # 运行测试程序，开启无头模式(不再控制台上显示任何内容),同时不打印Logo
        testcli = TestCli(
            logfilename=fullLogFile,
            headlessMode=True,
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
        from ..testcli import TestCli

        scriptFile = "testsessionmanage.sql"

        scriptBaseFile = os.path.splitext(scriptFile)[0]
        fullScriptFile = os.path.abspath(os.path.join(os.path.dirname(__file__), "", scriptFile))
        fullRefFile = os.path.abspath(os.path.join(os.path.dirname(__file__), "", scriptBaseFile + ".ref"))
        fullLogFile = os.path.abspath(os.path.join(tempfile.gettempdir(), scriptBaseFile + ".log"))

        # 运行测试程序，开启无头模式(不再控制台上显示任何内容),同时不打印Logo
        testcli = TestCli(
            logfilename=fullLogFile,
            headlessMode=True,
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

    def test_SQLIfAndLoopCondition(self):
        from ..testcli import TestCli

        scriptFile = "testsqlifandloop.sql"

        scriptBaseFile = os.path.splitext(scriptFile)[0]
        fullScriptFile = os.path.abspath(os.path.join(os.path.dirname(__file__), "", scriptFile))
        fullRefFile = os.path.abspath(os.path.join(os.path.dirname(__file__), "", scriptBaseFile + ".ref"))
        fullLogFile = os.path.abspath(os.path.join(tempfile.gettempdir(), scriptBaseFile + ".log"))

        # 运行测试程序，开启无头模式(不再控制台上显示任何内容),同时不打印Logo
        testcli = TestCli(
            logfilename=fullLogFile,
            headlessMode=True,
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

    def test_SQLLoadPlugin(self):
        from ..testcli import TestCli

        scriptFile = "testplugin.sql"

        scriptBaseFile = os.path.splitext(scriptFile)[0]
        fullScriptFile = os.path.abspath(os.path.join(os.path.dirname(__file__), "", scriptFile))
        fullRefFile = os.path.abspath(os.path.join(os.path.dirname(__file__), "", scriptBaseFile + ".ref"))
        fullLogFile = os.path.abspath(os.path.join(tempfile.gettempdir(), scriptBaseFile + ".log"))

        # 运行测试程序，开启无头模式(不再控制台上显示任何内容),同时不打印Logo
        testcli = TestCli(
            logfilename=fullLogFile,
            headlessMode=True,
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

    def test_SQLWhenever(self):
        from ..testcli import TestCli

        scriptFile = "testsqlwhenever.sql"

        scriptBaseFile = os.path.splitext(scriptFile)[0]
        fullScriptFile = os.path.abspath(os.path.join(os.path.dirname(__file__), "", scriptFile))
        fullRefFile = os.path.abspath(os.path.join(os.path.dirname(__file__), "", scriptBaseFile + ".ref"))
        fullLogFile = os.path.abspath(os.path.join(tempfile.gettempdir(), scriptBaseFile + ".log"))

        # 运行测试程序，开启无头模式(不再控制台上显示任何内容),同时不打印Logo
        testcli = TestCli(
            logfilename=fullLogFile,
            headlessMode=True,
            script=fullScriptFile
        )
        retValue = testcli.run_cli()
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

    def test_SQLJobManager(self):
        from ..testcli import TestCli

        scriptFile = "testjobmanager.sql"

        scriptBaseFile = os.path.splitext(scriptFile)[0]
        fullScriptFile = os.path.abspath(os.path.join(os.path.dirname(__file__), "", scriptFile))
        fullRefFile = os.path.abspath(os.path.join(os.path.dirname(__file__), "", scriptBaseFile + ".ref"))
        fullLogFile = os.path.abspath(os.path.join(tempfile.gettempdir(), scriptBaseFile + ".log"))

        # 运行测试程序，开启无头模式(不再控制台上显示任何内容),同时不打印Logo
        testcli = TestCli(
            logfilename=fullLogFile,
            headlessMode=True,
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

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
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

        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
            = APIAnalyze(script)
        self.assertEqual(None, ret_errorMsg)
        self.assertEqual(0, ret_errorCode)
        self.assertTrue(isFinished)

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

    def test_APIExecute_Get(self):
        from ..testcli import TestCli

        scriptFile = "testapiget.api"

        scriptBaseFile = os.path.splitext(scriptFile)[0]
        fullScriptFile = os.path.abspath(os.path.join(os.path.dirname(__file__), "", scriptFile))
        fullRefFile = os.path.abspath(os.path.join(os.path.dirname(__file__), "", scriptBaseFile + ".ref"))
        fullLogFile = os.path.abspath(os.path.join(tempfile.gettempdir(), scriptBaseFile + ".log"))

        # 运行测试程序，开启无头模式(不再控制台上显示任何内容),同时不打印Logo
        testcli = TestCli(
            logfilename=fullLogFile,
            headlessMode=True,
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

    def test_lastcommandresult(self):
        from ..testcli import TestCli

        scriptFile = "testlastcommandresult.sql"

        scriptBaseFile = os.path.splitext(scriptFile)[0]
        fullScriptFile = os.path.abspath(os.path.join(os.path.dirname(__file__), "", scriptFile))
        fullRefFile = os.path.abspath(os.path.join(os.path.dirname(__file__), "", scriptBaseFile + ".ref"))
        fullLogFile = os.path.abspath(os.path.join(tempfile.gettempdir(), scriptBaseFile + ".log"))

        # 运行测试程序，开启无头模式(不再控制台上显示任何内容),同时不打印Logo
        testcli = TestCli(
            logfilename=fullLogFile,
            headlessMode=True,
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

    def test_compare(self):
        from ..testcli import TestCli

        scriptFile = "testcompare.sql"

        scriptBaseFile = os.path.splitext(scriptFile)[0]
        fullScriptFile = os.path.abspath(os.path.join(os.path.dirname(__file__), scriptFile))
        fullRefFile = os.path.abspath(os.path.join(os.path.dirname(__file__), scriptBaseFile + ".ref"))
        fullLogFile = os.path.abspath(os.path.join(tempfile.gettempdir(), scriptBaseFile + ".log"))

        # 运行测试程序，开启无头模式(不再控制台上显示任何内容),同时不打印Logo
        testcli = TestCli(
            logfilename=fullLogFile,
            headlessMode=True,
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

        # 删除指定的dif文件
        fullDiffFile = os.path.abspath(os.path.join(os.path.dirname(__file__), "testcomparework.dif"))
        self.assertTrue(os.path.exists(fullDiffFile))
        os.remove(fullDiffFile)

    def test_sqlmapping(self):
        from ..testcli import TestCli

        scriptFile = "testsqlmapping.sql"

        scriptBaseFile = os.path.splitext(scriptFile)[0]
        fullScriptFile = os.path.abspath(os.path.join(os.path.dirname(__file__), "", scriptFile))
        fullRefFile = os.path.abspath(os.path.join(os.path.dirname(__file__), "", scriptBaseFile + ".ref"))
        fullLogFile = os.path.abspath(os.path.join(tempfile.gettempdir(), scriptBaseFile + ".log"))

        # 运行测试程序，开启无头模式(不再控制台上显示任何内容),同时不打印Logo
        testcli = TestCli(
            logfilename=fullLogFile,
            headlessMode=True,
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

    def test_sqllogmaskandfilter(self):
        from ..testcli import TestCli

        scriptFile = "testlogmaskandfilter.sql"

        scriptBaseFile = os.path.splitext(scriptFile)[0]
        fullScriptFile = os.path.abspath(os.path.join(os.path.dirname(__file__), "", scriptFile))
        fullRefFile = os.path.abspath(os.path.join(os.path.dirname(__file__), "", scriptBaseFile + ".ref"))
        fullLogFile = os.path.abspath(os.path.join(tempfile.gettempdir(), scriptBaseFile + ".log"))

        # 运行测试程序，开启无头模式(不再控制台上显示任何内容),同时不打印Logo
        testcli = TestCli(
            logfilename=fullLogFile,
            headlessMode=True,
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


if __name__ == '__main__':
    unittest.main()
