# -*- coding: utf-8 -*-
from testcli.globalvar import globalEmbeddScriptScope
from testcli.globalvar import localEmbeddScriptScope
from testcli.globalvar import lastCommandResult


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
    localEmbeddScriptScope["sessionContext"] = sessionContext
    localEmbeddScriptScope["lastCommandResult"] = lastCommandResult
    exec(block, globalEmbeddScriptScope, localEmbeddScriptScope)

    yield {
        "type": sessionContext["type"],
        "title": sessionContext["title"],
        "rows": sessionContext["rows"],
        "headers": sessionContext["headers"],
        "columnTypes": sessionContext["columnTypes"],
        "status": sessionContext["status"],
    }

