# -*- coding: utf-8 -*-
from ..globalvar import globalEmbeddScriptScope
from ..globalvar import lastCommandResult


# 执行Python脚本
def executeEmbeddScript(cls, block: str):
    # 定义全局的环境信息，保证在多次执行嵌入式脚本的时候，环境信息能够被保留
    sessionContext = {
        "dbConn": cls.db_conn.jconn if cls.db_conn is not None else None,
        "type": "result",
        "title": None,
        "rows": None,
        "headers": None,
        "columnTypes": None,
        "status": None
    }
    globalEmbeddScriptScope["sessionContext"] = sessionContext
    globalEmbeddScriptScope["lastCommandResult"] = lastCommandResult
    try:
        exec(block, globalEmbeddScriptScope)
    except Exception as se:
        yield {
            "type": "error",
            "message": repr(se),
        }
        return

    if sessionContext["type"] == "error":
        if "message" in sessionContext:
            errorMessage = sessionContext["message"]
        else:
            errorMessage = ""
        yield {
            "type": sessionContext["type"],
            "message": errorMessage
        }

    if sessionContext["type"] == "result":
        if "title" in sessionContext:
            resultTitle = sessionContext["title"]
        else:
            resultTitle = None
        if "rows" in sessionContext:
            resultRows = sessionContext["rows"]
        else:
            resultRows = None
        if "headers" in sessionContext:
            resultHeaders = sessionContext["headers"]
        else:
            resultHeaders = None
        if "columnTypes" in sessionContext:
            resultColumnTypes = sessionContext["columnTypes"]
        else:
            resultColumnTypes = None
        if "status" in sessionContext:
            resultStatus = sessionContext["status"]
        else:
            resultStatus = None
        yield {
            "type": sessionContext["type"],
            "title": resultTitle,
            "rows": resultRows,
            "headers": resultHeaders,
            "columnTypes": resultColumnTypes,
            "status": resultStatus,
        }
