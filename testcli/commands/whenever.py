# -*- coding: utf-8 -*-


# 切换程序运行空间
def setWheneverAction(cls, action: str, exitCode: int = 0):
    if action.upper().strip() == "EXIT":
        cls.breakWithError = True
        cls.breakErrorCode = exitCode
        cls.testOptions.set("WHENEVER_ERROR", "EXIT " + str(exitCode))
    else:
        cls.breakWithError = False
        cls.breakErrorCode = 0
        cls.testOptions.set("WHENEVER_ERROR", "CONTINUE")
    yield {
        "type": "result",
        "title": None,
        "rows": None,
        "headers": None,
        "columnTypes": None,
        "status": None
    }
