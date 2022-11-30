# -*- coding: utf-8 -*-
from testcli.globalvar import globalEmbeddScriptScope
from testcli.globalvar import localEmbeddScriptScope
from testcli.globalvar import lastCommandResult


def assertExpression(cls, expression: str):
    try:
        ret = evalExpression(cls, expression)
        if type(ret) == bool:
            yield {
                "type": "result",
                "title": "",
                "rows": "",
                "headers": "",
                "columnTypes": "",
                "status": "Assert " + ("successful." if ret else "fail.")
            }
    except (SyntaxError, NameError) as ae:
        yield {
            "type": "result",
            "title": "",
            "rows": "",
            "headers": "",
            "columnTypes": "",
            "status": "Assert fail. SyntaxError =>[" + str(ae) + "]"
        }


def evalExpression(cls, expression: str):
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

    return eval(expression, globalEmbeddScriptScope, localEmbeddScriptScope)
