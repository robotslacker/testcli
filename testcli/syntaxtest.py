# -*- coding: utf-8 -*-
import unittest
from .sqlparse import SQLAnalyze


class TestStringMethods(unittest.TestCase):
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

    def test_SQLAnalyze_Set(self):
        (isFinished, ret_CommandSplitResult, _, _, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("set")
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'SET'}, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_Set2Parameter(self):
        (isFinished, ret_CommandSplitResult, _, _, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("set XX YY")
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'SET',
                          'optionName': 'XX',
                          'optionValue': 'YY'}, ret_CommandSplitResult)
        self.assertEqual(0, ret_errorCode)
        self.assertEqual(None, ret_errorMsg)

    def test_SQLAnalyze_Set3Parameter(self):
        (isFinished, ret_CommandSplitResult, _, _, ret_errorCode, ret_errorMsg) \
            = SQLAnalyze("set ZZ DD FF")
        self.assertTrue(isFinished)
        self.assertEqual({'name': 'SET',
                          'optionName': 'ZZ',
                          'optionValue': 'DD',
                          'optionValue2': 'FF'
                          }, ret_CommandSplitResult)
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


if __name__ == '__main__':
    unittest.main()
