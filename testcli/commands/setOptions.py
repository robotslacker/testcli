# -*- coding: utf-8 -*-
import os
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

    # 处理DEBUG选项
    if optionName.upper() == "DEBUG":
        if optionValue.upper() == 'ON':
            os.environ['TESTCLI_DEBUG'] = "1"
        elif optionValue.upper() == 'OFF':
            if 'TESTCLI_DEBUG' in os.environ:
                del os.environ['TESTCLI_DEBUG']
        else:
            raise TestCliException("SQLCLI-00000: "
                                   "Unknown option [" + str(optionValue) + "]. ON/OFF only.")
        return [{
            "type": "result",
            "title": None,
            "rows": None,
            "headers": None,
            "columnTypes": None,
            "status": None
        }, ]

    # 处理AUTOCOMMIT选项
    if optionName.upper() == "AUTOCOMMIT":
        if cls.db_conn is None:
            raise TestCliException("Not connected.")
        if optionValue.upper() == 'FALSE':
            cls.db_conn.setAutoCommit(False)
        elif optionValue.upper() == 'TRUE':
            cls.db_conn.setAutoCommit(True)
        else:
            raise TestCliException("SQLCLI-00000: "
                                   "Unknown option [" + str(optionValue) + "]. True/False only.")
        return [{
            "type": "result",
            "title": None,
            "rows": None,
            "headers": None,
            "columnTypes": None,
            "status": None
        }, ]

    # 对于子进程，连接到JOB管理服务
    if optionName.upper() == "JOBMANAGER_METAURL":
        if cls.testOptions.get("JOBMANAGER") == "ON":
            raise TestCliException("SQLCLI-00000: "
                                   "You can't act as worker rule while option JOBMANAGER is ON")
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
        return [{
            "type": "result",
            "title": None,
            "rows": None,
            "headers": None,
            "columnTypes": None,
            "status": None
        }, ]

    # 如果特殊的选项，有可能时用户自己定义的变量
    if optionName.startswith('@'):
        cls.testOptions.set(optionName[1], optionValue)
        return [{
            "type": "result",
            "title": None,
            "rows": None,
            "headers": None,
            "columnTypes": None,
            "status": None
        }, ]

    # 查看是否属于定义的选项
    if cls.testOptions.get(optionName.upper()) is not None:
        cls.testOptions.set(optionName.upper(), optionValue)
        return [{
            "type": "result",
            "title": None,
            "rows": None,
            "headers": None,
            "columnTypes": None,
            "status": None
        }, ]
    else:
        # 不认识的配置选项按照SQL命令处理
        raise TestCliException("SQLCLI-00000: "
                               "Unknown option [" + str(optionValue) + "] .")
