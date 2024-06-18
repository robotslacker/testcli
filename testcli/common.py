# -*- coding: utf-8 -*-
import copy
import os
import re
from .sqlparse import SQLFormatWithPrefix
from .sqlparse import SQLAnalyze
from .apiparse import APIRequestObjectFormatWithPrefix
from .commands.assertExpression import evalExpression
from .testcliexception import TestCliException


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


def rewriteStatement(cls, statement: str, commandScriptFile: str):
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
                # 非本地变量
                pass
            except Exception as ex:
                if "TESTCLI_DEBUG" in os.environ:
                    raise TestCliException("evalExpression Error [" + varName + "]: [" + repr(ex) + "].")

            # 尝试环境变量
            if varName in os.environ:
                statement = statement.replace(searchResult, os.environ[varName])

            if statement == beforeRewriteStatement:
                # 循环替换再也没有发生变化
                break
        else:
            # 没有任何可以替换的了
            break

    # 随后尝试被替换内容是否为当前应用变量，环境变量
    while True:
        # 替换脚本中的变量信息
        # 替换： 一： 系统的环境变量,即${env}
        # 替换： 二:  系统内嵌脚本中的变量${eval}
        match_obj = re.search(r"\${(.*?)}", statement, re.IGNORECASE | re.DOTALL)
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
                # 非本地变量
                pass
            except Exception as ex:
                if "TESTCLI_DEBUG" in os.environ:
                    raise TestCliException("evalExpression Error 2[" + varName + "]: [" + repr(ex) + "].")

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
    statement = rewriteStatement(cls=cls, statement=statement, commandScriptFile=commandScriptFile)

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
    statement = rewriteStatement(cls=cls, statement=statement, commandScriptFile=commandScriptFile)

    # 语句发生了变化
    if rawStatement != statement:
        # 记录被变量信息改写的命令
        rewrotedCommandHistory.append(
            SQLFormatWithPrefix("Your SQL has been changed to:\n" + statement, 'REWROTED '))

    return statement, rewrotedCommandHistory


def rewriteConnectRequest(cls, connectRequestObject, commandScriptFile: str):
    # 命令可能会被多次改写
    rewrotedRequestObjects = []

    # 保留原脚本
    rawConnectRequestObject = copy.copy(connectRequestObject)

    for keyword in ["username", "password", "driver", "driverSchema", "driverType", "host", "port", "service"]:
        if keyword in connectRequestObject:
            oldType = type(connectRequestObject[keyword])
            newValue = rewriteStatement(
                cls=cls, statement=str(connectRequestObject[keyword]),
                commandScriptFile=commandScriptFile)
            newValue = oldType(newValue)
            connectRequestObject[keyword] = newValue

    # 语句发生了变化
    if rawConnectRequestObject != connectRequestObject:
        # 记录被变量信息改写的命令
        statement = "_CONNECT "
        if "username" in connectRequestObject:
            statement = statement + connectRequestObject["username"]
        if "password" in connectRequestObject:
            statement = statement + "/" + str(connectRequestObject["password"])
        if "driver" in connectRequestObject:
            statement = statement + "@" + str(connectRequestObject["driver"])
        if "driverSchema" in connectRequestObject:
            statement = statement + ":" + str(connectRequestObject["driverSchema"])
        if "driverType" in connectRequestObject:
            statement = statement + ":" + str(connectRequestObject["driverType"])
        if "host" in connectRequestObject:
            statement = statement + "//" + str(connectRequestObject["host"])
        if "port" in connectRequestObject:
            statement = statement + ":" + str(connectRequestObject["port"])
        if "service" in connectRequestObject:
            statement = statement + "/" + str(connectRequestObject["service"])

        rewrotedRequestObjects.append(
            SQLFormatWithPrefix("Your CONNECT has been changed to :\n" + statement, "REWROTED '"))

    return connectRequestObject, rewrotedRequestObjects


