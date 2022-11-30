# -*- coding: utf-8 -*-
import copy
import os
import re
from .sqlparse import SQLFormatWithPrefix
from .apiparse import APIRequestStringFormatWithPrefix
from .apiparse import APIRequestObjectFormatWithPrefix
from .commands.assertExpression import evalExpression


def rewriteSQLStatement(cls, statement: str, commandScriptFile: str):
    # 命令可能会被多次改写
    rewrotedCommandHistory = []

    # 保留原脚本
    rawStatement = statement

    # 如果打开了回写，并且指定了输出文件，且SQL被改写过，输出改写后的SQL
    if cls.testOptions.get("TESTREWRITE").upper() == 'ON':
        while True:
            beforeRewriteStatement = statement
            afterRewriteStatement = cls.mappingHandler.RewriteSQL(commandScriptFile, beforeRewriteStatement)
            if beforeRewriteStatement != afterRewriteStatement:  # 命令已经发生了改变
                # 记录被改写的命令
                rewrotedCommandHistory.append(
                    SQLFormatWithPrefix("Your SQL has been changed to:\n" + afterRewriteStatement, 'REWROTED '))
                statement = afterRewriteStatement
            else:
                # 一直循环到没有任何东西可以被替换
                break

    while True:
        # 替换脚本中的变量信息
        # 替换： 一： 系统的环境变量,即{{env}}
        # 替换： 二:  系统内嵌脚本中的变量{{eval}}
        match_obj = re.search(r"{{(.*?)}}", statement, re.IGNORECASE | re.DOTALL)
        if match_obj:
            searchResult = str(match_obj.group(0))
            varName = str(match_obj.group(1)).strip()
            # 尝试本地变量
            try:
                evalResult = evalExpression(cls.cliHandler, varName)
                statement = statement.replace(searchResult, str(evalResult))
            except NameError:
                # 非环境变量
                pass
            # 尝试环境变量
            if varName in os.environ:
                statement = statement.replace(searchResult, os.environ[varName])
        else:
            # 没有任何可以替换的了
            break

    # 语句发生了变化
    if rawStatement != statement:
        # 记录被变量信息改写的命令
        rewrotedCommandHistory.append(
            SQLFormatWithPrefix("Your SQL has been changed to:\n" + statement, 'REWROTED '))

    return statement, rewrotedCommandHistory


def rewriteAPIStatement(cls, requestObject: [], commandScriptFile: str):
    # 命令可能会被多次改写
    rewrotedRequestObjects = []

    # 保留原脚本
    rawRequestObject = copy.copy(requestObject)

    httpRequestTarget = requestObject["httpRequestTarget"]
    if cls.testOptions.get("TESTREWRITE").upper() == 'ON':
        while True:
            afterRewriteStatement = cls.mappingHandler.RewriteSQL(
                commandScriptFile, httpRequestTarget)
            if httpRequestTarget == afterRewriteStatement:
                # 一直循环到没有任何东西可以被替换
                break
            else:
                httpRequestTarget = afterRewriteStatement

    while True:
        # 替换脚本中的变量信息
        # 替换： 一： 系统的环境变量,即{{env}}
        # 替换： 二:  系统内嵌脚本中的变量{{eval}}
        match_obj = re.search(r"{{(.*?)}}", httpRequestTarget, re.IGNORECASE | re.DOTALL)
        if match_obj:
            searchResult = str(match_obj.group(0))
            varName = str(match_obj.group(1)).strip()
            # 尝试本地变量
            try:
                evalResult = evalExpression(cls, varName)
                httpRequestTarget = httpRequestTarget.replace(searchResult, str(evalResult))
            except NameError:
                # 非环境变量
                pass
            # 尝试环境变量
            if varName in os.environ:
                httpRequestTarget = httpRequestTarget.replace(searchResult, os.environ[varName])
        else:
            # 没有任何可以替换的了
            break
    requestObject["httpRequestTarget"] = httpRequestTarget

    # 语句发生了变化
    if rawRequestObject != requestObject:
        # 记录被变量信息改写的命令
        rewrotedRequestObjects.append(
            APIRequestObjectFormatWithPrefix(
                headerPrefix="Your API has been changed to:\n",
                requestObject=requestObject,
                outputPrefix='REWROTED '))

    return requestObject, rewrotedRequestObjects
