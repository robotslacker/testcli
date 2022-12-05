# -*- coding: utf-8 -*-
import datetime
import time
from json import JSONDecodeError

import click
import json
import os
import re
import platform
import binascii
import decimal
import traceback
import urllib3
from .sqlclijdbc import SQLCliJDBCException
from .sqlclijdbc import SQLCliJDBCLargeObject
from .sqlclijdbc import SQLCliJDBCTimeOutException
from .sqlparse import SQLAnalyze
from .apiparse import APIAnalyze
from .sqlparse import SQLFormatWithPrefix
from .apiparse import APIRequestStringFormatWithPrefix

from .commands.load import loadPlugin
from .commands.load import loadDriver
from .commands.load import loadMap
from .commands.exit import exitApplication
from .commands.session import sessionManage
from .commands.assertExpression import assertExpression
from .commands.assertExpression import evalExpression
from .commands.embeddScript import executeEmbeddScript
from .commands.connectdb import connectDb, disconnectDb
from .commands.start import executeFile
from .commands.host import executeLocalCommand
from .commands.spool import spool
from .commands.echo import echo_input
from .commands.setOptions import setOptions
from .commands.cliSleep import cliSleep
from .commands.userNameSpace import userNameSpace
from .commands.whenever import setWheneverAction
from .commands.ssh import executeSshRequest

from .common import rewriteSQLStatement
from .common import rewriteAPIStatement
from .common import parseSQLHints
from .common import parseAPIHints
from .testcliexception import TestCliException
from .globalvar import lastCommandResult


