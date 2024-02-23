# -*- coding: utf-8 -*-
import os
from ..commands.compare import compareDefaultOption
from ..testcliexception import TestCliException


# 设置一些选项
def setOptions(cls, options):
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

    if optionName.upper() == "JOBMANAGER":
        # JOBMANAGER无法通过SET命令来设置
        yield {
            "type": "error",
            "message": "Can't update this option with set command. Please use '_JOB JOBMANAGER ON|OFF'."
        }
        return
    if optionName.upper() == "MONITORMANAGER":
        # MONITORMANAGER无法通过SET命令来设置
        yield {
            "type": "error",
            "message": "Can't update this option with set command. Please use '_MONITOR MONITORMANAGER ON|OFF'."
        }
        return
    if optionName.upper() == "WHENEVER_ERROR":
        # WHENEVER无法通过SET命令来设置
        yield {
            "type": "error",
            "message": "Can't update this option with set command. "
                       "Please use '_WHENEVER ERROR <EXIT <int> | CONTINUE>'."
        }
        return

    # 以下参数只能为ON或者OFF
    if optionName.upper() in ["DEBUG", "TIMING", "TIME", "ECHO", "PAGE", "TERMOUT", "FEEDBACK",
                              "OUTPUT_SORT_ARRAY", "OUTPUT_CSV_HEADER", "SILENT"]:
        if optionValue.upper() not in ['ON', 'OFF']:
            yield {
                "type": "error",
                "message": "Option is ON/OFF only'."
            }
            return

    # 以下参数只能为整形
    if optionName.upper() in ["SQL_FETCHSIZE", "LOB_LENGTH", "SQLCONN_RETRYTIMES"]:
        try:
            optionValue = int(str(optionValue))
            if optionValue <= 0:
                yield {
                    "type": "error",
                    "message": "Option is valid positive integer only."
                }
                return
        except ValueError:
            yield {
                "type": "error",
                "message": "Option is valid integer only."
            }
            return
    if optionName.upper() in ["SCRIPT_TIMEOUT", "SQL_TIMEOUT", "API_TIMEOUT"]:
        try:
            optionValue = int(str(optionValue))
            if optionValue <= 0 and optionValue != -1:
                yield {
                    "type": "error",
                    "message": "Option is valid positive integer(or -1 means unlimited) only."
                }
                return
        except ValueError:
            yield {
                "type": "error",
                "message": "Option is valid integer only."
            }
            return

    # 处理Compare算法选项
    if optionName.upper() == "COMPARE_DEFAULT_METHOD":
        # 设置Compare的默认算法
        optionValue = str(optionValue)
        if optionValue.strip().upper() not in ["AUTO", "MYERS", "DIFFLIB", "LCS"]:
            yield {
                "type": "error",
                "message": "Available option are ['AUTO', 'MYERS', 'DIFFLIB', 'LCS']."
            }
            return
        compareDefaultOption["algorithm"] = str(optionValue)

    # 处理DEBUG选项
    if optionName.upper() == "DEBUG":
        if optionValue.upper() == 'ON':
            os.environ['TESTCLI_DEBUG'] = "1"
        else:
            if 'TESTCLI_DEBUG' in os.environ:
                del os.environ['TESTCLI_DEBUG']
        yield {
            "type": "result",
            "title": None,
            "rows": None,
            "headers": None,
            "columnTypes": None,
            "status": None
        }
        return

    # 处理AUTOCOMMIT选项
    if optionName.upper() == "AUTOCOMMIT":
        if cls.db_conn is None:
            raise TestCliException("Not connected.")
        if optionValue.upper() == 'FALSE':
            cls.db_conn.setAutoCommit(False)
        elif optionValue.upper() == 'TRUE':
            cls.db_conn.setAutoCommit(True)
        else:
            raise TestCliException("Unknown option [" + str(optionValue) + "]. True/False only.")
        yield {
            "type": "result",
            "title": None,
            "rows": None,
            "headers": None,
            "columnTypes": None,
            "status": None
        }
        return

    # 对于子进程，连接到JOB管理服务
    if optionName.upper() == "JOBMANAGER_METAURL":
        if cls.testOptions.get("JOBMANAGER") == "ON":
            raise TestCliException("You can't act as worker rule while option JOBMANAGER is ON.")
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
        yield {
            "type": "result",
            "title": None,
            "rows": None,
            "headers": None,
            "columnTypes": None,
            "status": None
        }
        return

    # 查看是否属于定义的选项
    if cls.testOptions.get(optionName.upper()) is not None:
        cls.testOptions.set(optionName.upper(), optionValue)
        yield {
            "type": "result",
            "title": None,
            "rows": None,
            "headers": None,
            "columnTypes": None,
            "status": None
        }
        return
    else:
        # 不认识的配置选项
        yield {
            "type": "error",
            "message": "Unknown option [" + str(optionName) + "] ."
        }
        return
