# -*- coding: utf-8 -*-
import copy
import os
import re
from .sqlparse import SQLFormatWithPrefix
from .apiparse import APIRequestObjectFormatWithPrefix
from .commands.assertExpression import evalExpression


def sortresult(result):
    """
        数组排序

        不能用sorted函数，需要考虑None出现在列表中特定元素的问题
        排序遵循空值最大原则
    """
    for i in range(len(result) - 1, 0, -1):
        for j in range(i - 1, -1, -1):
            bNeedExchange = False
            for k in range(0, len(result[i])):
                if len(result[i]) != len(result[j]):
                    return
                if result[i][k] is None and result[j][k] is None:
                    # 两边都是空值
                    continue
                if result[i][k] is None and result[j][k] is not None:
                    # 左边空值， 右侧不空， 按照左侧大值来考虑
                    break
                if result[j][k] is None and result[i][k] is not None:
                    # 右侧空值， 左边不空， 按照右侧大值来考虑
                    bNeedExchange = True
                    break
                if not isinstance(result[i][k], type(result[j][k])):
                    if str(result[i][k]) < str(result[j][k]):
                        bNeedExchange = True
                        break
                    if str(result[i][k]) > str(result[j][k]):
                        break
                else:
                    if result[i][k] < result[j][k]:
                        bNeedExchange = True
                        break
                    if result[i][k] > result[j][k]:
                        break
            if bNeedExchange:
                result[j], result[i] = result[i], result[j]


def rewiteStatement(cls, statement: str, commandScriptFile: str):
    # 随后尝试被替换内容是否为当前应用变量，环境变量
    while True:
        # 替换脚本中的变量信息
        # 替换： 一： 系统的环境变量,即{{env}}
        # 替换： 二:  系统内嵌脚本中的变量{{eval}}
        match_obj = re.search(r"{{(.*?)}}", statement, re.IGNORECASE | re.DOTALL)
        if match_obj:
            beforeRewriteStatement = statement
            searchResult = str(match_obj.group(0))
            varName = str(match_obj.group(1)).strip()

            # 先尝试在MAPPING文件中进行查找替换
            mappingResult = cls.cmdMappingHandler.RewriteWord(commandScriptFile, varName)
            if varName != mappingResult:
                statement = statement.replace(searchResult, str(mappingResult))

            # 尝试本地变量
            try:
                evalResult = evalExpression(cls, varName)
                if varName != evalResult:
                    statement = statement.replace(searchResult, str(evalResult))
            except NameError:
                # 非环境变量
                pass
            # 尝试环境变量
            if varName in os.environ:
                statement = statement.replace(searchResult, os.environ[varName])

            if statement == beforeRewriteStatement:
                # 循环替换再也没有发生变化
                break
        else:
            # 没有任何可以替换的了
            break
    return statement


def rewriteHintStatement(cls, statement: str, commandScriptFile: str):
    # 命令可能会被多次改写
    rewrotedCommandHistory = []

    # 保留原脚本
    rawStatement = statement

    # 开始替换
    statement = rewiteStatement(cls=cls, statement=statement, commandScriptFile=commandScriptFile)

    if rawStatement != statement:
        # 记录被变量信息改写的命令
        rewrotedCommandHistory.append(statement)

    return statement, rewrotedCommandHistory


def rewriteSQLStatement(cls, statement: str, commandScriptFile: str):
    # 命令可能会被多次改写
    rewrotedCommandHistory = []

    # 保留原脚本
    rawStatement = statement

    # 开始替换
    statement = rewiteStatement(cls=cls, statement=statement, commandScriptFile=commandScriptFile)

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

    # 替换请求目标的信息
    httpRequestTarget = rewiteStatement(
        cls=cls,
        statement=rawRequestObject["httpRequestTarget"],
        commandScriptFile=commandScriptFile)

    # 替换正文信息
    if "contents" in rawRequestObject:
        httpRequestContents = copy.copy(rawRequestObject["contents"])
        # 开始替换
        for nPos in range(0, len(httpRequestContents)):
            newHttpRequestContent = rewiteStatement(
                cls=cls,
                statement=httpRequestContents[nPos],
                commandScriptFile=commandScriptFile)
            if newHttpRequestContent == httpRequestContents[nPos]:
                # 一直循环到没有任何东西可以被替换
                break
            else:
                httpRequestContents[nPos] = newHttpRequestContent
    else:
        httpRequestContents = None

    # 替换请求字段
    if "httpFields" in rawRequestObject:
        httpRequestFields = copy.copy(rawRequestObject["httpFields"])
        for key, value in httpRequestFields.items():
            originFieldName = key
            key = rewiteStatement(
                cls=cls,
                statement=originFieldName,
                commandScriptFile=commandScriptFile)
            if originFieldName != key:
                # 替换Fields中的Field字段
                del httpRequestFields[originFieldName]
            value = rewiteStatement(
                cls=cls,
                statement=value,
                commandScriptFile=commandScriptFile)
            # 替换Fields中的Value字段
            httpRequestFields[key] = value
    else:
        httpRequestFields = None

    # 更新回原请求对象
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
        match_obj = re.match(
            r"^Scenario:(.*)", commandHint, re.IGNORECASE | re.DOTALL)
        if match_obj:
            senario = match_obj.group(1).strip()
            if len(senario.split(':')) == 2:
                # 如果包含两个内容， 规则是:Scenario:<ScenarioId>:<ScenarioName>
                scenarioSplitList = senario.split(':')
                commandHintList["ScenarioId"] = scenarioSplitList[0].strip()
                commandHintList["ScenarioName"] = scenarioSplitList[1].strip()
                continue
            else:
                # 如果只有一个内容， 规则是:Scenario:ScenarioName
                commandHintList["ScenarioId"] = "N/A"
                commandHintList["ScenarioName"] = senario
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
            sqlFilter = match_obj.group(2).strip()
            if "LogFilter" in commandHintList:
                commandHintList["LogFilter"].append(sqlFilter)
            else:
                commandHintList["LogFilter"] = [sqlFilter, ]
            continue

        # [Hint]  LogMask      -- TestCli会掩码随后显示的输出信息，对于符合掩码条件的，将会被掩码
        match_obj = re.search(
            r"^LogMask(\s+)(.*)", commandHint, re.IGNORECASE | re.DOTALL)
        if match_obj:
            sqlMask = match_obj.group(2).strip()
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
        # [Hint]  Scenario:XXXX   -- 相关SQL的Scenariox信息，仅仅作为日志信息供查看
        match_obj = re.match(
            r"^Scenario:(.*)", commandHint, re.IGNORECASE | re.DOTALL)
        if match_obj:
            senario = match_obj.group(1).strip()
            if len(senario.split(':')) == 2:
                # 如果包含两个内容， 规则是:Scenario:<ScenarioId>:<ScenarioName>
                scenarioSplitList = senario.split(':')
                commandHintList["ScenarioId"] = scenarioSplitList[0].strip()
                commandHintList["ScenarioName"] = scenarioSplitList[1].strip()
                continue
            else:
                # 如果只有一个内容， 规则是:Scenario:ScenarioName
                commandHintList["ScenarioId"] = "N/A"
                commandHintList["ScenarioName"] = senario
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