class CmdExecute(object):
    def __init__(self):
        # 程序处理选项
        self.testOptions = None

        # 主程序处理句柄
        self.cliHandler = None

        # 当前Executeor的WorkerName
        self.workerName = None

        # 程序Echo输出句柄
        self.echofile = None

        # 脚本启动的时间
        self.startTime = time.time()

        # 当前执行的命令脚本
        self.script = None

        # 命令重写处理
        self.mappingHandler = None

        # Scenario名称，如果当前未指定，则重复上一个命令的Scenario信息
        self.scenario = ''

        # Transaction信息
        self.transaction = ""

        # 当前脚本的TimeOut设置
        self.sqlTimeOut = -1          # SQL执行的超时时间设置
        self.apiTimeOut = -1          # API执行的超时时间设置
        self.scriptTimeOut = -1       # 脚本执行的超时时间设置
        self.timeout = -1             # 当前SQL的超时时间设置
        self.timeOutMode = None       # COMMAND|SCRIPT|NONE

        # 数据库连接
        self.sqlConn = None
        self.sqlCursor = None
        self.apiConn = None

        # 记录语句是否当前处于条件表达式判定中
        self.ifMode = False
        self.ifCondition = False
        # 记录语句是否在循环过程中
        self.loopMode = False
        self.loopCondition = False
        self.loopStartPos = 0

    def setStartTime(self, startTime):
        self.startTime = startTime

    def getStartTime(self):
        return self.startTime

    def jqparse(self, obj, path='.'):
        class DecimalEncoder(json.JSONEncoder):
            def default(self, o):
                if isinstance(o, decimal.Decimal):
                    return float(o)
                super(DecimalEncoder, self).default(o)

        if self is None:
            pass
        if obj is None:
            if "TESTCLI_DEBUG" in os.environ:
                click.secho("[DEBUG] JQ Parse Error: obj is None")
            return "****"
        try:
            obj = json.loads(obj) if isinstance(obj, str) else obj
            find_str, find_map = '', ['["%s"]', '[%s]', '%s', '.%s']
            for im in path.split('.'):
                if not im:
                    continue
                if obj is None:
                    if "TESTCLI_DEBUG" in os.environ:
                        click.secho("[DEBUG] JQ Parse Error: obj is none")
                    return "****"
                if isinstance(obj, (list, tuple, str)):
                    if im.startswith('[') and im.endswith(']'):
                        im = im[1:-1]
                    if ':' in im:
                        slice_default = [0, len(obj), 1]
                        obj, quota = obj[slice(
                            *[int(sli) if sli else slice_default[i] for i, sli in
                              enumerate(im.split(':'))])], 1
                    else:
                        obj, quota = obj[int(im)], 1
                else:
                    if im in obj:
                        obj, quota = obj.get(im), 0
                    elif im.endswith('()'):
                        obj, quota = list(getattr(obj, im[:-2])()), 3
                    else:
                        if im.isdigit():
                            obj, quota = obj[int(im)], 1
                        else:
                            raise KeyError(im)
                find_str += find_map[quota] % im
            return obj if isinstance(obj, str) else json.dumps(obj,
                                                               sort_keys=True,
                                                               ensure_ascii=False,
                                                               cls=DecimalEncoder)
        except (IndexError, KeyError, ValueError) as je:
            if "TESTCLI_DEBUG" in os.environ:
                click.secho("[DEBUG] JQ Parse Error: " + repr(je))
            return "****"

    @staticmethod
    def sortresult(result):
        # 无法使用系统默认的排序函数，这里空值总是置于最后
        for i in range(len(result) - 1, 0, -1):
            for j in range(i - 1, -1, -1):
                bNeedExchange = False
                for k in range(0, len(result[i])):
                    if len(result[i]) != len(result[j]):
                        return
                    if result[i][k] is None and result[j][k] is None:
                        # 两边都是空值
                        continue
                    if result[i][k] is None and result[j][k] is not None:
                        # 左边空值， 右侧不空， 按照左侧大值来考虑
                        break
                    if result[j][k] is None and result[i][k] is not None:
                        # 右侧空值， 左边不空， 按照右侧大值来考虑
                        bNeedExchange = True
                        break
                    if not isinstance(result[i][k], type(result[j][k])):
                        if str(result[i][k]) < str(result[j][k]):
                            bNeedExchange = True
                            break
                        if str(result[i][k]) > str(result[j][k]):
                            break
                    else:
                        if result[i][k] < result[j][k]:
                            bNeedExchange = True
                            break
                        if result[i][k] > result[j][k]:
                            break
                if bNeedExchange:
                    result[j], result[i] = result[i], result[j]

    def getcommandResult(self, cursor, rowcount):
        """
            返回的内容：
                title           输出的前提示信息
                result          结果数据集
                headers         表头信息
                columnTypes     结果字段类型
                status          输出的后提示信息
                FetchStatus     是否输出完成
                rowcount        共返回记录行数
                Warning         警告信息
        """
        title = headers = None
        fetchStatus = True

        def format_column(p_column, p_columntype):
            if type(p_column) == float:
                return self.testOptions.get("FLOAT_FORMAT") % p_column
            elif type(p_column) in (bool, str, int):
                return p_column
            elif type(p_column) == list:
                return p_column
            elif type(p_column) == datetime.date:
                columnFormat = self.testOptions.get("DATE_FORMAT")
                if platform.system().lower() in ['windows', 'darwin']:
                    columnFormat = columnFormat.replace("%04Y", "%Y")
                else:
                    columnFormat = columnFormat.replace("%Y", "%04Y")
                return p_column.strftime(columnFormat)
            elif type(p_column) == datetime.datetime:
                if p_columntype in ["TIMESTAMP WITH TIME ZONE",
                                    "TIMESTAMP WITH LOCAL TIME ZONE"]:
                    columnFormat = self.testOptions.get("DATETIME-TZ_FORMAT")
                else:
                    columnFormat = self.testOptions.get("DATETIME_FORMAT")
                if platform.system().lower() in ['windows', 'darwin']:
                    columnFormat = columnFormat.replace("%04Y", "%Y")
                else:
                    columnFormat = columnFormat.replace("%Y", "%04Y")
                return p_column.strftime(columnFormat)
            elif type(p_column) == datetime.time:
                return p_column.strftime(self.testOptions.get("TIME_FORMAT"))
            elif type(p_column) == bytearray:
                if p_columntype == "BLOB":
                    columnTrimedLength = int(self.testOptions.get("LOB_LENGTH"))
                    bColumnFullOutput = True
                    if len(p_column) > columnTrimedLength:
                        bColumnFullOutput = False
                        p_column = p_column[:columnTrimedLength]
                    # 转换为16进制，并反算成ASCII
                    p_column = binascii.b2a_hex(p_column)
                    p_column = p_column.decode()
                    if not bColumnFullOutput:
                        # 用...的方式提醒输出没有结束，只是由于格式控制导致不显示
                        return "0x" + p_column + "..."
                    else:
                        return "0x" + p_column
                else:
                    # 转换为16进制，并反算成ASCII
                    p_column = binascii.b2a_hex(p_column)
                    p_column = p_column.decode()
                    return "0x" + p_column
            elif type(p_column) == decimal.Decimal:
                if self.testOptions.get("DECIMAL_FORMAT") != "":
                    return self.testOptions.get("DECIMAL_FORMAT") % p_column
                else:
                    return p_column
            elif type(p_column) == SQLCliJDBCLargeObject:
                trimedLength = int(self.testOptions.get("LOB_LENGTH"))
                if trimedLength < 4:
                    trimedLength = 4
                if trimedLength > p_column.getObjectLength():
                    if p_column.getColumnTypeName().upper().find("CLOB") != -1:
                        dataValue = p_column.getData(1, p_column.getObjectLength())
                        return dataValue
                    elif p_column.getColumnTypeName().upper().find("BLOB") != -1:
                        dataValue = p_column.getData(1, p_column.getObjectLength())
                        dataValue = binascii.b2a_hex(dataValue)
                        dataValue = dataValue.decode()
                        return "0x" + dataValue
                else:
                    if p_column.getColumnTypeName().upper().find("CLOB") != -1:
                        dataValue = "Len:" + str(p_column.getObjectLength()) + ";" + \
                                      "Content:[" + \
                                      p_column.getData(1, trimedLength - 3) + "..." + \
                                      p_column.getData(p_column.getObjectLength() - 2, 3) + \
                                      "]"
                        return dataValue
                    elif p_column.getColumnTypeName().upper().find("BLOB") != -1:
                        dataValue = "Len:" + str(p_column.getObjectLength()) + ";" + \
                                      "Content:0x[" + \
                                      binascii.b2a_hex(p_column.getData(1, trimedLength - 3)).decode() + "..." + \
                                      binascii.b2a_hex(p_column.getData(p_column.getObjectLength() - 2, 3)).decode() + \
                                      "]"
                        return dataValue
            elif isinstance(p_column, type(None)):
                return p_column
            else:
                # 其他类型直接返回
                raise SQLCliJDBCException("TestCli-0000: Unknown column type [" +
                                          str(p_columntype) + ":" + str(type(p_column)) +
                                          "] in format_column")

        # cursor.description is not None for queries that return result sets,
        # e.g. SELECT.
        result = []
        columnTypes = []
        if cursor.description is not None:
            headers = [x[0] for x in cursor.description]
            columnTypes = [x[1] for x in cursor.description]
            if cursor.warnings is not None:
                status = "{0} row{1} selected with warnings."
            else:
                status = "{0} row{1} selected."
            arraySize = int(self.testOptions.get("ARRAYSIZE"))
            rowset = cursor.fetchmany(arraySize)
            for row in rowset:
                collatedRow = []
                for nColumnPos in range(0, len(row)):
                    column = row[nColumnPos]
                    columntype = columnTypes[nColumnPos]
                    # 对于空值直接返回
                    if column is None:
                        collatedRow.append(None)
                        continue

                    # 处理各种数据类型
                    if columnTypes[nColumnPos] == "STRUCT":
                        columnValue = "STRUCTURE("
                        for pos in range(0, len(column)):
                            m_ColumnType = str(type(column[pos]))
                            if pos == 0:
                                if type(column[pos]) == str:
                                    columnValue = columnValue + "'" + str(column[pos]) + "'"
                                elif type(column[pos]) == datetime.date:
                                    columnValue = columnValue + "DATE '" + \
                                                    format_column(column[pos], m_ColumnType) + "'"
                                elif type(column[pos]) == datetime.datetime:
                                    columnValue = columnValue + "TIMESTAMP '" + \
                                                    format_column(column[pos], m_ColumnType) + "'"
                                elif isinstance(column[pos], type(None)):
                                    columnValue = columnValue + "<null>"
                                else:
                                    columnValue = columnValue + \
                                                    str(format_column(column[pos], m_ColumnType))
                            else:
                                if type(column[pos]) == str:
                                    columnValue = columnValue + ",'" + str(column[pos]) + "'"
                                elif type(column[pos]) == datetime.date:
                                    columnValue = columnValue + ",DATE '" + \
                                                    format_column(column[pos], m_ColumnType) + "'"
                                elif type(column[pos]) == datetime.datetime:
                                    columnValue = columnValue + ",TIMESTAMP '" + \
                                                    format_column(column[pos], m_ColumnType) + "'"
                                elif isinstance(column[pos], type(None)):
                                    columnValue = columnValue + ",<null>"
                                else:
                                    columnValue = columnValue + "," + \
                                                    str(format_column(column[pos], m_ColumnType))
                        columnValue = columnValue + ")"
                        collatedRow.append(columnValue)
                    elif columnTypes[nColumnPos] == "ARRAY":
                        columnValue = "ARRAY["
                        if self.testOptions.get('OUTPUT_SORT_ARRAY') == "ON":
                            # 保证Array的输出每次都一样顺序
                            # 需要注意可能有NULL值导致字符数组无法排序的情况, column是一个一维数组
                            column.sort(key=lambda x: (x is None, x))
                        for pos in range(0, len(column)):
                            m_ColumnType = str(type(column[pos]))
                            if pos == 0:
                                if type(column[pos]) == str:
                                    columnValue = columnValue + "'" + str(column[pos]) + "'"
                                elif type(column[pos]) == datetime.date:
                                    columnValue = columnValue + "DATE '" + \
                                                    format_column(column[pos], m_ColumnType) + "'"
                                elif type(column[pos]) == datetime.datetime:
                                    columnValue = columnValue + "TIMESTAMP '" + \
                                                    format_column(column[pos], m_ColumnType) + "'"
                                elif isinstance(column[pos], type(None)):
                                    columnValue = columnValue + "<null>"
                                else:
                                    columnValue = columnValue + \
                                                    str(format_column(column[pos], m_ColumnType))
                            else:
                                if type(column[pos]) == str:
                                    columnValue = columnValue + ",'" + str(column[pos]) + "'"
                                elif type(column[pos]) == datetime.date:
                                    columnValue = columnValue + ",DATE '" + \
                                                    format_column(column[pos], m_ColumnType) + "'"
                                elif type(column[pos]) == datetime.datetime:
                                    columnValue = columnValue + ",TIMESTAMP '" + \
                                                    format_column(column[pos], m_ColumnType) + "'"
                                elif isinstance(column[pos], type(None)):
                                    columnValue = columnValue + ",<null>"
                                else:
                                    columnValue = columnValue + "," + \
                                                    str(format_column(column[pos], m_ColumnType))
                        columnValue = columnValue + "]"
                        collatedRow.append(columnValue)
                    else:
                        collatedRow.append(format_column(column, columntype))
                collatedRow = tuple(collatedRow)
                result.append(collatedRow)
            rowcount = rowcount + len(rowset)
            if len(rowset) < arraySize:
                # 已经没有什么可以取的了, 游标结束
                fetchStatus = False
        else:
            if cursor.warnings is not None:
                status = "{0} row{1} affected with warnings."
            else:
                status = "{0} row{1} affected."
            rowcount = 0 if cursor.rowcount == -1 else cursor.rowcount
            result = None
            fetchStatus = False

        # 只要不是最后一次打印，不再返回status内容
        if fetchStatus:
            status = None

        if self.testOptions.get('FEEDBACK').upper() == 'ON' and status is not None:
            status = status.format(rowcount, "" if rowcount in [0, 1] else "s")
        else:
            status = None
        return title, result, headers, columnTypes, status, fetchStatus, rowcount, cursor.warnings

    '''
        执行指定的API请求

        输入：
            apiRequest             JSON对象，请求的内容
            apiHints               提示信息            
    '''
    def executeAPIStatement(self, apiRequest, apiHints, startTime):
        """
        返回内容：
            错误情况下：
            {
                "type": "error",
                "message": apiErrorMessage
            }
            正确情况下：
            {
                "type": "result",
                "title": None,
                "rows": None,
                "headers": None,
                "columnTypes": None,
                "status": content
            }
        """
        httpHandler = self.cliHandler.httpHandler

        httpMethod = apiRequest["httpMethod"]
        httpRequestTarget = apiRequest["httpRequestTarget"]

        headers = {}
        fields = {}
        if "headers" in apiRequest:
            headers = apiRequest["headers"]
        if "httpFields" in apiRequest:
            fields = apiRequest["httpFields"]

        if "contents" in apiRequest:
            body = "".join(apiRequest["contents"])
        else:
            body = ""
        try:
            ret = httpHandler.request(
                method=httpMethod,
                url=httpRequestTarget,
                headers=headers,
                fields=fields,
                body=body
            )
            result = {"status": ret.status}
            data = ret.data.decode('utf-8')
            try:
                data = json.loads(data)
            except JSONDecodeError:
                # 返回的对象不是一个JSON
                pass
            result["content"] = data
            result = json.dumps(obj=result,
                                sort_keys=True,
                                indent=4,
                                separators=(',', ': '),
                                ensure_ascii=False)
            yield {
                "type": "result",
                "title": None,
                "rows": None,
                "headers": None,
                "columnTypes": None,
                "status": result
            }
            return
        except (urllib3.exceptions.MaxRetryError, ) as ex:
            yield {
                "type": "error",
                "message": str(ex)
            }
            return

    def executeSQLStatement(self, sql: str, sqlHints, startTime):
        """
        返回内容：
            错误情况下：
            {
                "type": "error",
                "message": sqlErrorMessage
            }
            正确情况下：
            {
                "type": "result",
                "title": title,
                "rows": result,
                "headers": headers,
                "columnTypes": columnTypes,
                "status": status
            }
        """

        # 进入到SQL执行阶段, 开始执行SQL语句
        if self.sqlConn:
            # 打开游标
            self.sqlCursor = self.sqlConn.cursor()
        else:
            # 进入到SQL执行阶段，不是特殊命令, 数据库连接也不存在, 直接报错
            if self.testOptions.get("WHENEVER_ERROR") == "EXIT":
                raise TestCliException("Not Connected. ")
            else:
                yield {
                    "type": "error",
                    "message": "Not connected. "
                }

        # 执行正常的SQL语句
        if self.sqlCursor is not None:
            try:
                # 执行数据库的SQL语句
                if "SQL_DIRECT" in sqlHints.keys():
                    self.sqlCursor.execute_direct(sql, TimeOutLimit=self.timeout)
                elif "SQL_PREPARE" in sqlHints.keys():
                    self.sqlCursor.execute(sql, TimeOutLimit=self.timeout)
                else:
                    if self.testOptions.get("SQL_EXECUTE").upper() == "DIRECT":
                        self.sqlCursor.execute_direct(sql, TimeOutLimit=self.timeout)
                    else:
                        self.sqlCursor.execute(sql, TimeOutLimit=self.timeout)

                rowcount = 0
                sqlStatus = 0
                while True:
                    (title, result, headers, columnTypes, status,
                     fetchStatus, fetchedRowCount, sqlWarnings) = \
                        self.getcommandResult(self.sqlCursor, rowcount)
                    rowcount = fetchedRowCount
                    if "TESTCLI_DEBUG" in os.environ:
                        print("[DEBUG] headers=" + str(headers))
                        if result is not None:
                            for rowPos in range(0, len(result)):
                                for cellPos in range(0, len(result[rowPos])):
                                    print("[DEBUG] Cell[" + str(rowPos) + ":" +
                                          str(cellPos) + "]=[" + str(result[rowPos][cellPos]) + "]")

                    sqlErrorMessage = ""
                    # 如果Hints中有order字样，对结果进行排序后再输出
                    if "Order" in sqlHints.keys() and result is not None:
                        if "TESTCLI_DEBUG" in os.environ:
                            print("[DEBUG] Apply Sort for this result 2.")
                        # 不能用sorted函数，需要考虑None出现在列表中特定元素的问题
                        # l =  [(-32767,), (32767,), (None,), (0,)]
                        # l = sorted(l, key=lambda x: (x is None, x))
                        # '<' not supported between instances of 'NoneType' and 'int'
                        self.sortresult(result)

                    # 如果Hint中存在LogFilter，则结果集中过滤指定的输出信息
                    if "LogFilter" in sqlHints.keys() and result is not None:
                        for sqlFilter in sqlHints["LogFilter"]:
                            for item in result[:]:
                                if "TESTCLI_DEBUG" in os.environ:
                                    print("[DEBUG] Apply Filter: " + str(''.join(str(item))) +
                                          " with " + sqlFilter)
                                if re.match(sqlFilter, ''.join(str(item)), re.IGNORECASE):
                                    result.remove(item)
                                    continue

                    # 如果Hint中存在LogMask,则掩码指定的输出信息
                    if "LogMask" in sqlHints.keys() and result is not None:
                        for i in range(0, len(result)):
                            rowResult = list(result[i])
                            bDataChanged = False
                            for j in range(0, len(rowResult)):
                                if rowResult[j] is None:
                                    continue
                                output = str(rowResult[j])
                                for sqlMaskListString in sqlHints["LogMask"]:
                                    sqlMaskList = sqlMaskListString.split("=>")
                                    if len(sqlMaskList) == 2:
                                        sqlMaskPattern = sqlMaskList[0]
                                        sqlMaskTarget = sqlMaskList[1]
                                        if "TESTCLI_DEBUG" in os.environ:
                                            print("[DEBUG] Apply Mask: " + output +
                                                  " with " + sqlMaskPattern + "=>" + sqlMaskTarget)
                                        try:
                                            beforeReplace = str(rowResult[j])
                                            nIterCount = 0
                                            while True:
                                                # 循环多次替代，一直到没有可替代为止
                                                afterReplace = re.sub(sqlMaskPattern, sqlMaskTarget,
                                                                      beforeReplace, re.IGNORECASE)
                                                if afterReplace == beforeReplace or nIterCount > 99:
                                                    newOutput = afterReplace
                                                    break
                                                beforeReplace = afterReplace
                                                nIterCount = nIterCount + 1
                                            if newOutput != output:
                                                bDataChanged = True
                                                rowResult[j] = newOutput
                                        except re.error:
                                            if "TESTCLI_DEBUG" in os.environ:
                                                print('[DEBUG] traceback.print_exc():\n%s'
                                                      % traceback.print_exc())
                                                print('[DEBUG] traceback.format_exc():\n%s'
                                                      % traceback.format_exc())
                                    else:
                                        if "TESTCLI_DEBUG" in os.environ:
                                            print("[DEBUG] LogMask Hint Error: " + sqlHints["LogMask"])
                            if bDataChanged:
                                result[i] = tuple(rowResult)

                    # 返回SQL结果
                    if sqlStatus == 1:
                        yield {
                            "type": "error",
                            "message": sqlErrorMessage
                        }
                    else:
                        if self.testOptions.get('TERMOUT').upper() != 'OFF':
                            yield {
                                "type": "result",
                                "title": title,
                                "rows": result,
                                "headers": headers,
                                "columnTypes": columnTypes,
                                "status": status
                            }
                        else:
                            yield {
                                "type": "result",
                                "title": title,
                                "rows": [],
                                "headers": headers,
                                "columnTypes": columnTypes,
                                "status": status
                            }
                    if not fetchStatus:
                        break
            except SQLCliJDBCTimeOutException:
                # 处理超时时间问题
                if sql.upper() not in ["_EXIT", "_QUIT"]:
                    if self.timeOutMode == "SCRIPT":
                        sqlErrorMessage = "TestCli-000: Script Timeout " \
                                             "(" + str(self.scriptTimeOut) + \
                                             ") expired. Abort this command."
                    else:
                        sqlErrorMessage = "TestCli-000: SQL Timeout " \
                                             "(" + str(self.sqlTimeOut) + \
                                             ") expired. Abort this command."
                    yield {"type": "error", "message": sqlErrorMessage}
            except (SQLCliJDBCException, Exception) as je:
                sqlErrorMessage = str(je).strip()
                for errorPrefix in ["java.util.concurrent.ExecutionException:", ]:
                    if sqlErrorMessage.startswith(errorPrefix):
                        sqlErrorMessage = sqlErrorMessage[len(errorPrefix):].strip()
                for errorPrefix in ['java.sql.SQLSyntaxErrorException:',
                                    "java.sql.SQLException:",
                                    "java.sql.SQLInvalidAuthorizationSpecException:",
                                    "java.sql.SQLDataException:",
                                    "java.sql.SQLTransactionRollbackException:",
                                    "java.sql.SQLTransientConnectionException:",
                                    "java.sql.SQLFeatureNotSupportedException",
                                    "com.microsoft.sqlserver.jdbc.",
                                    "org.h2.jdbc.JdbcSQLSyntaxErrorException:"
                                    ]:
                    if sqlErrorMessage.startswith(errorPrefix):
                        sqlErrorMessage = sqlErrorMessage[len(errorPrefix):].strip()

                # 如果Hint中存在LogFilter，则输出的消息中过滤指定的输出信息
                if "LogFilter" in sqlHints.keys():
                    sqlMultiLineErrorMessage = sqlErrorMessage.split('\n')
                    bErrorMessageHasChanged = False
                    for sqlFilter in sqlHints["LogFilter"]:
                        for item in sqlMultiLineErrorMessage[:]:
                            if re.match(sqlFilter, ''.join(str(item)), re.IGNORECASE):
                                sqlMultiLineErrorMessage.remove(item)
                                bErrorMessageHasChanged = True
                                continue
                    if bErrorMessageHasChanged:
                        sqlErrorMessage = "\n".join(sqlMultiLineErrorMessage)

                # 如果Hint中存在LogMask,则掩码指定的输出信息
                if "LogMask" in sqlHints.keys():
                    sqlMultiLineErrorMessage = sqlErrorMessage.split('\n')
                    bErrorMessageHasChanged = False
                    for sqlMaskListString in sqlHints["LogMask"]:
                        sqlMaskList = sqlMaskListString.split("=>")
                        if len(sqlMaskList) == 2:
                            sqlMaskPattern = sqlMaskList[0]
                            sqlMaskTarget = sqlMaskList[1]
                            for pos2 in range(0, len(sqlMultiLineErrorMessage)):
                                newOutput = re.sub(sqlMaskPattern, sqlMaskTarget,
                                                   sqlMultiLineErrorMessage[pos2],
                                                   re.IGNORECASE)
                                if newOutput != sqlMultiLineErrorMessage[pos2]:
                                    bErrorMessageHasChanged = True
                                    sqlMultiLineErrorMessage[pos2] = newOutput
                        else:
                            if "TESTCLI_DEBUG" in os.environ:
                                raise TestCliException("LogMask Hint Error: " + sqlHints["LogMask"])
                    if bErrorMessageHasChanged:
                        sqlErrorMessage = "\n".join(sqlMultiLineErrorMessage)
                yield {"type": "error", "message": sqlErrorMessage}

    def runStatement(self, statement: str, commandScriptFile: str, nameSpace: str):
        # Remove spaces and EOL
        statement = statement.strip()
        formattedCommand = None
        if not statement:  # Empty string
            return

        # 记录脚本的文件名
        self.script = commandScriptFile

        # DEBUG模式下，打印当前计划要执行的语句
        if "TESTCLI_DEBUG" in os.environ:
            if self.testOptions.get("NAMESPACE") == "SQL":
                print("[DEBUG] SQL Command=[" + str(statement) + "]")
            elif self.testOptions.get("NAMESPACE") == "API":
                print("[DEBUG] API Command=[" + str(statement) + "]")

        # 开始解析语句
        try:
            ret_CommandSplitResults = []
            ret_CommandSplitResultsWithComments = []
            ret_CommandHints = []
            defaultNameSpace = self.testOptions.get("NAMESPACE")
            # 将所有的语句分拆开，按照行，依次投喂给解析器，以获得被Antlr分拆后的运行结果
            currentStatement = None
            currentStatementWithComments = None
            currentHints = []
            statementLines = statement.split('\n')
            for nPos in range(0, len(statementLines)):
                statementLine = statementLines[nPos]

                # 将上次没有结束的行和当前行放在一起, 再次看是否已经结束
                if currentStatement is None:
                    currentStatement = statementLine
                else:
                    currentStatement = currentStatement + '\n' + statementLine
                if currentStatementWithComments is None:
                    currentStatementWithComments = statementLine
                else:
                    currentStatementWithComments = currentStatementWithComments + '\n' + statementLine

                # 调用解析器解析语句
                if self.testOptions.get("NAMESPACE") == "SQL":
                    (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
                        = SQLAnalyze(currentStatement)
                elif self.testOptions.get("NAMESPACE") == "API":
                    (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
                        = APIAnalyze(currentStatement)
                else:
                    raise TestCliException("不支持的运行空间【" + str(nameSpace) + "】")

                # 语句没有结束
                if not isFinished:
                    # 如果语句还没有结束，则需要等待下一行输入
                    # 如果到了文件末尾，就没有必要继续等待，直接返回
                    if nPos == (len(statementLines) - 1):
                        if self.testOptions.get("NAMESPACE") == "SQL":
                            ret_CommandSplitResults.append(
                                {'name': 'SQL_UNKNOWN',
                                 'statement': currentStatement,
                                 'reason': "missing SQL_END at '<EOF>'"}
                            )
                        elif self.testOptions.get("NAMESPACE") == "API":
                            ret_CommandSplitResults.append(
                                {'name': 'API_UNKNOWN',
                                 'statement': currentStatement,
                                 'reason': "missing HTTP_END at '<EOF>'"}
                            )
                        # 解析前的语句
                        ret_CommandSplitResultsWithComments.append(currentStatementWithComments)
                        # 所有的提示信息
                        ret_CommandHints.append(currentHints)
                        # 清空语句的变量
                        currentStatement = None
                        currentStatementWithComments = None
                    continue

                # 语句已经结束
                if ret_CommandSplitResult is None:
                    # 解析的结果为空，可能的原因有：
                    #    这是一个空行，或者仅仅包含注释，那继续等待下一个有意义的行
                    #    这行已经发生了解析错误，但是由于我们的解析规则并不覆盖所有的数据库语句，所以就假设其为数据库语句
                    if ret_errorCode != 0:
                        # 语句已经出错
                        if self.testOptions.get("NAMESPACE") == "SQL":
                            # 对于SQL语句，不认识的语句要当作一个SQL使用
                            #   如果语句的最后一个字符是SQL终止符号，则认为语句结束
                            #   如果语句的最后一个字符不是SQL终止符号，继续等待
                            if currentStatement.strip().endswith(';') or currentStatement.strip().endswith('\n/'):
                                ret_CommandSplitResults.append(
                                    {'name': 'SQL_UNKNOWN',
                                     'statement': currentStatement,
                                     'reason': ret_errorMsg}
                                )
                                # 解析前的语句
                                ret_CommandSplitResultsWithComments.append(currentStatementWithComments)
                                # 所有的提示信息
                                ret_CommandHints.append(currentHints)
                                # 清空语句的变量
                                currentStatement = None
                                currentStatementWithComments = None
                            continue
                        elif self.testOptions.get("NAMESPACE") == "API":
                            # 对于API语句，不认识的语句肯定是出问题了
                            ret_CommandSplitResults.append(
                                {'name': 'API_UNKNOWN',
                                 'statement': currentStatement,
                                 'reason': ret_errorMsg}
                            )
                            # 解析前的语句
                            ret_CommandSplitResultsWithComments.append(currentStatementWithComments)
                            # 所有的提示信息
                            ret_CommandHints.append(currentHints)
                            # 清空语句的变量
                            currentStatementWithComments = None

                    # 没有任何有效的语句，可能是空行或者完全的注释
                    # 对于注释中的Hint信息需要保留下来
                    pattern = ""
                    if self.testOptions.get("NAMESPACE") == "SQL":
                        pattern = r"^(\s+)?--(\s+)?\[(\s+)?Hint(\s+)?\](.*)"
                    elif self.testOptions.get("NAMESPACE") == "API":
                        pattern = r"^(\s+)?//(\s+)?\[(\s+)?Hint(\s+)?\](.*)"
                    matchObj = re.match(pattern, statementLine, re.IGNORECASE)
                    if matchObj:
                        currentHints.append(matchObj.group(5).strip())
                    # 解析后的语句
                    ret_CommandSplitResults.append(None)
                    # 解析前的语句
                    ret_CommandSplitResultsWithComments.append(currentStatementWithComments)
                    # 对于非有效语句，Hint不在当前语句中体现，而是要等到下次有意义的语句进行处理
                    ret_CommandHints.append([])
                    # 清空语句的变量
                    currentStatement = None
                    currentStatementWithComments = None
                    continue
                else:
                    # 解析出来了真实有效的内容
                    if ret_CommandSplitResult["name"] == "USE":
                        self.testOptions.set("NAMESPACE", ret_CommandSplitResult["nameSpace"])
                    if self.testOptions.get("NAMESPACE") == "SQL":
                        # 对于SQL的CONNECT命令做特殊处理
                        if ret_CommandSplitResult["name"] == "CONNECT":
                            # 对于数据库连接命令，如果没有给出连接详细信息，并且指定了环境变量，附属环境变量到连接命令后
                            if "driver" not in ret_CommandSplitResult and "SQLCLI_CONNECTION_URL" in os.environ:
                                (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
                                    = SQLAnalyze(currentStatement + "@" + os.environ["SQLCLI_CONNECTION_URL"])
                    # 语句已经结束, 记录语句解析的结果
                    # 解析后的语句
                    ret_CommandSplitResults.append(ret_CommandSplitResult)
                    # 解析前的语句
                    ret_CommandSplitResultsWithComments.append(currentStatementWithComments)
                    # 所有的提示信息
                    ret_CommandHints.append(currentHints)
                    # 清空语句的变量
                    currentStatement = None
                    currentStatementWithComments = None
                    continue
        except Exception:
            if "TESTCLI_DEBUG" in os.environ:
                print('traceback.print_exc():\n%s' % traceback.print_exc())
                print('traceback.format_exc():\n%s' % traceback.format_exc())
            raise TestCliException("TestCli-000 Internal error. Parse failed.")

        # 解析过程中设置的NAMESPACE，解析后要还原，好保证执行的正确
        self.testOptions.set("NAMESPACE", defaultNameSpace)

        # 开始执行语句
        pos = 0
        while True:
            if pos == len(ret_CommandSplitResults):
                break

            # 记录命令开始时间
            startTime = time.time()

            # 首先打印原有语句
            if self.testOptions.get("NAMESPACE") == "SQL":
                formattedCommand = SQLFormatWithPrefix(ret_CommandSplitResultsWithComments[pos])
            if self.testOptions.get("NAMESPACE") == "API":
                formattedCommand = APIRequestStringFormatWithPrefix(ret_CommandSplitResultsWithComments[pos])

            # 如果是空语句，不需要执行，但可能是完全注释行
            # 也可能是一个解析错误的语句
            if ret_CommandSplitResults[pos] is None:
                yield {
                    "type": "parse",
                    "rawCommand": ret_CommandSplitResults[pos],
                    "formattedCommand": formattedCommand,
                    "rewrotedCommand": [],
                    "script": commandScriptFile
                }
                pos = pos + 1
                continue
            else:
                parseObject = dict(ret_CommandSplitResults[pos])

            # 如果在循环模式下，且循环条件已经不满足，则直接跳出
            if parseObject["name"] != "LOOP":
                if self.loopMode and not self.loopCondition:
                    pos = pos + 1
                    continue

            # 返回SQL的解析信息
            if commandScriptFile != "Console":
                # 如果是控制台显示，不再回显原命令，没有任何实际意义
                yield {
                    "type": "parse",
                    "rawCommand": ret_CommandSplitResults[pos],
                    "formattedCommand": formattedCommand,
                    "rewrotedCommand": [],
                    "script": commandScriptFile
                }

            # 处理超时时间问题
            if self.scriptTimeOut > 0:
                if self.scriptTimeOut <= time.time() - self.getStartTime():
                    commandErrorMessage = "TestCli-000: Script Timeout " \
                                         "(" + str(round(self.scriptTimeOut, 2)) + \
                                         ") expired. Abort this Script."
                    yield {"type": "error", "message": commandErrorMessage}
                    raise EOFError
                else:
                    if self.testOptions.get("NAMESPACE") == "SQL":
                        if self.sqlTimeOut > 0:
                            if self.scriptTimeOut - (time.time() - self.getStartTime()) < self.sqlTimeOut:
                                # 脚本超时剩余时间更少，执行较少的那个超时控制
                                self.timeOutMode = "SCRIPT"
                                self.timeout = self.scriptTimeOut - (time.time() - self.getStartTime())
                            else:
                                self.timeOutMode = "COMMAND"
                                self.timeout = self.sqlTimeOut
                        else:
                            self.timeOutMode = "SCRIPT"
                            self.timeout = self.scriptTimeOut - (time.time() - self.getStartTime())
                    if self.testOptions.get("NAMESPACE") == "API":
                        if self.apiTimeOut > 0:
                            if self.scriptTimeOut - (time.time() - self.getStartTime()) < self.apiTimeOut:
                                # 脚本超时剩余时间更少，执行较少的那个超时控制
                                self.timeOutMode = "SCRIPT"
                                self.timeout = self.scriptTimeOut - (time.time() - self.getStartTime())
                            else:
                                self.timeOutMode = "COMMAND"
                                self.timeout = self.apiTimeOut
                        else:
                            self.timeOutMode = "SCRIPT"
                            self.timeout = self.scriptTimeOut - (time.time() - self.getStartTime())
            elif self.testOptions.get("NAMESPACE") == "SQL" and self.sqlTimeOut > 0:
                # 没有设置SCRIPT的超时时间，只设置了COMMAND的超时时间
                self.timeOutMode = "COMMAND"
                self.timeout = self.sqlTimeOut
            elif self.testOptions.get("NAMESPACE") == "API" and self.apiTimeOut > 0:
                # 没有设置SCRIPT的超时时间，只设置了COMMAND的超时时间
                self.timeOutMode = "COMMAND"
                self.timeout = self.apiTimeOut
            else:
                # 什么超时时间都没有设置
                self.timeOutMode = None
                self.timeout = -1

            # 处理各种命令
            sqlKeyWords = ["SELECT", "DELETE", "UPDATE", "CREATE", "INSERT",
                           "DROP", "COMMIT", "ROLLBACK",
                           "PROCEDURE", "DECLARE", "BEGIN",
                           "SQL_UNKNOWN"]
            if parseObject["name"] == "ECHO":
                # 将后续内容回显到指定的文件中
                for commandResult in echo_input(
                        cls=self.cliHandler,
                        fileName=parseObject["param"],
                        block=parseObject["block"],
                ):
                    yield commandResult
            elif parseObject["name"] == "START":
                # 执行脚本文件
                for commandResult in executeFile(
                        cls=self.cliHandler,
                        scriptFile=parseObject["script"],
                        argv=parseObject["argv"],
                ):
                    yield commandResult
            elif parseObject["name"] in ["EXIT", "QUIT"]:
                # 执行脚本文件
                if "exitValue" in parseObject.keys():
                    exitValue = parseObject["exitValue"]
                else:
                    exitValue = 0
                for commandResult in exitApplication(
                        cls=self.cliHandler,
                        exitValue=exitValue
                ):
                    yield commandResult
            elif parseObject["name"] == "CONNECT":
                # 执行CONNECT命令
                if self.testOptions.get("NAMESPACE") == "SQL":
                    for commandResult in connectDb(
                            cls=self.cliHandler,
                            connectProperties=parseObject
                    ):
                        yield commandResult
                else:
                    yield {
                        "type": "error",
                        "message": "affadsfsad",
                        "script": commandScriptFile
                    }
            elif parseObject["name"] == "SET":
                # 执行SET命令
                for commandResult in setOptions(
                        cls=self.cliHandler,
                        options=parseObject
                ):
                    yield commandResult
            elif parseObject["name"] == "DISCONNECT":
                # 执行DISCONNECT命令
                if self.testOptions.get("NAMESPACE") == "SQL":
                    for commandResult in disconnectDb(
                            cls=self.cliHandler
                    ):
                        yield commandResult
                else:
                    yield {
                        "type": "error",
                        "message": "affadsfsad",
                        "script": commandScriptFile
                    }
            elif parseObject["name"] in sqlKeyWords:
                if self.ifMode and not self.ifCondition:
                    pos = pos + 1
                    continue
                sqlCommand = parseObject["statement"]
                # 根据语句中的变量或者其他定义信息来重写当前语句
                sqlCommand, rewrotedCommandList = rewriteSQLStatement(
                    cls=self.cliHandler,
                    statement=sqlCommand,
                    commandScriptFile=commandScriptFile
                )
                if len(rewrotedCommandList) != 0:
                    # 如果命令被发生了改写，要打印改写记录
                    yield {
                        "type": "parse",
                        "rawCommand": None,
                        "formattedCommand": None,
                        "rewrotedCommand": rewrotedCommandList,
                        "script": commandScriptFile
                    }

                # 处理Hints信息
                commandHintList = parseSQLHints(list(ret_CommandHints[pos]))

                # 执行SQL语句
                for result in self.executeSQLStatement(
                        sql=sqlCommand,
                        sqlHints=commandHintList,
                        startTime=0):
                    if result["type"] == "result":
                        lastCommandResult["rows"] = result["rows"]
                        lastCommandResult["headers"] = result["headers"]
                        lastCommandResult["message"] = result["status"]
                        lastCommandResult["errorCode"] = 0
                    if result["type"] == "error":
                        lastCommandResult["rows"] = []
                        lastCommandResult["headers"] = []
                        lastCommandResult["message"] = result["message"]
                        lastCommandResult["errorCode"] = 1
                    yield result
            elif parseObject["name"] in ["USE"]:
                for commandResult in userNameSpace(
                        cls=self.cliHandler,
                        nameSpace=parseObject["nameSpace"]
                ):
                    yield commandResult
            elif parseObject["name"] in ["SLEEP"]:
                for commandResult in cliSleep(
                        cls=self.cliHandler,
                        sleepTime=parseObject["sleepTime"]
                ):
                    yield commandResult
            elif parseObject["name"] in ["SPOOL"]:
                for commandResult in spool(
                        cls=self.cliHandler,
                        fileName=parseObject["file"]
                ):
                    yield commandResult
            elif parseObject["name"] in ["SESSION"]:
                for commandResult in sessionManage(
                        cls=self.cliHandler,
                        action=parseObject["action"],
                        sessionName=parseObject["sessionName"]
                ):
                    yield commandResult
            elif parseObject["name"] in ["SCRIPT"]:
                for commandResult in executeEmbeddScript(
                        cls=self.cliHandler,
                        block=parseObject["block"]
                ):
                    yield commandResult
            elif parseObject["name"] in ["ASSERT"]:
                for commandResult in assertExpression(
                        cls=self.cliHandler,
                        expression=parseObject["expression"]
                ):
                    yield commandResult
            elif parseObject["name"] in ["LOAD"]:
                if parseObject["option"] == "PLUGIN":
                    for commandResult in loadPlugin(
                            cls=self.cliHandler,
                            pluginFile=parseObject["pluginFile"]
                    ):
                        yield commandResult
                elif parseObject["option"] == "DRIVER":
                    for commandResult in loadDriver(
                            cls=self.cliHandler,
                            driverName=parseObject["driverName"],
                            driverFile=parseObject["driverFile"]
                    ):
                        yield commandResult
                elif parseObject["option"] == "MAP":
                    for commandResult in loadMap(
                            cls=self.cliHandler,
                            mapFile=parseObject["mapFile"]
                    ):
                        yield commandResult
            elif parseObject["name"] in ["HTTP"]:
                if self.ifMode and not self.ifCondition:
                    pos = pos + 1
                    continue
                # 根据语句中的变量或者其他定义信息来重写当前语句
                httpRequestTarget, rewrotedCommandList = rewriteAPIStatement(
                    cls=self.cliHandler,
                    requestObject=parseObject,
                    commandScriptFile=commandScriptFile
                )
                if len(rewrotedCommandList) != 0:
                    # 如果命令被发生了改写，要打印改写记录
                    yield {
                        "type": "parse",
                        "rawCommand": None,
                        "formattedCommand": None,
                        "rewrotedCommand": rewrotedCommandList,
                        "script": commandScriptFile
                    }

                # 处理Hints信息
                commandHintList = parseAPIHints(list(ret_CommandHints[pos]))

                # 执行HTTP请求
                for result in self.executeAPIStatement(
                        apiRequest=parseObject,
                        apiHints=commandHintList,
                        startTime=0):
                    if result["type"] == "result":
                        lastCommandResult.clear()
                        data = json.loads(result["status"])
                        lastCommandResult["data"] = data["content"]
                        lastCommandResult["status"] = data["status"]
                        lastCommandResult["errorCode"] = 0
                    if result["type"] == "error":
                        lastCommandResult["message"] = result["message"]
                        lastCommandResult["errorCode"] = 1
                    yield result
            elif parseObject["name"] in ["HOST"]:
                # 执行主机操作系统命令
                for result in executeLocalCommand(
                        cls=self.cliHandler,
                        command=parseObject["script"]
                ):
                    yield result
            elif parseObject["name"] in ["ENDIF"]:
                self.ifMode = False
                self.ifCondition = False
            elif parseObject["name"] in ["IF"]:
                expression = parseObject["expression"]
                try:
                    ret = evalExpression(self.cliHandler, expression)
                    if type(ret) == bool:
                        self.ifMode = True
                        if ret:
                            self.ifCondition = True
                        else:
                            self.ifCondition = False
                    else:
                        yield {
                            "type": "error",
                            "message": "Set condition fail. SyntaxError =>[not a bool expression]"
                        }
                except (SyntaxError, NameError) as ae:
                    yield {
                        "type": "error",
                        "message": "Set condition fail. SyntaxError =>[" + str(ae) + "]"
                    }
            elif parseObject["name"] in ["LOOP"]:
                if parseObject["rule"] == "END":
                    if not self.loopCondition:
                        self.loopMode = False
                    else:
                        pos = self.loopStartPos
                        continue
                elif parseObject["rule"] == "BREAK":
                    self.loopCondition = False
                elif parseObject["rule"] == "CONTINUE":
                    pos = self.loopStartPos
                    continue
                elif parseObject["rule"] == "BEGIN":
                    self.loopMode = True
                    self.loopStartPos = pos
                    self.loopCondition = not evalExpression(self.cliHandler, parseObject["UNTIL"])
            elif parseObject["name"] in ["WHENEVER"]:
                for result in setWheneverAction(
                        cls=self.cliHandler,
                        action=parseObject["action"],
                        exitCode=parseObject["exitCode"]
                ):
                    yield result
            elif parseObject["name"] in ["SSH"]:
                for result in executeSshRequest(
                        cls=self.cliHandler,
                        requestObject=parseObject,
                ):
                    yield result
            elif parseObject["name"] in ["JOB"]:
                for result in self.cliHandler.JobHandler.processRequest(
                        cls=self.cliHandler,
                        requestObject=parseObject,
                ):
                    yield result
            elif parseObject["name"] in ["UNKNOWN"]:
                yield {"type": "error",
                       "message": "TESTCLI_0000:  " + parseObject["reason"]}
            else:
                raise TestCliException("FDDFSFDFSDSFD " + str(parseObject))

            # 如果需要，打印语句执行时间
            endTime = time.time()
            lastCommandResult["elapsed"] = endTime - startTime

            # 记录SQL日志信息
            if self.testOptions.get("SILENT").upper() == 'OFF':
                if "status" in lastCommandResult:
                    commandStatus = lastCommandResult["status"]
                else:
                    commandStatus = 0
                if "errorMessage" in lastCommandResult:
                    errorMessage = lastCommandResult["errorMessage"]
                else:
                    errorMessage = ""
                yield {
                    "type": "statistics",
                    "startedTime": startTime,
                    "elapsed": endTime - startTime,
                    "thread_name": self.workerName,
                    "rawCommand": ret_CommandSplitResultsWithComments[pos],
                    "command": json.dumps(obj=parseObject, sort_keys=True, ensure_ascii=False),
                    "commandStatus": commandStatus,
                    "errorMessage": errorMessage,
                    "scenario" : self.scenario
                }

            # 开始执行下一个语句
            pos = pos + 1
