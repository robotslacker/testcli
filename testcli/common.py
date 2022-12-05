# -*- coding: utf-8 -*-
import copy
import os
import re
from .sqlparse import SQLFormatWithPrefix
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


def parseSQLHints(commandHints: list):
    commandHintList = {}

    for commandHint in commandHints:
        # [Hint]  Scenario:XXXX   -- 相关SQL的Scenariox信息，仅仅作为日志信息供查看
        match_obj = re.search(
            r"^Scenario:(.*)", commandHint, re.IGNORECASE | re.DOTALL)
        if match_obj:
            senario = match_obj.group(1)
            # 如果只有一个内容， 规则是:Scenario:ScenarioName
            commandHintList["Scenario"] = senario
            continue

        # [Hint]  order           -- SQLCli将会把随后的SQL语句进行排序输出，原程序的输出顺序被忽略
        match_obj = re.search(r"^order", commandHint, re.IGNORECASE | re.DOTALL)
        if match_obj:
            commandHintList["Order"] = True
            continue

        # [Hint]  LogFilter      -- SQLCli会过滤随后显示的输出信息，对于符合过滤条件的，将会被过滤
        match_obj = re.search(
            r"^LogFilter(\s+)(.*)", commandHint, re.IGNORECASE | re.DOTALL)
        if match_obj:
            # 可能有多个Filter信息
            sqlFilter = match_obj.group(5).strip()
            if "LogFilter" in commandHintList:
                commandHintList["LogFilter"].append(sqlFilter)
            else:
                commandHintList["LogFilter"] = [sqlFilter, ]
            continue

        # [Hint]  LogMask      -- SQLCli会掩码随后显示的输出信息，对于符合掩码条件的，将会被掩码
        match_obj = re.search(
            r"^LogMask(\s+)(.*)", commandHint, re.IGNORECASE | re.DOTALL)
        if match_obj:
            sqlMask = match_obj.group(5).strip()
            if "LogMask" in commandHintList:
                commandHintList["LogMask"].append(sqlMask)
            else:
                commandHintList["LogMask"] = [sqlMask]
            continue

        # [Hint]  SQL_DIRECT   -- SQLCli执行的时候将不再尝试解析语句，而是直接解析执行
        match_obj = re.search(r"^SQL_DIRECT", commandHint, re.IGNORECASE | re.DOTALL)
        if match_obj:
            commandHintList["SQL_DIRECT"] = True
            continue

        # [Hint]  SQL_PREPARE   -- SQLCli执行的时候将首先尝试解析语句，随后执行
        match_obj = re.search(r"^SQL_PREPARE", commandHint, re.IGNORECASE | re.DOTALL)
        if match_obj:
            commandHintList["SQL_PREPARE"] = True
            continue
    return commandHintList


def parseAPIHints(commandHints: list):
    commandHintList = {}

    for commandHint in commandHints:
        # [Hint]  Scenario:XXXX   -- 相关SQL的Scenariox信息，仅仅作为日志信息供查看
        match_obj = re.search(
            r"^Scenario:(.*)", commandHint, re.IGNORECASE | re.DOTALL)
        if match_obj:
            senario = match_obj.group(1)
            # 如果只有一个内容， 规则是:Scenario:ScenarioName
            commandHintList["Scenario"] = senario
            continue

        # [Hint]  LogFilter      -- SQLCli会过滤随后显示的输出信息，对于符合过滤条件的，将会被过滤
        match_obj = re.search(
            r"^LogFilter(\s+)(.*)", commandHint, re.IGNORECASE | re.DOTALL)
        if match_obj:
            # 可能有多个Filter信息
            sqlFilter = match_obj.group(5).strip()
            if "LogFilter" in commandHintList:
                commandHintList["LogFilter"].append(sqlFilter)
            else:
                commandHintList["LogFilter"] = [sqlFilter, ]
            continue

        # [Hint]  LogMask      -- SQLCli会掩码随后显示的输出信息，对于符合掩码条件的，将会被掩码
        match_obj = re.search(
            r"^LogMask(\s+)(.*)", commandHint, re.IGNORECASE | re.DOTALL)
        if match_obj:
            sqlMask = match_obj.group(5).strip()
            if "LogMask" in commandHintList:
                commandHintList["LogMask"].append(sqlMask)
            else:
                commandHintList["LogMask"] = [sqlMask]
            continue

    return commandHintList