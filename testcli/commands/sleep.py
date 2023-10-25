# -*- coding: utf-8 -*-
import time
from ..sqlclijdbc import SQLCliJDBCTimeOutException


# 休息一段时间
def cliSleep(cls, sleepTime):
    try:
        sleepTime = int(sleepTime)
    except ValueError:
        yield {
            "type": "error",
            "message": "Sleep time must be valid positive integer.",
        }
        return

    sleepTimeOut = -1

    nameSpace = cls.testOptions.get("NAMESPACE")
    scriptTimeOut = int(cls.testOptions.get("SCRIPT_TIMEOUT"))
    if nameSpace == "SQL":
        sqlTimeOut = int(cls.testOptions.get("SQL_TIMEOUT"))
        if scriptTimeOut != -1:
            if scriptTimeOut < sqlTimeOut:
                sleepTimeOut = scriptTimeOut
        else:
            if sqlTimeOut != -1:
                sleepTimeOut = sqlTimeOut
    if nameSpace == "API":
        apiTimeOut = int(cls.testOptions.get("API_TIMEOUT"))
        if scriptTimeOut != -1:
            if scriptTimeOut < apiTimeOut:
                sleepTimeOut = scriptTimeOut
        else:
            if apiTimeOut != -1:
                sleepTimeOut = apiTimeOut

    if sleepTime <= 0:
        message = "Parameter must be a valid number, sleep [seconds]."
        return [{
            "type": "result",
            "title": None,
            "rows": None,
            "headers": None,
            "columnTypes": None,
            "status": message
        }]
    if sleepTimeOut != -1 and sleepTimeOut < sleepTime:
        # 有超时限制，最多休息到超时的时间
        time.sleep(sleepTimeOut)
        raise SQLCliJDBCTimeOutException("TimeOut")
    else:
        time.sleep(sleepTime)
    return [{
        "type": "result",
        "title": None,
        "rows": None,
        "headers": None,
        "columnTypes": None,
        "status": None
    }]
