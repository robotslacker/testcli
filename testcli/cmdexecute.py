# -*- coding: utf-8 -*-
import time
import json
import os
import re
import traceback
import glom
import ast
from .sqlparse import SQLAnalyze
from .apiparse import APIAnalyze
from .sqlparse import SQLFormatWithPrefix
from .apiparse import APIRequestStringFormatWithPrefix

from .commands.load import executeLoadRequest
from .commands.exit import exitApplication
from .commands.sqlsession import sqlSessionManage
from .commands.assertExpression import assertExpression
from .commands.assertExpression import evalExpression
from .commands.embeddScript import executeEmbeddScript
from .commands.connectdb import connectDb, disconnectDb
from .commands.start import executeFile
from .commands.host import executeLocalCommand
from .commands.spool import spool
from .commands.echo import echo_input
from .commands.setOptions import setOptions
from .commands.sleep import cliSleep
from .commands.userNameSpace import userNameSpace
from .commands.whenever import setWheneverAction
from .commands.ssh import executeSshRequest
from .commands.ssh import rewriteSshRequest
from .commands.compare import executeCompareRequest
from .commands.helper import showHelp
from .commands.data import executeDataRequest
from .commands.monitor import executeMonitorRequest
from .commands.apiSession import apiSessionManage
from .commands.apiExecute import executeAPIStatement
from .commands.apiExecute import executeAPISet
from .commands.sqlExecute import executeSQLStatement
from .commands.plugin import executePluginRequest
from .common import rewriteStatement
from .common import rewriteHintStatement
from .common import rewriteSQLStatement
from .common import rewriteAPIStatement
from .common import rewriteConnectRequest
from .common import parseSQLHints
from .common import parseAPIHints
from .common import sortresult
from .common import splitSqlCommand
from .testcliexception import TestCliException
from .globalvar import lastCommandResult


