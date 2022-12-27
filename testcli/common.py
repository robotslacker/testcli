# -*- coding: utf-8 -*-
import copy
import os
import re
from .sqlparse import SQLFormatWithPrefix
from .apiparse import APIRequestObjectFormatWithPrefix
from .commands.assertExpression import evalExpression


def rewriteHintStatement(cls, statement: str, commandScriptFile: str):
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
                    SQLFormatWithPrefix("Your hint has been changed to:\n" + afterRewriteStatement, 'REWROTED '))
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
                evalResult = evalExpression(cls, varName)
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
        rewrotedCommandHistory.append(statement)

    return statement, rewrotedCommandHistory


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
                evalResult = evalExpression(cls, varName)
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
    httpRequestTarget = rawRequestObject["httpRequestTarget"]

    if "contents" in rawRequestObject:
        httpRequestContents = copy.copy(rawRequestObject["contents"])
    else:
        httpRequestContents = None
    if "httpFields" in rawRequestObject:
        httpRequestFields = copy.copy(rawRequestObject["httpFields"])
    else:
        httpRequestFields = None
    if cls.testOptions.get("TESTREWRITE").upper() == 'ON':
        # 替换Mapping文件中Request的Header
        while True:
            afterRewriteStatement = cls.mappingHandler.RewriteCommand(
                commandScriptFile, httpRequestTarget)
            if httpRequestTarget == afterRewriteStatement:
                # 一直循环到没有任何东西可以被替换
                break
            else:
                httpRequestTarget = afterRewriteStatement

        # 替换Mapping文件中正文中的信息
        if httpRequestContents is not None:
            for nPos in range(0, len(httpRequestContents)):
                while True:
                    afterRewriteStatement = cls.mappingHandler.RewriteCommand(
                        commandScriptFile, httpRequestContents[nPos])
                    if httpRequestContents[nPos] == afterRewriteStatement:
                        # 一直循环到没有任何东西可以被替换
                        break
                    else:
                        httpRequestContents[nPos] = afterRewriteStatement

        # 替换Mapping文件中Fields信息
        if httpRequestFields is not None:
            for key, value in httpRequestFields.items():
                originFieldName = key
                # 替换Fields中的Field字段
                while True:
                    afterRewriteStatement = cls.mappingHandler.RewriteCommand(commandScriptFile, key)
                    if key == afterRewriteStatement:
                        # 一直循环到没有任何东西可以被替换
                        break
                    else:
                        key = afterRewriteStatement
                # 替换Fields中的Value字段
                while True:
                    afterRewriteStatement = cls.mappingHandler.RewriteCommand(commandScriptFile, value)
                    if value == afterRewriteStatement:
                        # 一直循环到没有任何东西可以被替换
                        break
                    else:
                        value = afterRewriteStatement
                # 替换Key和Value的内容
                if key != originFieldName:
                    del httpRequestFields[originFieldName]
                httpRequestFields[key] = value

    # 根据环境信息替换Request的Header
    while True:
        # 替换脚本中的变量信息
        # 替换： 一： 系统的环境变量,即{{env}}
        # 替换： 二:  系统内嵌脚本中的变量{{eval}}
        match_obj = re.search(r"{{(.*?)}}", httpRequestTarget, re.IGNORECASE | re.DOTALL)
        if match_obj:
            rawHttpRequestTarget = httpRequestTarget
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

            # 如果没有能够替换完成，也不会重复循环，直接标记为不认识的变量 #UNDEFINE_VAR#
            if rawHttpRequestTarget == httpRequestTarget:
                httpRequestTarget = httpRequestTarget.replace(searchResult, "#UNDEFINE_VAR#")
        else:
            # 没有任何可以替换的了
            break

    # 根据环境信息替换Request的Contents
    if httpRequestContents is not None:
        for nPos in range(0, len(httpRequestContents)):
            while True:
                rawHttpRequestContent = httpRequestContents[nPos]
                match_obj = re.search(r"{{(.*?)}}", httpRequestContents[nPos], re.IGNORECASE | re.DOTALL)
                if match_obj:
                    searchResult = str(match_obj.group(0))
                    varName = str(match_obj.group(1)).strip()
                    # 尝试本地变量
                    try:
                        evalResult = evalExpression(cls, varName)
                        httpRequestContents[nPos] = httpRequestContents[nPos].replace(searchResult, str(evalResult))
                    except NameError:
                        # 非环境变量
                        pass
                    # 尝试环境变量
                    if varName in os.environ:
                        httpRequestContents[nPos] = httpRequestContents[nPos].replace(searchResult, os.environ[varName])

                    # 如果没有能够替换完成，也不会重复循环，直接标记为不认识的变量 #UNDEFINE_VAR#
                    if rawHttpRequestContent == httpRequestContents[nPos]:
                        httpRequestContents[nPos] = httpRequestContents[nPos].replace(searchResult, "#UNDEFINE_VAR#")
                else:
                    # 没有任何可以替换的了
                    break

    # 根据环境信息替换Request的Fields
    if httpRequestFields is not None:
        for key, value in httpRequestFields.items():
            # 替换Fields中的Field字段
            originFieldName = key
            while True:
                rawFieldName = key
                match_obj = re.search(r"{{(.*?)}}", key, re.IGNORECASE | re.DOTALL)
                if match_obj:
                    searchResult = str(match_obj.group(0))
                    varName = str(match_obj.group(1)).strip()
                    # 尝试本地变量
                    try:
                        evalResult = evalExpression(cls, varName)
                        key = key.replace(searchResult, str(evalResult))
                    except NameError:
                        # 非环境变量
                        pass
                    # 尝试环境变量
                    if varName in os.environ:
                        key = key.replace(searchResult, os.environ[varName])

                    # 如果没有能够替换完成，也不会重复循环，直接标记为不认识的变量 #UNDEFINE_VAR#
                    if rawFieldName == key:
                        key = key.replace(searchResult, "#UNDEFINE_VAR#")
                else:
                    # 没有任何可以替换的了
                    break
            # 替换Fields中的Value字段
            while True:
                rawFieldValue = value
                match_obj = re.search(r"{{(.*?)}}", value, re.IGNORECASE | re.DOTALL)
                if match_obj:
                    searchResult = str(match_obj.group(0))
                    varName = str(match_obj.group(1)).strip()
                    # 尝试本地变量
                    try:
                        evalResult = evalExpression(cls, varName)
                        value = value.replace(searchResult, str(evalResult))
                    except NameError:
                        # 非环境变量
                        pass
                    # 尝试环境变量
                    if varName in os.environ:
                        value = value.replace(searchResult, os.environ[varName])

                    # 如果没有能够替换完成，也不会重复循环，直接标记为不认识的变量 #UNDEFINE_VAR#
                    if rawFieldValue == value:
                        value = value.replace(searchResult, "#UNDEFINE_VAR#")
                else:
                    # 没有任何可以替换的了
                    break

            # 替换Key和Value的内容
            if key != originFieldName:
                del httpRequestFields[originFieldName]
            httpRequestFields[key] = value

    requestObject["httpRequestTarget"] = httpRequestTarget
    if httpRequestContents is not None:
        requestObject["contents"] = httpRequestContents
    if httpRequestFields is not None:
        requestObject["httpFields"] = httpRequestFields

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

        # [Hint]  order           -- TestCli将会把随后的SQL语句进行排序输出，原程序的输出顺序被忽略
        match_obj = re.search(r"^order", commandHint, re.IGNORECASE | re.DOTALL)
        if match_obj:
            commandHintList["Order"] = True
            continue

        # [Hint]  LogFilter      -- TestCli会过滤随后显示的输出信息，对于符合过滤条件的，将会被过滤
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

        # [Hint]  LogMask      -- TestCli会掩码随后显示的输出信息，对于符合掩码条件的，将会被掩码
        match_obj = re.search(
            r"^LogMask(\s+)(.*)", commandHint, re.IGNORECASE | re.DOTALL)
        if match_obj:
            sqlMask = match_obj.group(5).strip()
            if "LogMask" in commandHintList:
                commandHintList["LogMask"].append(sqlMask)
            else:
                commandHintList["LogMask"] = [sqlMask]
            continue

        # [Hint]  SQL_DIRECT   -- TestCli执行的时候将不再尝试解析语句，而是直接解析执行
        match_obj = re.search(r"^SQL_DIRECT", commandHint, re.IGNORECASE | re.DOTALL)
        if match_obj:
            commandHintList["SQL_DIRECT"] = True
            continue

        # [Hint]  SQL_PREPARE   -- TestCli执行的时候将首先尝试解析语句，随后执行
        match_obj = re.search(r"^SQL_PREPARE", commandHint, re.IGNORECASE | re.DOTALL)
        if match_obj:
            commandHintList["SQL_PREPARE"] = True
            continue
    return commandHintList


def parseAPIHints(commandHints: list):
    commandHintList = {}

    for commandHint in commandHints:
        # [Hint]  Scenario:XXXX   -- 相关命令的Scenario信息
        match_obj = re.search(
            r"^Scenario:(.*)", commandHint, re.IGNORECASE | re.DOTALL)
        if match_obj:
            senario = match_obj.group(1)
            # 如果只有一个内容， 规则是:Scenario:ScenarioName
            commandHintList["Scenario"] = senario
            continue

        # [Hint]  LogFilter      -- TestCli会过滤随后显示的输出信息，对于符合过滤条件的，将会被过滤
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

        # [Hint]  LogMask      -- TestCli会掩码随后显示的输出信息，对于符合掩码条件的，将会被掩码
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
