# -*- coding: utf-8 -*-

globalEmbeddScriptScope = {}

# 内嵌脚本执行时候的命名空间
localEmbeddScriptScope = {}

# 最后一次执行后的结果
'''
    SQL Result:
    {
        "rows":
        "headers":
        "status":
        "elapsed": 
        "errorCode": 0
    }
    HTTP Result:
    {
        "status":
        "data":
        "errorCode": 0
    }
    Error:
    {
        "errorCode": 1
        "errorMsg":  errorMsg
    }
'''
lastCommandResult = {}
