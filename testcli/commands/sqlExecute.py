# -*- coding: utf-8 -*-
import os
import datetime
import platform
import binascii
import decimal
from ..testcliexception import TestCliException
from ..sqlclijdbc import SQLCliJDBCTimeOutException
from ..sqlclijdbc import SQLCliJDBCException
from ..sqlclijdbc import SQLCliJDBCLargeObject


def getcommandResult(cls, rowcount):
    """
        获取当前游标的数据库运行结果集，并完成格式化

        返回的内容：
            title           输出内容的标题信息
            result          结果数据集，用一个二维的元组信息表示，((1,2),(3,4),(5,6),...)
                            每一行数据被记录在一个元组中，所有行的记录再被记录到整个的元组中
            headers         表头信息
                            数组。其维数一定和列数相同。 如["COL1", "COL2"]
            columnTypes     结果字段类型
                            数组。其维数一定和列数相同。 如["VARCHAR", "INTEGER"]
                            具体列表参考： sqlclijdbc.py中的_DEFAULT_CONVERTERS中信息
            status          输出的后提示信息，字符串格式
            FetchStatus     是否输出完成。
                            True 输出已经完成
                            False  输出仍未完成
            rowcount        共返回记录行数（累计，不是当前记录集返回数量）
            Warning         警告信息
    """
    title = headers = None
    fetchStatus = True
    cursor = cls.sqlCursor

    def format_column(p_column, p_columntype):
        if type(p_column) == float:
            return cls.testOptions.get("FLOAT_FORMAT") % p_column
        elif type(p_column) in (bool, str, int):
            return p_column
        elif type(p_column) == list:
            return p_column
        elif type(p_column) == datetime.date:
            columnFormat = cls.testOptions.get("DATE_FORMAT")
            if platform.system().lower() in ['windows', 'darwin']:
                columnFormat = columnFormat.replace("%04Y", "%Y")
            else:
                columnFormat = columnFormat.replace("%Y", "%04Y")
            return p_column.strftime(columnFormat)
        elif type(p_column) == datetime.datetime:
            if p_columntype in ["TIMESTAMP_WITH_TIMEZONE",
                                "TIME_WITH_TIMEZONE",
                                "TIMESTAMP_WITH_LOCAL_TIME_ZONE"]:
                columnFormat = cls.testOptions.get("DATETIME-TZ_FORMAT")
            else:
                columnFormat = cls.testOptions.get("DATETIME_FORMAT")
            if platform.system().lower() in ['windows', 'darwin']:
                columnFormat = columnFormat.replace("%04Y", "%Y")
            else:
                columnFormat = columnFormat.replace("%Y", "%04Y")
            return p_column.strftime(columnFormat)
        elif type(p_column) == datetime.time:
            return p_column.strftime(cls.testOptions.get("TIME_FORMAT"))
        elif type(p_column) == bytearray:
            if p_columntype == "BLOB":
                columnTrimedLength = int(cls.testOptions.get("LOB_LENGTH"))
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
            if cls.testOptions.get("DECIMAL_FORMAT") != "":
                return cls.testOptions.get("DECIMAL_FORMAT") % p_column
            else:
                return p_column
        elif type(p_column) == SQLCliJDBCLargeObject:
            trimedLength = int(cls.testOptions.get("LOB_LENGTH"))
            if trimedLength < 4:
                trimedLength = 4
            if trimedLength > p_column.getObjectLength():
                if p_column.getColumnTypeName().upper().find("CLOB") != -1:
                    dataValue = p_column.getData(1, p_column.getObjectLength())
                    return dataValue
                elif p_column.getColumnTypeName().upper().find("BLOB") != -1:
                    dataValue = p_column.getData(1, p_column.getObjectLength())
                    if dataValue is not None:
                        dataValue = binascii.b2a_hex(dataValue)
                        dataValue = dataValue.decode()
                        return "0x" + dataValue
                    else:
                        return None
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
        arraySize = int(cls.testOptions.get("SQL_FETCHSIZE"))
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
                    if cls.testOptions.get('OUTPUT_SORT_ARRAY') == "ON":
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

    if cls.testOptions.get('FEEDBACK').upper() == 'ON' and status is not None:
        status = status.format(rowcount, "" if rowcount in [0, 1] else "s")
    else:
        status = None
    return title, result, headers, columnTypes, status, fetchStatus, rowcount, cursor.warnings


