# -*- coding: utf-8 -*-
import os
from ..testcliexception import TestCliException
from ..sqlclijdbc import SQLCliJDBCTimeOutException
from ..sqlclijdbc import SQLCliJDBCException


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
            "type": "result",
            "title": title,
            "rows": result,
            "headers": headers,
            "columnTypes": columnTypes,
            "status": status
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
            while True:
                (title, result, headers, columnTypes, status,
                 fetchStatus, fetchedRowCount, sqlWarnings) = \
                    cls.getcommandResult(cls.sqlCursor, rowcount)
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
                        "headers": headers,
                        "columnTypes": columnTypes,
                        "status": status
                    }
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
