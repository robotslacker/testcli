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
    SQL Error:
    {
        "errorCode": 1
        "message":  errorMsg
    }
    HTTP Result:
    {
        "status":
        "content":
        "errorCode": 0
    }
    HTTP Error:
    {
        "errorCode": 1
        "errorMsg":  errorMsg
    }
'''
lastCommandResult = {}