def executeSQLStatement(cls, sql: str, sqlHints):
    """
    返回内容：
        错误情况下：
        {
            "type": "error",
            "message": sqlErrorMessage
        }
        正确情况下：
        {
            "type": "result",                 固定字符串标志
            "title": title,                   字符串，表示输出的标题信息
            "rows": result,                   返回结果集
            "rowPos": rowPos                  多段返回中，当前所在行在总体结果集中的开始位置
            "headers": headers,               返回结果集的字段标题信息
            "columnTypes": columnTypes,       返回结果集的字段类型信息
            "status": status                  返回结果集的状态返回信息
        }
    """

    # 进入到SQL执行阶段, 开始执行SQL语句
    if cls.sqlConn:
        # 打开游标
        cls.sqlCursor = cls.sqlConn.cursor()
    else:
        # 进入到SQL执行阶段，不是特殊命令, 数据库连接也不存在, 直接报错
        if cls.testOptions.get("WHENEVER_ERROR") == "EXIT":
            raise TestCliException("Not Connected. ")
        else:
            yield {
                "type": "error",
                "message": "Not connected. "
            }

    # 执行正常的SQL语句
    if cls.sqlCursor is not None:
        try:
            # 执行数据库的SQL语句
            if "SQL_DIRECT" in sqlHints.keys():
                cls.sqlCursor.execute_direct(sql, TimeOutLimit=cls.timeout)
            elif "SQL_PREPARE" in sqlHints.keys():
                cls.sqlCursor.execute(sql, TimeOutLimit=cls.timeout)
            else:
                if cls.testOptions.get("SQL_EXECUTE").upper() == "DIRECT":
                    cls.sqlCursor.execute_direct(sql, TimeOutLimit=cls.timeout)
                else:
                    cls.sqlCursor.execute(sql, TimeOutLimit=cls.timeout)

            rowcount = 0
            sqlStatus = 0
            rowPos = 0    # 多段返回的结果集中，当前返回部分在多段结果集中的开始位置
            while True:
                (title, result, headers, columnTypes, status,
                 fetchStatus, fetchedRowCount, sqlWarnings) = \
                    getcommandResult(
                        cls=cls,
                        rowcount=rowcount
                    )
                rowcount = fetchedRowCount
                if "TESTCLI_DEBUG" in os.environ:
                    print("[DEBUG] headers=" + str(headers))
                    if result is not None:
                        for rowPos in range(0, len(result)):
                            for cellPos in range(0, len(result[rowPos])):
                                print("[DEBUG] Cell[" + str(rowPos) + ":" +
                                      str(cellPos) + "]=[" + str(result[rowPos][cellPos]) + "]")

                sqlErrorMessage = ""

                # 返回SQL结果
                if sqlStatus == 1:
                    yield {
                        "type": "error",
                        "message": sqlErrorMessage
                    }
                else:
                    yield {
                        "type": "result",
                        "title": title,
                        "rows": result,
                        "rowPos": rowPos,
                        "headers": headers,
                        "columnTypes": columnTypes,
                        "status": status
                    }
                    if result is not None:
                        rowPos = rowPos + len(result)
                if not fetchStatus:
                    break
        except SQLCliJDBCTimeOutException:
            # 处理超时时间问题
            if sql.upper() not in ["_EXIT", "_QUIT"]:
                if cls.timeOutMode == "SCRIPT":
                    sqlErrorMessage = "Testcli-0000: Script Timeout " \
                                      "(" + str(cls.scriptTimeOut) + \
                                      ") expired. Abort this command."
                else:
                    sqlErrorMessage = "Testcli-0000: SQL Timeout " \
                                      "(" + str(cls.sqlTimeOut) + \
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
                                "org.h2.jdbc.JdbcSQLSyntaxErrorException:",
                                "dm.jdbc.driver.DMException:",
                                ]:
                if sqlErrorMessage.startswith(errorPrefix):
                    sqlErrorMessage = sqlErrorMessage[len(errorPrefix):].strip()
            yield {"type": "error", "message": sqlErrorMessage}