def rewriteAPIStatement(cls, requestObject: [], commandScriptFile: str):
    # 命令可能会被多次改写
    rewrotedRequestObjects = []

    # 保留原脚本
    rawRequestObject = copy.copy(requestObject)

    # 替换请求目标的信息
    httpRequestTarget = rewriteStatement(
        cls=cls,
        statement=rawRequestObject["httpRequestTarget"],
        commandScriptFile=commandScriptFile)

    if "headers" in rawRequestObject:
        httpRequestHeaders = copy.copy(rawRequestObject["headers"])
        # 开始替换
        for headerName, headerValue in httpRequestHeaders.items():
            newHttpRequestHeaderName = rewriteStatement(
                cls=cls,
                statement=headerName,
                commandScriptFile=commandScriptFile)
            newHttpRequestHeaderValue = rewriteStatement(
                cls=cls,
                statement=headerValue,
                commandScriptFile=commandScriptFile)
            if newHttpRequestHeaderName == headerName and newHttpRequestHeaderValue == headerValue:
                pass
            else:
                httpRequestHeaders.update(
                    {newHttpRequestHeaderName: newHttpRequestHeaderValue}
                )
    else:
        httpRequestHeaders = None

    # 替换正文信息
    if "contents" in rawRequestObject:
        httpRequestContents = copy.copy(rawRequestObject["contents"])
        # 开始替换
        for nPos in range(0, len(httpRequestContents)):
            newHttpRequestContent = rewriteStatement(
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
            key = rewriteStatement(
                cls=cls,
                statement=originFieldName,
                commandScriptFile=commandScriptFile)
            if originFieldName != key:
                # 替换Fields中的Field字段
                del httpRequestFields[originFieldName]
            value = rewriteStatement(
                cls=cls,
                statement=value,
                commandScriptFile=commandScriptFile)
            # 替换Fields中的Value字段
            httpRequestFields[key] = value
    else:
        httpRequestFields = None

    # 替换operate信息
    if "operate" in rawRequestObject:
        operateList = []
        for operate in rawRequestObject["operate"]:
            content = operate["content"]
            content = rewriteStatement(
                cls=cls,
                statement=content,
                commandScriptFile=commandScriptFile)
            operateList.append(
                {
                    "operator": operate["operator"],
                    "content": content
                }
            )
        requestObject["operate"] = operateList
    else:
        requestObject["operate"] = None

    # 更新回原请求对象
    requestObject["httpRequestTarget"] = httpRequestTarget
    if httpRequestContents is not None:
        requestObject["contents"] = httpRequestContents
    if httpRequestFields is not None:
        requestObject["httpFields"] = httpRequestFields
    if httpRequestHeaders is not None:
        requestObject["headers"] = httpRequestHeaders

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
            if len(senario.split(':')) >= 2:
                # 如果包含两个内容， 规则是:Scenario:<ScenarioId>:<ScenarioName>
                scenarioSplitList = senario.split(':')
                commandHintList["ScenarioId"] = scenarioSplitList[0].strip()
                commandHintList["ScenarioName"] = ":".join(scenarioSplitList[1:]).strip()
                continue
            else:
                # 如果只有一个内容， 规则是:Scenario:ScenarioName
                # 没有scenarioId，就默认和scenarioName相同
                commandHintList["ScenarioId"] = senario
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
            if len(senario.split(':')) >= 2:
                # 如果包含两个内容， 规则是:Scenario:<ScenarioId>:<ScenarioName>
                scenarioSplitList = senario.split(':')
                commandHintList["ScenarioId"] = scenarioSplitList[0].strip()
                commandHintList["ScenarioName"] = ":".join(scenarioSplitList[1:]).strip()
                continue
            else:
                # 如果只有一个内容， 规则是:Scenario:ScenarioName
                # 如果只有一个内容， 规则是:Scenario:ScenarioName
                # 没有scenarioId，就默认和scenarioName相同
                commandHintList["ScenarioId"] = senario
                commandHintList["ScenarioName"] = senario
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

        # [Hint] JsonFilter   -- 如果输出结果为Json格式，则按照Json的格式过滤，这对于API测试比较有用
        match_obj = re.search(
            r"^JsonFilter(\s+)(.*)", commandHint, re.IGNORECASE | re.DOTALL)
        if match_obj:
            sqlMask = match_obj.group(2).strip()
            if "JsonFilter" in commandHintList:
                commandHintList["JsonFilter"].append(sqlMask)
            else:
                commandHintList["JsonFilter"] = [sqlMask]
            continue

    return commandHintList

def isClosedBracket(s):
    # 首先去除SQL中的''和""信息 (重复的''表示单引号，重复的""表示双引号，是普通字符)
    s = s.replace("‘'", '').replace('“"', '')
    bClosedBracket = True
    lastEncloseChar = ""
    for c in s:
        if c in ['"', "'"] and lastEncloseChar == c and not bClosedBracket:
            # 遇到单引号或者双引号，并且上一个也是相同引号，且语句没结束，则结束
            bClosedBracket = True
            lastEncloseChar = ""
            continue
        if c in ['"', "'"] and bClosedBracket:
            # 第一次遇到单引号或者双引号
            bClosedBracket = False
            lastEncloseChar = c
            continue
    return bClosedBracket

def splitSqlCommand(sqlCommand: str):
    """
        将单行语句中包含的多行语句分解
        如：  单行语句SELECT 1 FROM DUAL;SELECT 2 FROM DUAL;分解成多行

        找到语句中的分号或者换行符，分段送给解析器，若能够成功解析，则为一个完整SQL
    """
    delimiters = [';', '\n']

    # 如果不包含多个语句部分，则直接返回
    multiSQL = False
    for delimiter in delimiters:
        if delimiter in sqlCommand:
            multiSQL = True
            break
    if not multiSQL:
        return [sqlCommand, ]

    # 有可能存在多个语句
    splitSqlCommandList = []
    currentSql = ""
    for c in sqlCommand:
        currentSql = currentSql + c
        # 只有遇到换行符或者分号，才有必要进行分析
        if c in delimiters:
            if not isClosedBracket(currentSql):
                isFinished = False
            else:
                (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
                    = SQLAnalyze(currentSql)
                if ret_errorCode != 0:
                    if re.search(pattern=r'missing.*<EOF>', string=ret_errorMsg):
                        # 语句没有结束
                        isFinished = False
                    if re.search(pattern=r'missing.*SQL_SLASH', string=ret_errorMsg):
                        # 语句没有结束
                        isFinished = False
                    if re.search(pattern=r'expecting.*<EOF>', string=ret_errorMsg):
                        # 语句没有结束
                        isFinished = False
            if isFinished:
                splitSqlCommandList.append(currentSql)
                currentSql = ""
    if currentSql.strip() != "":
        splitSqlCommandList.append(currentSql)
    return splitSqlCommandList