class CmdExecute(object):
    def __init__(self):
        # 程序处理选项
        self.testOptions = None

        # 主程序处理句柄
        self.cliHandler = None

        # 当前Executeor的WorkerName
        self.workerName = None

        # 程序Echo输出句柄
        self.echofile = None

        # 脚本启动的时间
        self.startTime = time.time()

        # 当前执行的命令脚本
        self.script = None

        # 命令重写处理
        self.mappingHandler = None

        # Scenario名称，如果当前未指定，则重复上一个命令的Scenario信息
        self.scenarioId = ''
        self.scenarioName = ''

        # 当前脚本的TimeOut设置
        self.sqlTimeOut = -1          # SQL执行的超时时间设置
        self.apiTimeOut = -1          # API执行的超时时间设置
        self.scriptTimeOut = -1       # 脚本执行的超时时间设置
        self.timeout = -1             # 当前SQL的超时时间设置
        self.timeOutMode = None       # COMMAND|SCRIPT|NONE

        # 数据库连接
        self.sqlConn = None
        self.sqlCursor = None

        # 记录语句是否当前处于条件表达式判定中
        self.ifMode = False
        self.ifCondition = False

        # 记录语句在Block循环过程中的相关信息
        self.loopMode = False
        self.loopCondition = False
        self.loopStartPos = 0

        # 记录语句在单句循环中的相关信息
        self.singleLoopMode = False              # 是否处于单句循环中
        self.singleLoopExpression = None         # 单句循环的判断表达式
        self.singleLoopInterval = 0              # 每次检查的时间间隔
        self.singleLoopIter = 0                  # 循环次数计数
        self.singleLoopMaxIter = -1              # 最大循环次数, -1表示不判断次数

    def setStartTime(self, startTime):
        self.startTime = startTime

    def getStartTime(self):
        return self.startTime

    """
        解析命令语句
        传入参数：
             statement         需要解析的语句
             nameSpace         当前语句所在的命名空间
        返回结果：
            返回结果为一个三元组
            ret_CommandSplitResults                 解析后的结果，用list表示的json数组，即parsedObject[]
            ret_CommandSplitResultsWithComments     包含注释信息的解析原文
            ret_CommandHints                        被提取出来的命令行注释
    """
    def parseStatement(self, statement: str, nameSpace: str = None):
        # 将所有的语句分拆开，按照行，依次投喂给解析器，以获得被Antlr分拆后的运行结果
        ret_CommandSplitResults = []
        ret_CommandSplitResultsWithComments = []
        ret_CommandHints = []

        currentStatement = None
        currentStatementWithComments = None
        currentHints = []
        statementLines = statement.split('\n')
        for nPos in range(0, len(statementLines)):
            statementLine = statementLines[nPos]
            # 将上次没有结束的行和当前行放在一起, 再次看是否已经结束
            if currentStatement is None:
                currentStatement = statementLine
            else:
                currentStatement = currentStatement + '\n' + statementLine
            if currentStatementWithComments is None:
                currentStatementWithComments = statementLine
            else:
                currentStatementWithComments = currentStatementWithComments + '\n' + statementLine

            # 调用解析器解析语句
            if self.testOptions.get("NAMESPACE") == "SQL":
                (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
                    = SQLAnalyze(currentStatement)
            elif self.testOptions.get("NAMESPACE") == "API":
                (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
                    = APIAnalyze(currentStatement)
            else:
                raise TestCliException("Non-support NAMESPACE [" + str(nameSpace) + "]")

            # 如果发生了语句解析错误，且错误信息是缺少EOF，则是认为语句没有结束导致，不是正常的错误
            if ret_errorCode != 0:
                missedSQLSlash = False
                if re.search(pattern=r'missing.*<EOF>', string=ret_errorMsg):
                    # 语句没有结束
                    isFinished = False
                if re.search(pattern=r'missing.*SQL_SLASH', string=ret_errorMsg):
                    # 语句没有结束
                    missedSQLSlash = True
                    isFinished = False
                if re.search(pattern=r'expecting.*<EOF>', string=ret_errorMsg):
                    # 语句没有结束
                    isFinished = False
                if not isFinished and self.testOptions.get("NAMESPACE") == "SQL":
                    statementFinished = False
                    if nPos == (len(statementLines) - 1):
                        # 都已经到最后一行了，不需要继续等待了
                        statementFinished = True
                    if not currentStatement.strip().startswith("_") and \
                            currentStatement.strip().endswith(';') and \
                            not missedSQLSlash:
                        # 遇到了分号，且不是复合语句，那么直接结束
                        statementFinished = True
                    if currentStatement.strip().endswith("\n/"):
                        # 遇到了顶行的/，不管是不是复合语句，直接结束
                        statementFinished = True
                    if statementFinished:
                        if currentStatement.strip().startswith("_"):
                            # 内部语句，且语句已经结束
                            ret_CommandSplitResults.append(
                                {'name': 'PARSE_ERROR',
                                 'statement': currentStatement,
                                 'reason': ret_errorMsg}
                            )
                            # 解析前的语句
                            ret_CommandSplitResultsWithComments.append(currentStatementWithComments)
                            # 所有的提示信息
                            ret_CommandHints.append(currentHints)
                            # 清空语句的变量
                            currentHints = []
                            currentStatement = None
                            currentStatementWithComments = None
                        else:
                            if currentStatement.strip().endswith("\n/"):
                                currentStatement = currentStatement[:-2]
                            elif currentStatement.strip().endswith(";"):
                                currentStatement = currentStatement[:-1]
                            ret_CommandSplitResults.append(
                                {'name': 'SQL_UNKNOWN',
                                 'statement': currentStatement,
                                 'reason': ret_errorMsg}
                            )
                            # 解析前的语句
                            ret_CommandSplitResultsWithComments.append(currentStatementWithComments)
                            # 所有的提示信息
                            ret_CommandHints.append(currentHints)
                            # 清空语句的变量
                            currentHints = []
                            currentStatement = None
                            currentStatementWithComments = None
                    continue

            # 如果语句没有结束，则需要等待下一句输入
            if not isFinished:
                # 如果到了文件末尾，就没有必要继续等待，直接返回
                if nPos == (len(statementLines) - 1):
                    if self.testOptions.get("NAMESPACE") == "SQL":
                        ret_CommandSplitResults.append(
                            {'name': 'SQL_UNKNOWN',
                             'statement': currentStatement,
                             'reason': ret_errorMsg}
                        )
                    elif self.testOptions.get("NAMESPACE") == "API":
                        ret_CommandSplitResults.append(
                            {'name': 'API_UNKNOWN',
                             'statement': currentStatement,
                             'reason': ret_errorMsg}
                        )
                    # 解析前的语句
                    ret_CommandSplitResultsWithComments.append(currentStatementWithComments)
                    # 所有的提示信息
                    ret_CommandHints.append(currentHints)
                    # 清空语句的变量
                    currentHints = []
                    currentStatement = None
                    currentStatementWithComments = None
                continue

            # 语句已经结束, 但是输入的内容有错误信息
            if isFinished and ret_errorCode != 0:
                ret_CommandSplitResults.append(
                    {'name': 'PARSE_ERROR',
                     'statement': currentStatement,
                     'reason': ret_errorMsg}
                )
                # 解析前的语句
                ret_CommandSplitResultsWithComments.append(currentStatementWithComments)
                # 所有的提示信息
                ret_CommandHints.append(currentHints)
                # 清空语句的变量
                currentHints = []
                currentStatement = None
                currentStatementWithComments = None
                continue

            # 语句已经结束，没有任何错误，但解析的结果为空
            if ret_CommandSplitResult is None:
                # 空行，可能包含注释，保留注释内容，带到下一个有意义的段落
                # Hint的两种写法
                # 1.  -- [Hint]  hintsomething
                # 2.  -- [hitsomething]
                pattern = r"^(\s+)?([-/][-/])(\s+)?\[(\s+)?Hint(\s+)?\](.*)"
                matchObj = re.match(pattern, statementLine, re.IGNORECASE)
                if matchObj:
                    currentHints.append(matchObj.group(6).strip())
                else:
                    pattern = r"^(\s+)?([-/][-/])(\s+)?\[(.*)\].*"
                    matchObj = re.match(pattern, statementLine, re.IGNORECASE)
                    if matchObj:
                        currentHints.append(matchObj.group(4).strip())
                # 解析后的语句
                ret_CommandSplitResults.append(None)
                # 解析前的语句
                ret_CommandSplitResultsWithComments.append(currentStatementWithComments)
                # 对于非有效语句，Hint不在当前语句中体现，而是要等到下次有意义的语句进行处理
                ret_CommandHints.append([])
                # 清空除了Hint以外的其他语句变量
                currentStatement = None
                currentStatementWithComments = None
                continue

            # 切换解析的命名空间
            if ret_CommandSplitResult["name"] == "USE":
                self.testOptions.set("NAMESPACE", ret_CommandSplitResult["nameSpace"])

            # 对于SQL的CONNECT命令做特殊处理， 以支持外部环境变量带来的问题
            if self.testOptions.get("NAMESPACE") == "SQL":
                if ret_CommandSplitResult["name"] == "CONNECT":
                    # 对于数据库连接命令，如果没有给出连接详细信息，并且指定了环境变量，附属环境变量到连接命令后
                    if "driver" not in ret_CommandSplitResult:
                        connectionURL = None
                        if "SQLCLI_CONNECTION_URL" in os.environ:
                            connectionURL = str(os.environ["SQLCLI_CONNECTION_URL"]).strip('"').strip("'").strip()
                        elif "TESTCLI_CONNECTION_URL" in os.environ:
                            connectionURL = str(os.environ["TESTCLI_CONNECTION_URL"]).strip('"').strip("'").strip()
                        if connectionURL is not None:
                            # 拼接链接字符串后重新解析
                            (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) \
                                = SQLAnalyze(currentStatement + "@" + connectionURL)

            # 语句正常结束，且其中包含了正式的内容
            ret_CommandSplitResults.append(ret_CommandSplitResult)
            # 解析前的语句
            ret_CommandSplitResultsWithComments.append(currentStatementWithComments)
            # 所有的提示信息
            ret_CommandHints.append(currentHints)
            # 清空语句的变量
            currentHints = []
            currentStatement = None
            currentStatementWithComments = None
            continue

        return ret_CommandSplitResults, ret_CommandSplitResultsWithComments, ret_CommandHints

    """
        根据提示信息改写返回结果中的结果集
        传入参数：
             result            命令执行结果
             commandHints      命令提示信息
        返回结果：             
            处理result中的Rows对象. 没有单独的返回，将直接重写传入的result内容.
            目前处理的提示包括：
                 Order          对返回结果集再排序，仅针对rows
                 LogFilter      对返回结果集进行过滤
                 LogMask        对返回结果集进行掩码
    """
    @staticmethod
    def processCommandHint_Rows(result, commandHints: dict):
        if result is None:
            return

        if "rows" in result.keys() and result["rows"] is not None:
            rows = result["rows"]
            # 如果Hints中有order字样，对结果进行排序后再输出
            if "Order" in commandHints.keys():
                if "TESTCLI_DEBUG" in os.environ:
                    print("[DEBUG] Will sort this result accoring to [Order] hint ...")
                # 不能用sorted函数，需要考虑None出现在列表中特定元素的问题
                # l =  [(-32767,), (32767,), (None,), (0,)]
                sortresult(rows)

            # 如果Hint中存在LogFilter，则结果集中过滤指定的输出信息
            if "LogFilter" in commandHints.keys():
                for logFilter in commandHints["LogFilter"]:
                    if logFilter.strip().startswith("'") and logFilter.strip().endswith("'"):
                        logFilter = logFilter.strip()
                    if logFilter.strip().startswith("'") and logFilter.strip().endswith("'"):
                        logFilter = logFilter.strip()
                    for item in rows[::-1]:
                        # 将所有列用空格分隔来合并为一行
                        combinedRow = ""
                        for cell in item:
                            if combinedRow == "":
                                combinedRow = str(cell)
                            else:
                                combinedRow = combinedRow + " " + str(cell)
                        if re.match(pattern=logFilter, string=combinedRow, flags=re.IGNORECASE):
                            if "TESTCLI_DEBUG" in os.environ:
                                print("[DEBUG] Will apply filter: [" + combinedRow +
                                      "] with " + logFilter + ". Matched.")
                            rows.remove(item)
                            continue
                        else:
                            if "TESTCLI_DEBUG" in os.environ:
                                print("[DEBUG] Will apply filter: [" + combinedRow +
                                      "] with " + logFilter + ". Not matched.")

            # 如果Hint中存在LogMask,则掩码指定的输出信息
            if "LogMask" in commandHints.keys():
                for i in range(0, len(rows)):
                    rowResult = list(rows[i])
                    bDataChanged = False
                    for j in range(0, len(rowResult)):
                        if rowResult[j] is None:
                            continue
                        output = str(rowResult[j])
                        for sqlMaskListString in commandHints["LogMask"]:
                            sqlMaskList = sqlMaskListString.split("=>")
                            if len(sqlMaskList) == 2:
                                sqlMaskPattern = str(sqlMaskList[0])
                                sqlMaskTarget = str(sqlMaskList[1])
                                if sqlMaskPattern.strip().startswith("'") and sqlMaskPattern.strip().endswith("'"):
                                    sqlMaskPattern = sqlMaskPattern.strip()
                                if sqlMaskTarget.strip().startswith("'") and sqlMaskTarget.strip().endswith("'"):
                                    sqlMaskTarget = sqlMaskTarget.strip()
                                if sqlMaskPattern.strip().startswith('"') and sqlMaskPattern.strip().endswith('"'):
                                    sqlMaskPattern = sqlMaskPattern.strip()
                                if sqlMaskTarget.strip().startswith('"') and sqlMaskTarget.strip().endswith('"'):
                                    sqlMaskTarget = sqlMaskTarget.strip()
                                if "TESTCLI_DEBUG" in os.environ:
                                    print("[DEBUG] Will apply mask:" + output +
                                          " with " + sqlMaskPattern + "=>" + sqlMaskTarget)
                                try:
                                    beforeReplace = str(rowResult[j])
                                    nIterCount = 0
                                    while True:
                                        # 循环多次替代，一直到没有可替代为止
                                        afterReplace = re.sub(sqlMaskPattern, sqlMaskTarget,
                                                              beforeReplace, re.IGNORECASE)
                                        if afterReplace == beforeReplace or nIterCount > 99:
                                            newOutput = afterReplace
                                            break
                                        beforeReplace = afterReplace
                                        nIterCount = nIterCount + 1
                                    if newOutput != output:
                                        bDataChanged = True
                                        rowResult[j] = newOutput
                                    output = newOutput
                                except re.error:
                                    if "TESTCLI_DEBUG" in os.environ:
                                        print('[DEBUG] traceback.print_exc():\n%s'
                                              % traceback.print_exc())
                                        print('[DEBUG] traceback.format_exc():\n%s'
                                              % traceback.format_exc())
                            else:
                                if "TESTCLI_DEBUG" in os.environ:
                                    print("[DEBUG] LogMask Hint Error: " + commandHints["LogMask"])
                    if bDataChanged:
                        rows[i] = tuple(rowResult)

    """
        根据提示信息改写返回结果中的状态信息
        传入参数：
             result            命令执行结果
             commandHints      命令提示信息
        返回结果：             
            处理result中的Status对象. 没有单独的返回，将直接重写传入的result内容.
            目前处理的提示包括：
                 LogFilter      对返回状态信息，错误提示进行过滤（状态信息，错误提示如果包含多行，则逐行过滤）
                 LogMask        对返回状态信息，错误提示进行掩码（状态信息，错误提示如果包含多行，则逐行掩码）
    """
    @staticmethod
    def processCommandHint_Status(result, commandHints: dict):
        if result is None:
            return

        # 处理状态消息中的信息
        if "status" in result.keys() and result["status"] is not None:
            status = result["status"]
            statusLineList = status.splitlines(keepends=False)
            # 如果Hint中存在LogFilter，则结果集中过滤指定的输出信息
            if "LogFilter" in commandHints.keys():
                for logFilter in commandHints["LogFilter"]:
                    # 从后往前删除，以避免漏掉一些东西
                    for line in statusLineList[::-1]:
                        try:
                            if re.match(pattern=logFilter, string=line, flags=re.IGNORECASE):
                                if "TESTCLI_DEBUG" in os.environ:
                                    print("[DEBUG] Apply filter: [" + line + "] with " + logFilter + ". Matched.")
                                statusLineList.remove(line)
                                continue
                            else:
                                if "TESTCLI_DEBUG" in os.environ:
                                    print("[DEBUG] Apply filter: [" + line + "] with " + logFilter + ". Not match.")
                        except re.error as rex:
                            if "TESTCLI_DEBUG" in os.environ:
                                print("[DEBUG] Filter error : [" + line + "] with " + logFilter + ". " + str(rex))
                result["status"] = "\n".join(statusLineList)
            # 如果Hint中存在LogMask,则掩码指定的输出信息
            if "LogMask" in commandHints.keys():
                for i in range(0, len(statusLineList)):
                    line = statusLineList[i]
                    for sqlMaskListString in commandHints["LogMask"]:
                        sqlMaskList = sqlMaskListString.split("=>")
                        if len(sqlMaskList) == 2:
                            sqlMaskPattern = sqlMaskList[0]
                            sqlMaskTarget = sqlMaskList[1]
                            if "TESTCLI_DEBUG" in os.environ:
                                print("[DEBUG] Will apply mask:" + line +
                                      " with " + sqlMaskPattern + "=>" + sqlMaskTarget)
                            try:
                                beforeReplace = line
                                nIterCount = 0
                                bDataChanged = False
                                while True:
                                    # 循环多次替代，一直到没有可替代为止
                                    afterReplace = re.sub(sqlMaskPattern, sqlMaskTarget,
                                                          beforeReplace, re.IGNORECASE)
                                    if afterReplace == beforeReplace or nIterCount > 99:
                                        newLine = afterReplace
                                        break
                                    beforeReplace = afterReplace
                                    nIterCount = nIterCount + 1
                                if newLine != line:
                                    bDataChanged = True
                                    line = newLine
                                if bDataChanged:
                                    statusLineList[i] = newLine
                            except re.error:
                                if "TESTCLI_DEBUG" in os.environ:
                                    print('[DEBUG] traceback.print_exc():\n%s'
                                          % traceback.print_exc())
                                    print('[DEBUG] traceback.format_exc():\n%s'
                                          % traceback.format_exc())
                        else:
                            if "TESTCLI_DEBUG" in os.environ:
                                print("[DEBUG] LogMask Hint Error: " + commandHints["LogMask"])
                result["status"] = "\n".join(statusLineList)

    """
        根据提示信息改写返回结果中的错误信息
        传入参数：
             result            命令执行结果
             commandHints      命令提示信息
        返回结果：             
            处理result中的Message对象. 没有单独的返回，将直接重写传入的result内容.
            目前处理的提示包括：
                 LogFilter      对错误提示进行过滤，如果存在多行，则逐行过滤
                 LogMask        对错误提示进行掩码，如果存在多行，则逐行过滤
    """
    @staticmethod
    def processCommandHint_Message(result, commandHints: dict):
        if result is None:
            return

        if "message" in result.keys() and result["message"] is not None:
            message = result["message"]
            messageLineList = message.splitlines(keepends=False)
            # 如果Hint中存在LogFilter，则结果集中过滤指定的输出信息
            if "LogFilter" in commandHints.keys():
                for logFilter in commandHints["LogFilter"]:
                    for line in messageLineList[::-1]:
                        try:
                            if re.match(pattern=logFilter, string=line, flags=re.IGNORECASE):
                                if "TESTCLI_DEBUG" in os.environ:
                                    print("[DEBUG] Apply filter: [" + line + "] with " + logFilter + ". Matched.")
                                messageLineList.remove(line)
                                continue
                            else:
                                if "TESTCLI_DEBUG" in os.environ:
                                    print("[DEBUG] Apply filter: [" + line + "] with " + logFilter + ". Not match.")
                        except re.error as rex:
                            if "TESTCLI_DEBUG" in os.environ:
                                print("[DEBUG] Filter error : [" + line + "] with " + logFilter + ". " + str(rex))
                result["message"] = "\n".join(messageLineList)

            # 如果Hint中存在LogMask,则掩码指定的输出信息
            if "LogMask" in commandHints.keys():
                for i in range(0, len(messageLineList)):
                    line = messageLineList[i]
                    for sqlMaskListString in commandHints["LogMask"]:
                        sqlMaskList = sqlMaskListString.split("=>")
                        if len(sqlMaskList) == 2:
                            sqlMaskPattern = sqlMaskList[0]
                            sqlMaskTarget = sqlMaskList[1]
                            if "TESTCLI_DEBUG" in os.environ:
                                print("[DEBUG] Will apply mask:" + line +
                                      " with " + sqlMaskPattern + "=>" + sqlMaskTarget)
                            try:
                                beforeReplace = line
                                nIterCount = 0
                                bDataChanged = False
                                while True:
                                    # 循环多次替代，一直到没有可替代为止
                                    afterReplace = re.sub(sqlMaskPattern, sqlMaskTarget,
                                                          beforeReplace, re.IGNORECASE)
                                    if afterReplace == beforeReplace or nIterCount > 99:
                                        newLine = afterReplace
                                        break
                                    beforeReplace = afterReplace
                                    nIterCount = nIterCount + 1
                                if newLine != line:
                                    bDataChanged = True
                                    line = newLine
                                if bDataChanged:
                                    messageLineList[i] = newLine
                            except re.error:
                                if "TESTCLI_DEBUG" in os.environ:
                                    print('[DEBUG] traceback.print_exc():\n%s'
                                          % traceback.print_exc())
                                    print('[DEBUG] traceback.format_exc():\n%s'
                                          % traceback.format_exc())
                        else:
                            if "TESTCLI_DEBUG" in os.environ:
                                print("[DEBUG] LogMask Hint Error: " + commandHints["LogMask"])
                result["message"] = "\n".join(messageLineList)

    """
        根据提示信息改写返回结果中的Content信息
        传入参数：
             result            命令执行结果
             commandHints      命令提示信息
        返回结果：             
            处理result["Status"]中的Content对象. 没有单独的返回，将直接重写传入的result内容.
            Content信息为API语句执行结果，多半为JSON表达式
            目前处理的提示包括：
                 JsonFilter     对回应的JSON格式进行glom表达式过滤
    """
    @staticmethod
    def processCommandHint_Contents(result, commandHints: dict):
        if "JsonFilter" in commandHints.keys():
            if "status" in result.keys() and result["status"] is not None:
                status = result["status"]
                try:
                    jsonStatus = json.loads(status)
                except json.decoder.JSONDecodeError:
                    # 传递的对象不是一个JSON组合体，不适用JsonFilter
                    return
                # 查看status是否为JSON格式，如果不是，则跳过
                if "content" in jsonStatus.keys() and jsonStatus["content"] is not None:
                    content = jsonStatus["content"]
                    for spec in commandHints["JsonFilter"]:
                        try:
                            # 此处不使用eval，而使用literal_eval, 是因为eval可能会把一些规则中的内容进行进行非预期的数据运算
                            spec = ast.literal_eval(spec)
                        except (SyntaxError, ValueError) as ex:
                            # 传递的信息并不是一个字典结构，那就按照字符串传递给glom
                            if "TESTCLI_DEBUG" in os.environ:
                                print("[DEBUG] Bad glom (1) expression =[" + str(spec) + "]" + repr(ex))
                        # 尝试使用glom进行解析
                        try:
                            content = glom.glom(target=content, spec=spec)
                        except glom.core.GlomError as ex:
                            #  无法解析的glob表达式
                            if "TESTCLI_DEBUG" in os.environ:
                                print("[DEBUG] Bad glom (2) expression =[" + str(spec) + "]" + repr(ex))
                    jsonStatus["content"] = content
                result["status"] = json.dumps(
                    obj=jsonStatus,
                    sort_keys=True,
                    indent=4,
                    separators=(',', ': '),
                    ensure_ascii=False
                )

    """
        执行命令语句
        传入参数：
             statement            需要执行的语句
             commandScriptFile    文件来自于那个文件，如果是控制台输入，则为Console。否则应该是脚本文名
                                  文件名称主要用于命令行映射，日志的输出等
             nameSpace            需要执行的命名空间                     
        返回结果：
            无return结果
            
            用yield的方式分批次返回执行的结果，JSON格式，根据执行语句不同，返回内容也会有所不同
            
            执行错误的语句，返回内容为：
                {
                    "type":     "error"
                    "message":  错误消息
                }
            对于命令语句解析，返回内容为：
                {
                    "type":             "parse"
                    "rawCommand":       用数组表示的解析前的语句，包括注释信息
                    "formattedCommand": 对语句进行解析后的结果，包含了格式化后的内容信息
                    "rewrotedCommand":  语句重写机制的提示信息
                    "script":           执行该语句的脚本文件名
                }
            对于数据库语句执行结果，返回内容为：
                {
                    "type":        "result"
                    "title":        输出内容的标题信息,
                    "rows":         结果数据集，用一个二维的元组信息表示，((1,2),(3,4),(5,6),...)
                                    每一行数据被记录在一个元组中，所有行的记录再被记录到整个的元组中
                    "headers":      表头信息
                                    数组。其维数一定和列数相同。 如["COL1", "COL2"]
                    "columnTypes":  结果字段类型
                                    数组。其维数一定和列数相同。 如["VARCHAR", "INTEGER"]
                                    具体列表参考： sqlclijdbc.py中的_DEFAULT_CONVERTERS中信息
                    "status":       输出的后提示信息，字符串格式
                }
            对于API语句执行结果，返回内容为：
                {
                    "type":        "result"
                    "title":       恒定为None
                    "rows":        恒定为None
                    "headers":     恒定为None
                    "columnTypes": 恒定为None
                    "status":      JSON格式，内容为：
                                   "status"     HTTP请求响应结果
                                   "content"    可能为字符串格式（如果可以被解析为JSON格式，则返回JSON格式）
                }
            对于语句执行统计信息，返回内容为：
                    "type":             "statistics",
                    "startedTime":      语句开始执行时间。 UNIX时间秒单位
                    "elapsed":          语句累计执行时间，浮点数，单位为秒
                    "processName":      当前执行语句进程名称
                    "rawCommand":       原始语句信息（包含注释等）
                    "commandType":      语句类型，字符串，如SQL，HTTP, SLEEP，....
                    "command":          解析后的语句，JSON格式表达
                    "commandStatus":    命令执行后提示信息
                    "errorCode":        错误代码
                    "scenarioId":       测试场景ID
                    "scenarioName":     测试场景名称
            
            任何语句执行，包括API，包括SQL，总是会用三段返回， 即解析内容、结果内容、统计内容
    """
    def runStatement(self, statement: str,
                     commandScriptFile: str = "Console",
                     nameSpace: str = None):

        # 如果没有提供nameSpace，则使用系统默认的nameSpace
        if nameSpace is None:
            nameSpace = self.testOptions.get("NAMESPACE")

        # Remove spaces and EOL
        statement = statement.strip()
        formattedCommand = None
        if not statement:  # Empty string
            return

        # 记录脚本的文件名
        self.script = commandScriptFile

        # DEBUG模式下，打印当前计划要执行的语句
        if "TESTCLI_DEBUG" in os.environ:
            if nameSpace == "SQL":
                print("[DEBUG] SQL Command=[" + str(statement) + "]")
            elif nameSpace == "API":
                print("[DEBUG] API Command=[" + str(statement) + "]")

        try:
            # 解析前要保留用户的nameSpace，解析后要把这个内容还原
            # 主要是考虑了执行脚本中，脚本内部含有的nameSpace切换不应该影响到外部的脚本
            defaultNameSpace = self.testOptions.get("NAMESPACE")

            # 开始解析语句
            ret_CommandSplitResults, ret_CommandSplitResultsWithComments, ret_CommandHints = \
                self.parseStatement(statement=statement, nameSpace=nameSpace)

            # 解析过程中设置的NAMESPACE，解析后要还原，好保证执行的正确
            self.testOptions.set("NAMESPACE", defaultNameSpace)
        except Exception:
            if "TESTCLI_DEBUG" in os.environ:
                print('traceback.print_exc():\n%s' % traceback.print_exc())
                print('traceback.format_exc():\n%s' % traceback.format_exc())
            raise TestCliException("TestCli-000 Internal error. Parse failed.")

        # 开始执行语句
        pos = 0
        startTime = None
        while True:
            if pos == len(ret_CommandSplitResults):
                break

            # 记录命令开始时间
            if self.singleLoopMode and self.singleLoopIter != 0:
                # 单句循环模式下，只有第一句记录开始运行时间，以后都不再修改开始时间
                if startTime is None:
                    startTime = time.time()
            else:
                startTime = time.time()

            try:
                self.sqlTimeOut = int(self.testOptions.get("SQL_TIMEOUT"))
            except ValueError:
                self.sqlTimeOut = -1
            try:
                self.apiTimeOut = int(self.testOptions.get("API_TIMEOUT"))
            except ValueError:
                self.apiTimeOut = -1
            try:
                self.scriptTimeOut = int(self.testOptions.get("SCRIPT_TIMEOUT"))
            except ValueError:
                self.scriptTimeOut = -1

            # 首先打印原有语句
            if self.testOptions.get("NAMESPACE") == "SQL":
                formattedCommand = SQLFormatWithPrefix(ret_CommandSplitResultsWithComments[pos])
            if self.testOptions.get("NAMESPACE") == "API":
                formattedCommand = APIRequestStringFormatWithPrefix(ret_CommandSplitResultsWithComments[pos])

            # 如果是空语句，不需要执行，但可能是完全注释行
            # 也可能是一个解析错误的语句
            if ret_CommandSplitResults[pos] is None:
                if self.loopMode and not self.loopCondition:
                    pass
                else:
                    yield {
                        "type": "parse",
                        "rawCommand": ret_CommandSplitResults[pos],
                        "formattedCommand": formattedCommand,
                        "rewrotedCommand": [],
                        "script": commandScriptFile
                    }
                pos = pos + 1
                continue
            else:
                parseObject = dict(ret_CommandSplitResults[pos])

            # 如果在循环模式下，且循环条件已经不满足，则直接跳出
            if parseObject["name"] != "LOOP":
                if self.loopMode and not self.loopCondition:
                    pos = pos + 1
                    continue

            # 返回Command的解析信息
            if self.singleLoopMode and self.singleLoopIter != 0:
                # 单句循环模式下，只在第一次打印语句解析结果，之后都不再打印
                pass
            else:
                yield {
                    "type": "parse",
                    "rawCommand": ret_CommandSplitResults[pos],
                    "formattedCommand": formattedCommand,
                    "rewrotedCommand": [],
                    "script": commandScriptFile
                }

            # 处理超时时间问题
            if self.scriptTimeOut > 0:
                if self.scriptTimeOut <= time.time() - self.getStartTime():
                    commandErrorMessage = "Testcli-0000: Script Timeout " \
                                         "(" + str(round(self.scriptTimeOut, 2)) + \
                                         ") expired. Abort this Script."
                    yield {"type": "error", "message": commandErrorMessage}
                    raise EOFError
                else:
                    if self.testOptions.get("NAMESPACE") == "SQL":
                        if self.sqlTimeOut > 0:
                            if self.scriptTimeOut - (time.time() - self.getStartTime()) < self.sqlTimeOut:
                                # 脚本超时剩余时间更少，执行较少的那个超时控制
                                self.timeOutMode = "SCRIPT"
                                self.timeout = self.scriptTimeOut - (time.time() - self.getStartTime())
                            else:
                                self.timeOutMode = "COMMAND"
                                self.timeout = self.sqlTimeOut
                        else:
                            self.timeOutMode = "SCRIPT"
                            self.timeout = self.scriptTimeOut - (time.time() - self.getStartTime())
                    if self.testOptions.get("NAMESPACE") == "API":
                        if self.apiTimeOut > 0:
                            if self.scriptTimeOut - (time.time() - self.getStartTime()) < self.apiTimeOut:
                                # 脚本超时剩余时间更少，执行较少的那个超时控制
                                self.timeOutMode = "SCRIPT"
                                self.timeout = self.scriptTimeOut - (time.time() - self.getStartTime())
                            else:
                                self.timeOutMode = "COMMAND"
                                self.timeout = self.apiTimeOut
                        else:
                            self.timeOutMode = "SCRIPT"
                            self.timeout = self.scriptTimeOut - (time.time() - self.getStartTime())
            elif self.testOptions.get("NAMESPACE") == "SQL" and self.sqlTimeOut > 0:
                # 没有设置SCRIPT的超时时间，只设置了COMMAND的超时时间
                self.timeOutMode = "COMMAND"
                self.timeout = self.sqlTimeOut
            elif self.testOptions.get("NAMESPACE") == "API" and self.apiTimeOut > 0:
                # 没有设置SCRIPT的超时时间，只设置了COMMAND的超时时间
                self.timeOutMode = "COMMAND"
                self.timeout = self.apiTimeOut
            else:
                # 什么超时时间都没有设置
                self.timeOutMode = None
                self.timeout = -1

            # 处理Hints信息
            if self.testOptions.get("NAMESPACE") == "SQL":
                commandHintList = parseSQLHints(list(ret_CommandHints[pos]))
            elif self.testOptions.get("NAMESPACE") == "API":
                commandHintList = parseAPIHints(list(ret_CommandHints[pos]))
            else:
                commandHintList = {}
            for commandHintKey, commandHintValue in commandHintList.items():
                if type(commandHintValue) == list:
                    for nPos in range(0, len(commandHintValue)):
                        commandHintNewValue, rewrotedCommandHintValueList = rewriteHintStatement(
                            cls=self.cliHandler,
                            statement=commandHintValue[nPos],
                            commandScriptFile=commandScriptFile
                        )
                        if len(rewrotedCommandHintValueList) != 0:
                            commandHintValue[nPos] = commandHintNewValue
                            rewrotedHint = "REWROTED Hint> --[Hint] " + \
                                           commandHintKey + "    " + commandHintNewValue + "]"
                            yield {
                                "type": "parse",
                                "rawCommand": None,
                                "formattedCommand": None,
                                "rewrotedCommand": [rewrotedHint, ],
                                "script": commandScriptFile
                            }

                # 根据语句中的变量或者其他定义信息来重写当前语句
                if type(commandHintValue) == str:
                    # 只针对字符串进行处理，暂时不对其他数据类型进行处理
                    commandHintNewValue, rewrotedCommandHintValueList = rewriteHintStatement(
                        cls=self.cliHandler,
                        statement=commandHintValue,
                        commandScriptFile=commandScriptFile
                    )
                    if len(rewrotedCommandHintValueList) != 0:
                        commandHintList[commandHintKey] = commandHintNewValue

            # 处理ScenarioId和ScenarioName, 他们总是成对出现
            if "ScenarioId" in commandHintList:
                scenarioId = str(commandHintList["ScenarioId"])
                scenarioName = str(commandHintList["ScenarioName"])
                if scenarioName.strip().upper() == 'END':
                    self.scenarioName = ""
                    self.scenarioId = ""
                else:
                    self.scenarioName = scenarioName
                    self.scenarioId = scenarioId
                    rewrotedHint = "REWROTED Hint> --[Scenario:" + scenarioId + ":" + scenarioName + "]"
                    yield {
                        "type": "parse",
                        "rawCommand": None,
                        "formattedCommand": None,
                        "rewrotedCommand": [rewrotedHint, ],
                        "script": commandScriptFile
                    }

            # 处理各种命令
            if "TESTCLI_DEBUG" in os.environ:
                print("[DEBUG] parsedObject=[" + str(parseObject) + "]")
            sqlKeyWords = ["SELECT", "DELETE", "UPDATE", "CREATE", "INSERT",
                           "DROP", "COMMIT", "ROLLBACK",
                           "PROCEDURE", "DECLARE", "BEGIN",
                           "SQL_UNKNOWN"]
            try:
                if parseObject["name"] == "HELP":
                    # 显示帮助信息
                    for commandResult in showHelp(
                            topicName=parseObject["topic"],
                    ):
                        yield commandResult
                elif parseObject["name"] == "ECHO":
                    # 将后续内容回显到指定的文件中
                    for commandResult in echo_input(
                            cls=self.cliHandler,
                            fileName=parseObject["param"],
                            block=parseObject["block"],
                    ):
                        yield commandResult
                elif parseObject["name"] == "START":
                    # 执行脚本前记录当前执行的脚本名称
                    savedExecuteScript = self.cliHandler.executeScript
                    self.cliHandler.executeScript = parseObject["script"]
                    # 执行脚本文件
                    for commandResult in executeFile(
                            cls=self.cliHandler,
                            scriptFile=parseObject["script"],
                            argv=parseObject["argv"],
                    ):
                        yield commandResult
                    # 执行脚本后还原当前执行脚本的名称
                    self.cliHandler.executeScript = savedExecuteScript
                elif parseObject["name"] in ["EXIT", "QUIT"]:
                    # 执行脚本文件
                    if "exitValue" in parseObject.keys():
                        exitValue = parseObject["exitValue"]
                    else:
                        exitValue = 0
                    for commandResult in exitApplication(
                            cls=self.cliHandler,
                            exitValue=exitValue
                    ):
                        if commandResult["type"] == "result":
                            lastCommandResult.clear()
                            lastCommandResult["status"] = commandResult["status"]
                            lastCommandResult["errorCode"] = 0
                        if commandResult["type"] == "error":
                            lastCommandResult["status"] = commandResult["message"]
                            lastCommandResult["errorCode"] = 1
                        yield commandResult
                elif parseObject["name"] == "CONNECT":
                    # 根据语句中的变量或者其他定义信息来重写当前语句
                    connectRequestObject, rewrotedCommandList = rewriteConnectRequest(
                        cls=self.cliHandler,
                        connectRequestObject=parseObject,
                        commandScriptFile=commandScriptFile
                    )
                    if len(rewrotedCommandList) != 0:
                        # 如果命令被发生了改写，要打印改写记录
                        yield {
                            "type": "parse",
                            "rawCommand": None,
                            "formattedCommand": None,
                            "rewrotedCommand": rewrotedCommandList,
                            "script": commandScriptFile
                        }

                    # 执行CONNECT命令
                    for commandResult in connectDb(
                            cls=self.cliHandler,
                            connectProperties=connectRequestObject
                    ):
                        if commandResult["type"] == "result":
                            lastCommandResult.clear()
                            lastCommandResult["status"] = commandResult["status"]
                            lastCommandResult["errorCode"] = 0
                        if commandResult["type"] == "error":
                            lastCommandResult["message"] = commandResult["message"]
                            lastCommandResult["errorCode"] = 1
                        yield commandResult
                elif parseObject["name"] == "SET":
                    # 执行SET命令
                    for commandResult in setOptions(
                            cls=self.cliHandler,
                            options=parseObject
                    ):
                        if commandResult["type"] == "result":
                            lastCommandResult.clear()
                            lastCommandResult["status"] = commandResult["status"]
                            lastCommandResult["errorCode"] = 0
                        if commandResult["type"] == "error":
                            lastCommandResult["status"] = commandResult["message"]
                            lastCommandResult["errorCode"] = 1
                        yield commandResult
                elif parseObject["name"] == "DISCONNECT":
                    # 执行DISCONNECT命令
                    if self.testOptions.get("NAMESPACE") == "SQL":
                        for commandResult in disconnectDb(
                                cls=self.cliHandler
                        ):
                            if commandResult["type"] == "result":
                                lastCommandResult.clear()
                                lastCommandResult["status"] = commandResult["status"]
                                lastCommandResult["errorCode"] = 0
                            if commandResult["type"] == "error":
                                lastCommandResult["status"] = commandResult["message"]
                                lastCommandResult["errorCode"] = 1
                            yield commandResult
                    else:
                        yield {
                            "type": "error",
                            "message": "Non-SQL namespace does not support DISCONNECT command.",
                            "script": commandScriptFile
                        }
                elif parseObject["name"] in sqlKeyWords:
                    if self.ifMode and not self.ifCondition:
                        pos = pos + 1
                        continue
                    sqlCommand = parseObject["statement"]

                    # 根据语句中的变量或者其他定义信息来重写当前语句
                    sqlCommand, rewrotedCommandList = rewriteSQLStatement(
                        cls=self.cliHandler,
                        statement=sqlCommand,
                        commandScriptFile=commandScriptFile
                    )
                    if len(rewrotedCommandList) != 0:
                        # 如果命令被发生了改写，要打印改写记录
                        yield {
                            "type": "parse",
                            "rawCommand": None,
                            "formattedCommand": None,
                            "rewrotedCommand": rewrotedCommandList,
                            "script": commandScriptFile
                        }

                    # 一个SQL语句可能包含多个部分。如分号或者/分割，需要先拆解成多个
                    sqlCommandList = splitSqlCommand(sqlCommand=sqlCommand)

                    # 依次执行SQL语句
                    for sqlCommand in sqlCommandList:
                        # 执行SQL语句
                        sqlIter = 0
                        for result in executeSQLStatement(
                                cls=self,
                                sql=sqlCommand,
                                sqlHints=commandHintList):
                            sqlIter = sqlIter + 1

                            # 处理命令行的提示信息
                            self.processCommandHint_Rows(result=result, commandHints=commandHintList)
                            self.processCommandHint_Status(result=result, commandHints=commandHintList)
                            self.processCommandHint_Message(result=result, commandHints=commandHintList)

                            # 保留上一次的执行结果
                            if result["type"] == "result":
                                lastCommandResult["rows"] = result["rows"]
                                lastCommandResult["headers"] = result["headers"]
                                lastCommandResult["status"] = result["status"]
                                lastCommandResult["errorCode"] = 0
                            if result["type"] == "error":
                                lastCommandResult["rows"] = []
                                lastCommandResult["headers"] = []
                                lastCommandResult["status"] = result["message"]
                                lastCommandResult["errorCode"] = 1
                            lastCommandResult["sqlIter"] = sqlIter

                            # 对于单句循环模式，只有最后一个返回的结果有意义，其他的结果不作为判断依据
                            if self.singleLoopMode:
                                try:
                                    matchCondition = evalExpression(self.cliHandler, self.singleLoopExpression)
                                except Exception:
                                    matchCondition = False
                                if matchCondition or (
                                    self.singleLoopMaxIter != -1 and self.singleLoopIter >= self.singleLoopMaxIter
                                ):
                                    # 符合条件，退出单语句循环
                                    self.singleLoopMode = False
                                    self.singleLoopExpression = None
                                    self.singleLoopInterval = 0
                                    self.singleLoopIter = 0
                                    self.singleLoopMaxIter = -1
                                else:
                                    # 不符合条件，需要下次继续执行该语句，pos不能加1
                                    time.sleep(self.singleLoopInterval)
                                    self.singleLoopIter = self.singleLoopIter + 1
                            if not self.singleLoopMode:
                                # 如果不是单语句循环模式，则每一个查询都需要输出结果
                                yield result
                    if self.singleLoopMode:
                        # 对于单句循环，无论该单句包含多少个内容，均重复执行
                        continue
                elif parseObject["name"] in ["USE"]:
                    for commandResult in userNameSpace(
                            cls=self.cliHandler,
                            nameSpace=parseObject["nameSpace"]
                    ):
                        if commandResult["type"] == "result":
                            lastCommandResult.clear()
                            lastCommandResult["status"] = commandResult["status"]
                            lastCommandResult["errorCode"] = 0
                        if commandResult["type"] == "error":
                            lastCommandResult["status"] = commandResult["message"]
                            lastCommandResult["errorCode"] = 1
                        yield commandResult
                elif parseObject["name"] in ["SLEEP"]:
                    sleepTime = rewriteStatement(
                        cls=self.cliHandler,
                        statement=parseObject["sleepTime"],
                        commandScriptFile=commandScriptFile
                    )
                    parseObject["sleepTime"] = sleepTime
                    for commandResult in cliSleep(
                            cls=self.cliHandler,
                            sleepTime=parseObject["sleepTime"]
                    ):
                        if commandResult["type"] == "result":
                            lastCommandResult.clear()
                            lastCommandResult["status"] = commandResult["status"]
                            lastCommandResult["errorCode"] = 0
                        if commandResult["type"] == "error":
                            lastCommandResult["status"] = commandResult["message"]
                            lastCommandResult["errorCode"] = 1
                        yield commandResult
                elif parseObject["name"] in ["SPOOL"]:
                    # 根据语句中的变量或者其他定义信息来重写当前语句
                    spoolFile = rewriteStatement(
                        cls=self.cliHandler,
                        statement=parseObject["file"],
                        commandScriptFile=commandScriptFile
                    )
                    if spoolFile != parseObject["file"]:
                        # 如果命令被发生了改写，要打印改写记录
                        rewrotedHint = "REWROTED CMD> _SPOOL " + str(spoolFile)
                        yield {
                            "type": "parse",
                            "rawCommand": None,
                            "formattedCommand": None,
                            "rewrotedCommand": [rewrotedHint, ],
                            "script": commandScriptFile
                        }
                    for commandResult in spool(
                            cls=self.cliHandler,
                            fileName=spoolFile
                    ):
                        if commandResult["type"] == "result":
                            lastCommandResult.clear()
                            lastCommandResult["status"] = commandResult["status"]
                            lastCommandResult["errorCode"] = 0
                        if commandResult["type"] == "error":
                            lastCommandResult["status"] = commandResult["message"]
                            lastCommandResult["errorCode"] = 1
                        yield commandResult
                elif parseObject["name"] in ["SESSION"]:
                    for commandResult in sqlSessionManage(
                            cls=self.cliHandler,
                            action=parseObject["action"],
                            sessionName=parseObject["sessionName"]
                    ):
                        if commandResult["type"] == "result":
                            lastCommandResult.clear()
                            lastCommandResult["status"] = commandResult["status"]
                            lastCommandResult["errorCode"] = 0
                        if commandResult["type"] == "error":
                            lastCommandResult["status"] = commandResult["message"]
                            lastCommandResult["errorCode"] = 1
                        yield commandResult
                elif parseObject["name"] in ["SCRIPT"]:
                    for commandResult in executeEmbeddScript(
                            cls=self.cliHandler,
                            block=parseObject["block"]
                    ):
                        if commandResult["type"] == "result":
                            lastCommandResult.clear()
                            lastCommandResult["status"] = commandResult["status"]
                            lastCommandResult["errorCode"] = 0
                        if commandResult["type"] == "error":
                            lastCommandResult["status"] = commandResult["message"]
                            lastCommandResult["errorCode"] = 1
                        yield commandResult
                elif parseObject["name"] in ["ASSERT"]:
                    for commandResult in assertExpression(
                            cls=self.cliHandler,
                            expression=parseObject["expression"],
                            assertName=parseObject["assertName"]
                    ):
                        if commandResult["type"] == "result":
                            lastCommandResult.clear()
                            lastCommandResult["status"] = commandResult["status"]
                            lastCommandResult["errorCode"] = 0
                        if commandResult["type"] == "error":
                            lastCommandResult["status"] = commandResult["message"]
                            lastCommandResult["errorCode"] = 1
                        yield commandResult
                elif parseObject["name"] in ["LOAD"]:
                    for commandResult in executeLoadRequest(
                            cls=self.cliHandler,
                            requestObject=parseObject
                    ):
                        if commandResult["type"] == "result":
                            lastCommandResult.clear()
                            lastCommandResult["status"] = commandResult["status"]
                            lastCommandResult["errorCode"] = 0
                        if commandResult["type"] == "error":
                            lastCommandResult["status"] = commandResult["message"]
                            lastCommandResult["errorCode"] = 1
                        yield commandResult
                elif parseObject["name"] in ["HTTP"]:
                    if self.ifMode and not self.ifCondition:
                        pos = pos + 1
                        continue
                    # 根据语句中的变量或者其他定义信息来重写当前语句
                    httpRequestTarget, rewrotedCommandList = rewriteAPIStatement(
                        cls=self.cliHandler,
                        requestObject=parseObject,
                        commandScriptFile=commandScriptFile
                    )
                    if len(rewrotedCommandList) != 0:
                        # 如果命令被发生了改写，要打印改写记录
                        yield {
                            "type": "parse",
                            "rawCommand": None,
                            "formattedCommand": None,
                            "rewrotedCommand": rewrotedCommandList,
                            "script": commandScriptFile
                        }

                    # 执行HTTP请求
                    for result in executeAPIStatement(
                            cls=self,
                            apiRequest=parseObject,
                            apiHints=commandHintList):

                        # 处理命令行的提示信息
                        self.processCommandHint_Contents(result=result, commandHints=commandHintList)
                        self.processCommandHint_Status(result=result, commandHints=commandHintList)
                        self.processCommandHint_Message(result=result, commandHints=commandHintList)

                        # 保留上一次的处理结果
                        if result["type"] == "result":
                            lastCommandResult.clear()
                            data = json.loads(result["status"])
                            lastCommandResult["content"] = data["content"]
                            lastCommandResult["status"] = data["status"]
                            lastCommandResult["errorCode"] = 0
                        if result["type"] == "error":
                            lastCommandResult["message"] = result["message"]
                            lastCommandResult["errorCode"] = 1

                        # 判断是否处于单语句循环模式
                        if self.singleLoopMode:
                            matchCondition = evalExpression(self.cliHandler, self.singleLoopExpression)
                            if matchCondition or (
                                    self.singleLoopMaxIter != -1 and self.singleLoopIter >= self.singleLoopMaxIter
                            ):
                                # 符合条件，退出单语句循环
                                self.singleLoopMode = False
                                self.singleLoopExpression = None
                                self.singleLoopInterval = 0
                                self.singleLoopIter = 0
                                self.singleLoopMaxIter = -1
                            else:
                                # 不符合条件，需要下次继续执行该语句，pos不能加1
                                time.sleep(self.singleLoopInterval)
                                self.singleLoopIter = self.singleLoopIter + 1
                        if not self.singleLoopMode:
                            # 最后一次执行，返回结果
                            yield result
                    if self.singleLoopMode:
                        # 如果当前还处于单句循环中，则重复执行语句，即POS位置不能加1
                        continue
                elif parseObject["name"] in ["HTTPSET"]:
                    for result in executeAPISet(
                            cls=self.cliHandler,
                            apiSetRequest=parseObject
                    ):
                        yield result
                elif parseObject["name"] in ["HTTPSESSION"]:
                    for result in apiSessionManage(
                            cls=self.cliHandler,
                            action=parseObject["action"],
                            sessionName=parseObject["sessionName"]
                    ):
                        yield result
                elif parseObject["name"] in ["HOST"]:
                    # 执行主机操作系统命令
                    for result in executeLocalCommand(
                            cls=self.cliHandler,
                            command=parseObject["script"]
                    ):
                        yield result
                elif parseObject["name"] in ["ENDIF"]:
                    self.ifMode = False
                    self.ifCondition = False
                elif parseObject["name"] in ["IF"]:
                    expression = parseObject["expression"]
                    try:
                        ret = evalExpression(self.cliHandler, expression)
                        if type(ret) == bool:
                            self.ifMode = True
                            if ret:
                                self.ifCondition = True
                            else:
                                self.ifCondition = False
                        else:
                            yield {
                                "type": "error",
                                "message": "Set condition fail. SyntaxError =>[not a bool expression]"
                            }
                    except (SyntaxError, NameError) as ae:
                        yield {
                            "type": "error",
                            "message": "Set condition fail. SyntaxError =>[" + str(ae) + "]"
                        }
                elif parseObject["name"] in ["LOOP"]:
                    if parseObject["rule"] == "END":
                        if not self.loopCondition:
                            self.loopMode = False
                        else:
                            pos = self.loopStartPos
                            continue
                    elif parseObject["rule"] == "BREAK":
                        if self.ifCondition and self.ifMode:
                            self.loopCondition = False
                    elif parseObject["rule"] == "CONTINUE":
                        if self.ifCondition and self.ifMode:
                            pos = self.loopStartPos
                            continue
                    elif parseObject["rule"] == "BEGIN":
                        # block循环
                        try:
                            self.loopCondition = not evalExpression(self.cliHandler, parseObject["until"])
                            self.loopMode = True
                            self.loopStartPos = pos
                        except Exception as ex:
                            self.loopMode = False
                            yield {
                                "type": "error",
                                "message": "Loop condition expression error.. SyntaxError =>[" + str(ex) + "]"
                            }
                    elif parseObject["rule"] == "UNTIL":
                        # 但语句循环
                        self.singleLoopExpression = parseObject["until"]
                        self.singleLoopInterval = parseObject["interval"]
                        self.singleLoopMaxIter = parseObject["limit"]
                        self.singleLoopMode = True
                        self.singleLoopIter = 0
                elif parseObject["name"] in ["WHENEVER"]:
                    for result in setWheneverAction(
                            cls=self.cliHandler,
                            action=parseObject["action"],
                            exitCode=parseObject["exitCode"]
                    ):
                        yield result
                elif parseObject["name"] in ["SSH"]:
                    # SSH的命令输出，由于控制台的反馈存在多行的问题，所以需要合并返回内容到一行，再放到lastCommandResult中
                    consoleOutput = []
                    parseObject, rewrotedCommandList = rewriteSshRequest(
                        cls=self.cliHandler,
                        requestObject=parseObject,
                        commandScriptFile=commandScriptFile
                    )
                    if len(rewrotedCommandList) != 0:
                        # 如果命令被发生了改写，要打印改写记录
                        yield {
                            "type": "parse",
                            "rawCommand": None,
                            "formattedCommand": None,
                            "rewrotedCommand": rewrotedCommandList,
                            "script": commandScriptFile
                        }
                    for result in executeSshRequest(
                            cls=self.cliHandler,
                            requestObject=parseObject,
                    ):
                        # 处理命令行的提示信息
                        self.processCommandHint_Status(result=result, commandHints=commandHintList)
                        if "status" in result.keys() and result["status"] is not None:
                            consoleOutput.append(result["status"])
                        lastCommandResult["status"] = "\n".join(consoleOutput)
                        lastCommandResult["errorCode"] = 0

                        if self.singleLoopMode:
                            try:
                                matchCondition = evalExpression(self.cliHandler, self.singleLoopExpression)
                            except Exception:
                                matchCondition = False
                            if matchCondition or (
                                self.singleLoopMaxIter != -1 and self.singleLoopIter >= self.singleLoopMaxIter
                            ):
                                if "TESTCLI_DEBUG" in os.environ:
                                    if matchCondition:
                                        print("[DEBUG] Loop execute statement " + str(self.singleLoopIter) +
                                              ". Matched.")
                                    else:
                                        print("[DEBUG] Loop execute statement " + str(self.singleLoopIter) +
                                              ". Not match.")
                                # 符合条件，退出单语句循环
                                self.singleLoopMode = False
                                self.singleLoopExpression = None
                                self.singleLoopInterval = 0
                                self.singleLoopIter = 0
                                self.singleLoopMaxIter = -1
                            else:
                                if "TESTCLI_DEBUG" in os.environ:
                                    print("[DEBUG] Loop execute statement " + str(self.singleLoopIter) + ". Not match.")
                                # 不符合条件，需要下次继续执行该语句，pos不能加1
                                time.sleep(self.singleLoopInterval)
                                self.singleLoopIter = self.singleLoopIter + 1
                        if not self.singleLoopMode:
                            if "TESTCLI_DEBUG" in os.environ:
                                print("[DEBUG] Loop end " + str(self.singleLoopIter) + ".")
                            # 最后一次执行，要输出结果
                            yield result
                    if self.singleLoopMode:
                        if "TESTCLI_DEBUG" in os.environ:
                            print("[DEBUG] Loop execute statement " + str(self.singleLoopIter) + ".")
                        # 如果当前还处于单句循环中，则重复执行语句，即POS位置保持不变
                        continue
                elif parseObject["name"] in ["JOB"]:
                    # rewriteStatement
                    if "jobName" in parseObject.keys():
                        jobName = rewriteStatement(
                            cls=self.cliHandler,
                            statement=parseObject["jobName"],
                            commandScriptFile=commandScriptFile
                        )
                        parseObject["jobName"] = jobName
                    if "param" in parseObject.keys():
                        params = dict(parseObject["param"])
                        for paramKey, paramValue in params.items():
                            newParamValue = rewriteStatement(
                                cls=self.cliHandler,
                                statement=paramValue,
                                commandScriptFile=commandScriptFile
                            )
                            params.update({paramKey: newParamValue})
                        parseObject["param"] = params
                    for result in self.cliHandler.JobHandler.processRequest(
                            cls=self.cliHandler,
                            requestObject=parseObject,
                    ):
                        yield result
                elif parseObject["name"] in ["COMPARE"]:
                    for result in executeCompareRequest(
                            cls=self.cliHandler,
                            requestObject=parseObject,
                            commandScriptFile=commandScriptFile
                    ):
                        yield result
                elif parseObject["name"] in ["DATA"]:
                    for result in executeDataRequest(
                            cls=self.cliHandler,
                            requestObject=parseObject,
                    ):
                        yield result
                elif parseObject["name"] in ["PARSE_ERROR"]:
                    yield {"type": "error",
                           "message": "TestCli parse error:  " + str(parseObject["reason"])}
                elif parseObject["name"] in ["MONITOR"]:
                    for result in executeMonitorRequest(
                            cls=self.cliHandler,
                            requestObject=parseObject,
                    ):
                        if result["type"] == "result":
                            lastCommandResult["rows"] = result["rows"]
                            lastCommandResult["headers"] = result["headers"]
                            lastCommandResult["status"] = result["status"]
                            lastCommandResult["errorCode"] = 0
                        if result["type"] == "error":
                            lastCommandResult["rows"] = []
                            lastCommandResult["headers"] = []
                            lastCommandResult["status"] = result["message"]
                            lastCommandResult["errorCode"] = 1
                        yield result
                elif parseObject["name"] in ["PLUGIN"]:
                    for result in executePluginRequest(
                            cls=self.cliHandler,
                            requestObject=parseObject,
                    ):
                        if result["type"] == "result":
                            lastCommandResult["rows"] = result["rows"]
                            lastCommandResult["headers"] = result["headers"]
                            lastCommandResult["status"] = result["status"]
                            lastCommandResult["errorCode"] = 0
                        if result["type"] == "error":
                            lastCommandResult["rows"] = []
                            lastCommandResult["headers"] = []
                            lastCommandResult["status"] = result["message"]
                            lastCommandResult["errorCode"] = 1
                        yield result
                else:
                    raise TestCliException("TestCli parse error:  unknown parseObject [" + str(parseObject) + "]")
            except TestCliException as clie:
                yield {"type": "error",
                       "message": str(clie)}

            # 如果需要，打印语句执行时间
            endTime = time.time()
            lastCommandResult["elapsed"] = endTime - startTime

            # 如果指定了reference文件，要判断是否符合reference的结果
            # if self.cliHandler.referenceFile is not None:
            #     print("check reference ...")

            # 记录命令的日志信息
            if self.testOptions.get("SILENT").upper() == 'OFF':
                if parseObject["name"] == "START":
                    commandStatus = ""
                    commandErrorCode = ""
                else:
                    if "status" in lastCommandResult:
                        commandStatus = lastCommandResult["status"]
                    else:
                        commandStatus = ""
                    if "errorCode" in lastCommandResult:
                        commandErrorCode = lastCommandResult["errorCode"]
                    else:
                        commandErrorCode = ""
                yield {
                    "type": "statistics",
                    "startedTime": startTime,
                    "elapsed": endTime - startTime,
                    "processName": self.workerName,
                    "rawCommand": ret_CommandSplitResultsWithComments[pos],
                    "commandType": parseObject["name"],
                    "command": json.dumps(obj=parseObject, sort_keys=True, ensure_ascii=False),
                    "commandStatus": commandStatus,
                    "errorCode": commandErrorCode,
                    "scenarioId": self.scenarioId,
                    "scenarioName": self.scenarioName
                }

            # 开始执行下一个语句
            pos = pos + 1
