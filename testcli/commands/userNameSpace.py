# -*- coding: utf-8 -*-


# 切换程序运行空间
def userNameSpace(cls, nameSpace: str):
    cls.testOptions.set("NAMESPACE", nameSpace)
    yield {
        "type": "result",
        "title": None,
        "rows": None,
        "headers": None,
        "columnTypes": None,
        "status": "Current NameSpace: " + str(nameSpace) + "."
    }
