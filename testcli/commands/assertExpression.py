# -*- coding: utf-8 -*-
from ..globalvar import globalEmbeddScriptScope
from ..globalvar import lastCommandResult


def assertExpression(cls, expression: str, assertName: str):
    try:
        ret = evalExpression(cls, expression)
        if ret:
            if assertName is None:
                status = "Assert successful."
            else:
                status = "Assert [" + assertName + "] successful."
        else:
            if assertName is None:
                status = "Assert fail."
            else:
                status = "Assert [" + assertName + "] fail."
        if ret:
            yield {
                "type": "result",
                "title": "",
                "rows": "",
                "headers": "",
                "columnTypes": "",
                "status": status
            }
        else:
            yield {
                "type": "error",
                "message": status
            }
    except Exception as ae:
        yield {
            "type": "error",
            "message": "Assert fail. SyntaxError =>[" + str(ae) + "]"
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
    globalEmbeddScriptScope["sessionContext"] = sessionContext
    globalEmbeddScriptScope["lastCommandResult"] = lastCommandResult

    return eval(expression, globalEmbeddScriptScope)
