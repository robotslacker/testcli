# -*- coding: utf-8 -*-
from antlr4.Token import Token
import re

from .antlrgen.SQLParser import SQLParser
from .antlrgen.SQLParserVisitor import SQLParserVisitor
from .antlrgen.SQLLexer import SQLLexer


class SQLVisitor(SQLParserVisitor):
    def __init__(self, tokens, defaultNameSpace=None):
        # 词法符号表
        self.tokens = tokens
        # 解析空间 API/SQL，先转换成大写
        self.defaultNameSpace = None if defaultNameSpace is None else defaultNameSpace.upper()
        # 解析是否正常完成
        self.isFinished = True
        # 返回去掉了注释信息的解析结果
        self.parsedObject = None
        # 包含了所有注释信息的原语句（格式保持不变，包括空行，换行符号等)
        self.originScripts = None
        # 有意义的注释信息(即用-- [Hint] 开头的SQL语句, 或者用# [Hint]|// [Hint] 开头的API语句), 一个语句有多个注释信息的，用数组返回
        self.hints = []
        # 如果成功，返回0； 如果失败，返回-1； 
        self.errorCode = 0
        # 如果成功，返回空；如果失败，返回解析的错误提示信息
        self.errorMsg = ""

    """
        功能：返回分析上下文分词索引
             提示计入
        参数：
             ctx: 上下文
        返回：
            start: 开始索引号
            end: 结束索引号
    """
    @staticmethod
    def getSourceInterval(ctx):
        start, end = ctx.getSourceInterval()
        while start > 0:
            token = ctx.parser._input.tokens[start-1]
            if token.channel != SQLLexer.HINT_CHANNEL:
                break
            start -= 1
        return start, end

    """
        功能：返回指定通道文本
        参数：
            tokens 分词数组
            channel 分词通道
        返回：
            分词数组指定通道的分词文本
    """
    @staticmethod
    def getText(tokens, channel=Token.DEFAULT_CHANNEL):
        # 返回单一通道的信息
        return ''.join(token.text if token.channel == channel else '' for token in tokens)

    """
        功能：返回全部文本
        参数：
            tokens 分词数组
        返回：
            指定分词数组的文本
    """

    @staticmethod
    def getSource(tokens):
        # 返回单一通道的信息
        return ''.join(token.text for token in tokens)

    """
        功能：返回提示文本
        参数：
            tokens 分词数组
        返回：
            指定分词数组中提示分词文本
    """
    @staticmethod
    def getHint(tokens):
        hints = []
        for token in tokens:
            if token.channel == SQLLexer.HINT_CHANNEL:
                # 使用提示[Hint]分割字符串 
                pattern = r"\[ *Hint *\]"
                hint_arr = re.split(pattern, token.text, flags=re.IGNORECASE)
                if len(hint_arr) > 1:
                    hint = hint_arr[1]
                else:
                    hint = None
                if hint is not None:
                    # 删除后面的换行符号
                    tmp = hint.splitlines()
                    if len(tmp) > 0:
                        hint = tmp[0].strip()
                    else:
                        hint = ''
                if (hint is not None) and (hint != ''):
                    hints.append(hint)
        if len(hints) == 0:
            return None
        if len(hints) == 1:
            return hints[0]
        return hints

    """
        功能：访问语法树的程序节点
        参数：
            ctx: 上下文
        返回：
            isFinished: 完成与否
            parsedObject: 分析结果列表
            originScripts: 源文件列表
            hints: 提示列表
            errorCode: 错误码列表
            errorMsg: 错误信息列表
    """
    def visitProg(self, ctx: SQLParser.ProgContext):
        self.visitChildren(ctx)
        return self.isFinished, self.parsedObject, self.originScripts, self.hints, self.errorCode, self.errorMsg
    
    def visitCommand(self, ctx: SQLParser.CommandContext):
        return self.visitChildren(ctx)
        
    def visitExit(self, ctx: SQLParser.ExitContext):
        parsedObject = {'name': 'EXIT'}
        
        if ctx.INT() is not None:
            parsedObject.update({'exitValue': int(ctx.INT().getText())})
        else:
            parsedObject.update({'exitValue': 0})

        # 获取源文件
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        originScript = self.getSource(tokens)

        # 获取提示信息
        hint = self.getHint(tokens)

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        self.originScripts = originScript
        self.parsedObject = parsedObject
        self.hints = hint
        self.errorCode = errorCode
        self.errorMsg = errorMsg
        return parsedObject, originScript, hint, errorCode, errorMsg

    def visitQuit(self, ctx: SQLParser.QuitContext):
        parsedObject = {'name': 'QUIT'}
        
        if ctx.INT() is not None:
            parsedObject.update({'exitValue': int(ctx.INT().getText())})
        else:
            parsedObject.update({'exitValue': 0})

        # 获取源文件
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        originScript = self.getSource(tokens)

        # 获取提示信息
        hint = self.getHint(tokens)

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        self.originScripts = originScript
        self.parsedObject = parsedObject
        self.hints = hint
        self.errorCode = errorCode
        self.errorMsg = errorMsg
        return parsedObject, originScript, hint, errorCode, errorMsg

    def visitUse(self, ctx: SQLParser.UseContext):
        parsedObject = {'name': 'USE'}
        nameSpace = None
        if ctx.API() is not None:
            nameSpace = 'API'
        elif ctx.SQL() is not None:
            nameSpace = 'SQL'
        parsedObject.update({'nameSpace': nameSpace})

        # 获取源文件
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        originScript = self.getSource(tokens)

        # 获取提示信息
        hint = self.getHint(tokens)

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        self.originScripts = originScript
        self.parsedObject = parsedObject
        self.hints = hint
        self.errorCode = errorCode
        self.errorMsg = errorMsg
        return parsedObject, originScript, hint, errorCode, errorMsg

    def visitSleep(self, ctx: SQLParser.SleepContext):
        parsedObject = {
            'name': 'SLEEP',
            "sleepTime": int(ctx.INT().getText())
        }

        # 获取源文件
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        originScript = self.getSource(tokens)

        # 获取提示信息
        hint = self.getHint(tokens)

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        self.originScripts = originScript
        self.parsedObject = parsedObject
        self.hints = hint
        self.errorCode = errorCode
        self.errorMsg = errorMsg
        return parsedObject, originScript, hint, errorCode, errorMsg

    def visitConnect(self, ctx: SQLParser.ConnectContext):
        parsedObject = {'name': 'CONNECT'}

        # 用户信息
        if ctx.connectlocal() is not None:
            result, script, hint, code, message = self.visit(ctx.connectlocal())
            parsedObject.update(result)
        if ctx.connectjdbc() is not None:
            result, script, hint, code, message = self.visit(ctx.connectjdbc())
            parsedObject.update(result)

        # 获取源文件
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        originScript = self.getSource(tokens)

        # 获取提示信息
        hint = self.getHint(tokens)

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        self.originScripts = originScript
        self.parsedObject = parsedObject
        self.hints = hint
        self.errorCode = errorCode
        self.errorMsg = errorMsg
        return parsedObject, originScript, hint, errorCode, errorMsg

    def visitConnectjdbc(self, ctx: SQLParser.ConnectjdbcContext):
        parsedObject = {}
        if ctx.connectUserInfo() is not None:
            result, script, hint, code, message = self.visit(ctx.connectUserInfo())
            parsedObject.update(result)
        if ctx.connectDriver() is not None:
            result, script, hint, code, message = self.visit(ctx.connectDriver())
            parsedObject.update(result)
        if ctx.connectDriverSchema() is not None:
            result, script, hint, code, message = self.visit(ctx.connectDriverSchema())
            parsedObject.update(result)
        if ctx.connectDriverType() is not None:
            result, script, hint, code, message = self.visit(ctx.connectDriverType())
            parsedObject.update(result)
        if ctx.connectHost() is not None:
            result, script, hint, code, message = self.visit(ctx.connectHost())
            parsedObject.update(result)
        if ctx.connectPort() is not None:
            result, script, hint, code, message = self.visit(ctx.connectPort())
            parsedObject.update(result)
        if ctx.connectService() is not None:
            result, script, hint, code, message = self.visit(ctx.connectService())
            parsedObject.update(result)
        if ctx.connectParameters() is not None:
            result, script, hint, code, message = self.visit(ctx.connectParameters())
            parsedObject.update(result)

        # 获取源文件
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        originScript = self.getSource(tokens)

        # 获取提示信息
        hint = self.getHint(tokens)

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        return parsedObject, originScript, hint, errorCode, errorMsg

    def visitConnectlocal(self, ctx: SQLParser.ConnectlocalContext):
        parsedObject = {}
        if ctx.connectlocalService() is not None:
            result, script, hint, code, message = self.visit(ctx.connectlocalService())
            parsedObject.update(result)

        # 获取源文件
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        originScript = self.getSource(tokens)

        # 获取提示信息
        hint = self.getHint(tokens)

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        return parsedObject, originScript, hint, errorCode, errorMsg

    def visitConnectlocalService(self, ctx: SQLParser.ConnectlocalServiceContext):
        parsedObject = {}
        if ctx.CONNECT_STRING() is not None:
            parsedObject.update({'localService': ctx.CONNECT_STRING().getText()})

        # 获取源文件
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        originScript = self.getSource(tokens)

        # 获取提示信息
        hint = self.getHint(tokens)

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        return parsedObject, originScript, hint, errorCode, errorMsg

    def visitConnectService(self, ctx: SQLParser.ConnectServiceContext):
        parsedObject = {}
        if ctx.CONNECT_STRING() is not None:
            if len(ctx.CONNECT_STRING()) == 2:
                parsedObject.update(
                    {'service': ctx.CONNECT_STRING()[0].getText() + ":" + ctx.CONNECT_STRING()[1].getText()}
                )
            else:
                parsedObject.update(
                    {'service': ctx.CONNECT_STRING()[0].getText()}
                )

        # 获取源文件
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        originScript = self.getSource(tokens)

        # 获取提示信息
        hint = self.getHint(tokens)

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        return parsedObject, originScript, hint, errorCode, errorMsg

    # connect中的用户信息
    def visitConnectUserInfo(self, ctx: SQLParser.ConnectUserInfoContext):
        parsedObject = {}

        # 用户名
        if ctx.connectUser() is not None:
            result, script, hint, code, message = self.visit(ctx.connectUser())
            parsedObject.update(result)

        # password
        if ctx.connectPassword() is not None:
            result, script, hint, code, message = self.visit(ctx.connectPassword())
            parsedObject.update(result)

        # 获取源文件
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        originScript = self.getSource(tokens)

        # 获取提示信息
        hint = self.getHint(tokens)

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        return parsedObject, originScript, hint, errorCode, errorMsg

    def visitConnectUser(self, ctx: SQLParser.ConnectUserContext):
        parsedObject = {}
        if ctx.CONNECT_STRING() is not None:
            parsedObject.update({'username': ctx.CONNECT_STRING().getText()})

        # 获取源文件
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        originScript = self.getSource(tokens)

        # 获取提示信息
        hint = self.getHint(tokens)

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        return parsedObject, originScript, hint, errorCode, errorMsg

    def visitConnectPassword(self, ctx: SQLParser.ConnectPasswordContext):
        parsedObject = {}
        if ctx.CONNECT_STRING() is not None:
            parsedObject.update({'password': ctx.CONNECT_STRING().getText()})

        # 获取源文件
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        originScript = self.getSource(tokens)

        # 获取提示信息
        hint = self.getHint(tokens)

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        return parsedObject, originScript, hint, errorCode, errorMsg

    def visitConnectDriver(self, ctx: SQLParser.ConnectDriverContext):
        parsedObject = {}
        if ctx.JDBC() is not None:
            parsedObject.update({'driver': "jdbc"})

        # 获取源文件
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        originScript = self.getSource(tokens)

        # 获取提示信息
        hint = self.getHint(tokens)

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        return parsedObject, originScript, hint, errorCode, errorMsg

    def visitConnectDriverSchema(self, ctx: SQLParser.ConnectDriverSchemaContext):
        parsedObject = {}
        if ctx.CONNECT_STRING() is not None:
            parsedObject.update({'driverSchema': ctx.CONNECT_STRING().getText()})

        # 获取源文件
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        originScript = self.getSource(tokens)

        # 获取提示信息
        hint = self.getHint(tokens)

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        return parsedObject, originScript, hint, errorCode, errorMsg

    def visitConnectDriverType(self, ctx: SQLParser.ConnectDriverSchemaContext):
        parsedObject = {}
        if ctx.CONNECT_STRING() is not None:
            parsedObject.update({'driverType': ctx.CONNECT_STRING().getText()})

        # 获取源文件
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        originScript = self.getSource(tokens)

        # 获取提示信息
        hint = self.getHint(tokens)

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        return parsedObject, originScript, hint, errorCode, errorMsg

    def visitConnectHost(self, ctx: SQLParser.ConnectHostContext):
        parsedObject = {'host': ctx.getText()}

        # 获取源文件
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        originScript = self.getSource(tokens)

        # 获取提示信息
        hint = self.getHint(tokens)

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message
        return parsedObject, originScript, hint, errorCode, errorMsg

    def visitConnectPort(self, ctx: SQLParser.ConnectPortContext):
        parsedObject = {'port': int(ctx.getText().replace(":", ""))}

        # 获取源文件
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        originScript = self.getSource(tokens)

        # 获取提示信息
        hint = self.getHint(tokens)

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message
        return parsedObject, originScript, hint, errorCode, errorMsg

    def visitConnectParameters(self, ctx: SQLParser.ConnectParametersContext):
        parsedObject = {}

        # 连接参数信息
        if ctx.connectParameter() is not None:
            result, script, hint, code, message = self.visit(ctx.connectParameter())
            parsedObject.update(result)

        # 获取源文件
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        originScript = self.getSource(tokens)

        # 获取提示信息
        hint = self.getHint(tokens)

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        return parsedObject, originScript, hint, errorCode, errorMsg

    def visitConnectParameter(self, ctx: SQLParser.ConnectParameterContext):
        parsedObject = {}

        if ctx.connectParameterName() is not None:
            result, script, hint, code, message = self.visit(ctx.connectParameterName())
            parsedObject.update(result)

        if ctx.connectParameterValue() is not None:
            result, script, hint, code, message = self.visit(ctx.connectParameterValue())
            parsedObject.update(result)

        # 获取源文件
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        originScript = self.getSource(tokens)

        # 获取提示信息
        hint = self.getHint(tokens)

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message
        return parsedObject, originScript, hint, errorCode, errorMsg

    def visitConnectParameterName(self, ctx: SQLParser.ConnectParameterNameContext):
        parsedObject = {'parameterName': ctx.getText()}

        # 获取源文件
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        originScript = self.getSource(tokens)

        # 获取提示信息
        hint = self.getHint(tokens)

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message
        return parsedObject, originScript, hint, errorCode, errorMsg

    def visitConnectParameterValue(self, ctx: SQLParser.ConnectParameterValueContext):
        parsedObject = {'parameterValue': ctx.getText()}

        # 获取源文件
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        originScript = self.getSource(tokens)

        # 获取提示信息
        hint = self.getHint(tokens)

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message
        return parsedObject, originScript, hint, errorCode, errorMsg

    def visitDisconnect(self, ctx: SQLParser.DisconnectContext):
        parsedObject = {'name': 'DISCONNECT'}

        # 获取源文件
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        originScript = self.getSource(tokens)

        # 获取提示信息
        hint = self.getHint(tokens)

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        self.originScripts = originScript
        self.parsedObject = parsedObject
        self.hints = hint
        self.errorCode = errorCode
        self.errorMsg = errorMsg
        return parsedObject, originScript, hint, errorCode, errorMsg

    def visitEcho(self, ctx: SQLParser.EchoContext):
        parsedObject = {'name': 'ECHO'}

        # 删除BLOCK 末尾的 ECHO OFF
        block = ctx.EchoBlock().getText()
        pattern = '\n *echo\\s+off'
        blocks = re.split(pattern, block, flags=re.IGNORECASE)
        if len(blocks) > 1:
            parsedObject.update({'block': blocks[0]})
        else:
            self.isFinished = False

        # 需要输出的文件名
        param = ctx.ECHO_OPEN().getText().partition(' ')[2]
        if param is not None:
            param = param.splitlines()[0]
            parsedObject.update({'param': str(param).strip()})

        # 获取源文件
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        originScript = self.getSource(tokens)

        # 获取提示信息
        hint = self.getHint(tokens)

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        self.originScripts = originScript
        self.parsedObject = parsedObject
        self.hints = hint
        self.errorCode = errorCode
        self.errorMsg = errorMsg
        return parsedObject, originScript, hint, errorCode, errorMsg

    def visitStart(self, ctx: SQLParser.StartContext):
        parsedObject = {'name': 'START'}
        if ctx.INT() is not None:
            parsedObject.update({'loopTimes': int(ctx.INT().getText())})
        else:
            parsedObject.update({'loopTimes': 1})

        expression_list = []
        for expression in ctx.expression():
            result, script, hint, code, message = self.visit(expression)
            expression_list.append(result)

        parsedObject.update({'scriptList': expression_list})

        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end + 1]
        # 源文件
        originScript = self.getSource(tokens)
        # 提示信息
        hint = self.getHint(tokens)
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = 1
            errorMsg = ctx.exception.message
            self.isFinished = False

        self.parsedObject = parsedObject
        self.originScripts = originScript
        self.hints = hint
        self.errorCode = errorCode
        self.errorMsg = errorMsg

        return parsedObject, originScript, hint, errorCode, errorMsg

    def visitSingleExpression(self, ctx: SQLParser.SingleExpressionContext):
        expression = ctx.getText()

        # 获取源文件
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        originScript = self.getSource(tokens)

        # 获取提示信息
        hint = self.getHint(tokens)

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        return expression, originScript, hint, errorCode, errorMsg

    def visitExpression(self, ctx: SQLParser.ExpressionContext):
        expression = ctx.getText()

        # 获取源文件
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        originScript = self.getSource(tokens)

        # 获取提示信息
        hint = self.getHint(tokens)

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        return expression, originScript, hint, errorCode, errorMsg

    def visitSet(self, ctx: SQLParser.SetContext):
        parsedObject = {'name': 'SET'}

        expression_list = []
        for expression in ctx.singleExpression():
            result, script, hint, code, message = self.visit(expression)
            expression_list.append(result)

        if ctx.AT() is not None:
            parsedObject.update({'scope': "global"})
        else:
            parsedObject.update({'scope': "local"})
        if len(expression_list) >= 1:
            parsedObject.update({'optionName': expression_list[0]})
        if len(expression_list) >= 2:
            optionValue = " ".join(expression_list[1:])
            parsedObject.update({"optionValue": optionValue})

        # 获取源文件
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end + 1]
        originScript = self.getSource(tokens)

        # 获取提示信息
        hint = self.getHint(tokens)

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        self.parsedObject = parsedObject
        self.originScripts = originScript
        self.hints = hint
        self.errorCode = errorCode
        self.errorMsg = errorMsg

        return parsedObject, originScript, hint, errorCode, errorMsg

    def visitSession(self, ctx: SQLParser.SessionContext):
        action = ""
        if ctx.SESSION_SAVE() is not None:
            action = 'SAVE'
        elif ctx.SESSION_RELEASE() is not None:
            action = 'RELEASE'
        elif ctx.SESSION_RESTORE() is not None:
            action = 'RESTORE'
        elif ctx.SESSION_SAVEURL() is not None:
            action = 'SAVEURL'
        elif ctx.SESSION_SHOW() is not None:
            action = 'SHOW'

        parsedObject = {'name':  'SESSION', 'action': action}
        if ctx.SESSION_NAME() is not None:
            parsedObject.update({'sessionName': ctx.SESSION_NAME().getText()})
        else:
            parsedObject.update({'sessionName': None})
            
        # 获取源文件
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end + 1]
        originScript = self.getSource(tokens)

        # 获取提示信息
        hint = self.getHint(tokens)

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        self.parsedObject = parsedObject
        self.originScripts = originScript
        self.hints = hint
        self.errorCode = errorCode
        self.errorMsg = errorMsg

        return parsedObject, originScript, hint, errorCode, errorMsg

    def visitLoad(self, ctx: SQLParser.LoadContext):
        parsedObject = {'name': 'LOAD'}

        # 获取源文件
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end + 1]
        originScript = self.getSource(tokens)

        # 加载的选项
        option = str(ctx.LOAD_OPTION().getText()).strip().upper()
        parsedObject.update({"option": option})

        # 加载的内容
        if ctx.LOAD_EXPRESSION() is not None:
            if option.upper() == "DRIVER":
                driverName = None
                driverFile = None
                if len(ctx.LOAD_EXPRESSION()) >= 1:
                    driverName = str((ctx.LOAD_EXPRESSION()[0].getText())).strip()
                    if driverName.startswith('"') and driverName.endswith('"'):
                        driverName = driverName[1:-1]
                    if driverName.startswith("'") and driverName.endswith("'"):
                        driverName = driverName[1:-1]
                if len(ctx.LOAD_EXPRESSION()) >= 2:
                    driverFile = str((ctx.LOAD_EXPRESSION()[1].getText())).strip()
                    if driverFile.startswith('"') and driverFile.endswith('"'):
                        driverFile = driverFile[1:-1]
                    if driverFile.startswith("'") and driverFile.endswith("'"):
                        driverFile = driverFile[1:-1]
                parsedObject.update(
                    {
                        "driverName": driverName,
                        "driverFile": driverFile,
                     }
                )
            if option.upper() == "PLUGIN":
                pluginFile = str((ctx.LOAD_EXPRESSION()[0].getText())).strip()
                if pluginFile.startswith('"') and pluginFile.endswith('"'):
                    pluginFile = pluginFile[1:-1]
                if pluginFile.startswith("'") and pluginFile.endswith("'"):
                    pluginFile = pluginFile[1:-1]
                parsedObject.update({"pluginFile": pluginFile})
            if option.upper() == "MAP":
                mapFile = str((ctx.LOAD_EXPRESSION()[0].getText())).strip()
                if mapFile.startswith('"') and mapFile.endswith('"'):
                    mapFile = mapFile[1:-1]
                if mapFile.startswith("'") and mapFile.endswith("'"):
                    mapFile = mapFile[1:-1]
                parsedObject.update({"mapFile": mapFile})

        # 获取提示信息
        hint = self.getHint(tokens)

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        self.parsedObject = parsedObject
        self.originScripts = originScript
        self.hints = hint
        self.errorCode = errorCode
        self.errorMsg = errorMsg

        return parsedObject, originScript, hint, errorCode, errorMsg

    def visitWheneverError(self, ctx:SQLParser.WheneverErrorContext):
        param = None
        if ctx.CONTINUE() is not None:
            param = ctx.CONTINUE().getText()
        elif ctx.EXIT() is not None:
            param = ctx.EXIT().getText()
        
        parsedObject = {'name': 'WHENEVER_ERROR' , 'rule': ctx.getRuleIndex(), 'param': param }
    
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        # 源文件
        originScript = self.getSource(tokens)
        # 提示信息
        hint = self.getHint(tokens)
        errorCode = 0
        errorMsg = None
        if (ctx.exception is not None):
            errorCode = -1
            errorMsg = ctx.exception.message
            self.isFinished = False

        self.parsedObject.append(parsedObject)
        self.originScripts.append(originScript)
        self.hints.append(hint)
        self.errorCode.append(errorCode)
        self.errorMsg.append(errorMsg)

        return  parsedObject, originScript, hint, errorCode, errorMsg

    def visitSpool(self, ctx: SQLParser.SpoolContext):
        content = ctx.String().getText()
        
        parsedObject = {'name': 'SPOOL', 'file': content}

        # 获取源文件
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end + 1]
        originScript = self.getSource(tokens)

        # 获取提示信息
        hint = self.getHint(tokens)

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        self.parsedObject = parsedObject
        self.originScripts = originScript
        self.hints = hint
        self.errorCode = errorCode
        self.errorMsg = errorMsg

        return parsedObject, originScript, hint, errorCode, errorMsg

    def visitScript(self, ctx: SQLParser.ScriptContext):
        parsedObject = {'name': 'SCRIPT'}

        # 删除BLOCK 末尾的 %}
        if ctx.ScriptBlock() is not None:
            block = ctx.ScriptBlock().getText()
            if str(block).endswith('\n%}'):
                block = str(block[:-3])
                if block.startswith("\n"):
                    block = block[1:]
                parsedObject.update({'block': block})
            else:
                self.isFinished = False
        else:
            self.isFinished = False

        # 获取源文件
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        originScript = self.getSource(tokens)

        # 获取提示信息
        hint = self.getHint(tokens)

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        self.originScripts = originScript
        self.parsedObject = parsedObject
        self.hints = hint
        self.errorCode = errorCode
        self.errorMsg = errorMsg
        return parsedObject, originScript, hint, errorCode, errorMsg

    # def visitBaseCommand(self, ctx: SQLParser.BaseCommandContext):
    #     print("=== + " + str(ctx.getText()))
    #     # basectx = BaseParser.BaseCommandContext()
    #     return self.baseVisitor.visitBaseCommand(BaseParser.BaseCommandContext(basectx))

    def visitAssert(self, ctx: SQLParser.AssertContext):
        parsedObject = {'name': 'ASSERT'}

        if ctx.ASSERT_EXPRESSION() is not None:
            expression = str(ctx.ASSERT_EXPRESSION().getText()).strip()
            if expression.startswith('{%'):
                expression = expression[2:]
            if expression.endswith('%}'):
                expression = expression[:-2]
            parsedObject.update({'expression': expression})
        else:
            parsedObject.update({'expression': ""})

        # 获取源文件
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        originScript = self.getSource(tokens)

        # 获取提示信息
        hint = self.getHint(tokens)

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        self.originScripts = originScript
        self.parsedObject = parsedObject
        self.hints = hint
        self.errorCode = errorCode
        self.errorMsg = errorMsg
        return parsedObject, originScript, hint, errorCode, errorMsg

    def visitSql(self, ctx: SQLParser.SqlContext):
        return self.visitChildren(ctx)

    def visitSqlCreate(self, ctx: SQLParser.SqlCreateContext):
        # 获取源文件
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        originScript = self.getSource(tokens)

        statement = ctx.SQL_CREATE().getText() + self.getText(tokens, SQLLexer.SQLSTATEMENT_CHANNEL)
        parsedObject = {'name': 'CREATE', 'statement': statement}

        # 获取提示信息
        hint = self.getHint(tokens)

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        # 如果SQL没有结尾，要返回没有结尾的标志
        if (ctx.SQL_END() is None) or ((ctx.SQL_END().getText() != ';') and (ctx.SQL_END().getText() != '\n/')):
            self.isFinished = False

        self.originScripts = originScript
        self.parsedObject = parsedObject
        self.hints = hint
        self.errorCode = errorCode
        self.errorMsg = errorMsg
        return parsedObject, originScript, hint, errorCode, errorMsg

    def visitSqlDrop(self, ctx: SQLParser.SqlDropContext):
        # 获取源文件
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        originScript = self.getSource(tokens)

        statement = ctx.SQL_DROP().getText() + self.getText(tokens, SQLLexer.SQLSTATEMENT_CHANNEL)
        parsedObject = {'name': 'DROP', 'statement': statement}

        # 获取提示信息
        hint = self.getHint(tokens)

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        # 如果SQL没有结尾，要返回没有结尾的标志
        if (ctx.SQL_END() is None) or ((ctx.SQL_END().getText() != ';') and (ctx.SQL_END().getText() != '\n/')):
            self.isFinished = False

        self.originScripts = originScript
        self.parsedObject = parsedObject
        self.hints = hint
        self.errorCode = errorCode
        self.errorMsg = errorMsg
        return parsedObject, originScript, hint, errorCode, errorMsg

    def visitSqlReplace(self, ctx: SQLParser.SqlReplaceContext):
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]

        statement = ctx.SQL_REPLACE().getText() + self.getText(tokens, SQLLexer.SQLSTATEMENT_CHANNEL)

        parsedObject = {'name': 'REPLACE', 'rule': ctx.getRuleIndex(), 'statement': statement}
        # 包含注释和提示
        originScript = self.getSource(tokens)
        # 句子中的提示
        hint = self.getHint(tokens)
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message
            self.isFinished = False
        if (ctx.SQL_END() is None) or ((ctx.SQL_END().getText() != ';') and (ctx.SQL_END().getText() != '\n/')):
            errorCode = -1
            self.isFinished = False

        self.parsedObject.append(parsedObject)
        self.originScripts.append(originScript)
        self.hints.append(hint)
        self.errorCode.append(errorCode)
        self.errorMsg.append(errorMsg)

        return parsedObject, originScript, hint, errorCode, errorMsg

    def visitSqlInsert(self, ctx: SQLParser.SqlInsertContext):
        # 获取源文件
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        originScript = self.getSource(tokens)

        statement = ctx.SQL_INSERT().getText() + self.getText(tokens, SQLLexer.SQLSTATEMENT_CHANNEL)
        parsedObject = {'name': 'INSERT', 'statement': statement}

        # 获取提示信息
        hint = self.getHint(tokens)

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        # 如果SQL没有结尾，要返回没有结尾的标志
        if (ctx.SQL_END() is None) or ((ctx.SQL_END().getText() != ';') and (ctx.SQL_END().getText() != '\n/')):
            self.isFinished = False

        self.originScripts = originScript
        self.parsedObject = parsedObject
        self.hints = hint
        self.errorCode = errorCode
        self.errorMsg = errorMsg
        return parsedObject, originScript, hint, errorCode, errorMsg

    def visitSqlUpdate(self, ctx: SQLParser.SqlUpdateContext):
        # 获取源文件
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        originScript = self.getSource(tokens)

        statement = ctx.SQL_UPDATE().getText() + self.getText(tokens, SQLLexer.SQLSTATEMENT_CHANNEL)
        parsedObject = {'name': 'UPDATE', 'statement': statement}

        # 获取提示信息
        hint = self.getHint(tokens)

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        # 如果SQL没有结尾，要返回没有结尾的标志
        if (ctx.SQL_END() is None) or ((ctx.SQL_END().getText() != ';') and (ctx.SQL_END().getText() != '\n/')):
            self.isFinished = False

        self.originScripts = originScript
        self.parsedObject = parsedObject
        self.hints = hint
        self.errorCode = errorCode
        self.errorMsg = errorMsg
        return parsedObject, originScript, hint, errorCode, errorMsg

    def visitSqlDelete(self, ctx: SQLParser.SqlDeleteContext):
        # 获取源文件
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        originScript = self.getSource(tokens)

        statement = ctx.SQL_DELETE().getText() + self.getText(tokens, SQLLexer.SQLSTATEMENT_CHANNEL)
        parsedObject = {'name': 'DELETE', 'statement': statement}

        # 获取提示信息
        hint = self.getHint(tokens)

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        # 如果SQL没有结尾，要返回没有结尾的标志
        if (ctx.SQL_END() is None) or ((ctx.SQL_END().getText() != ';') and (ctx.SQL_END().getText() != '\n/')):
            self.isFinished = False

        self.originScripts = originScript
        self.parsedObject = parsedObject
        self.hints = hint
        self.errorCode = errorCode
        self.errorMsg = errorMsg
        return parsedObject, originScript, hint, errorCode, errorMsg

    def visitSqlSelect(self, ctx: SQLParser.SqlSelectContext):
        # 获取源文件
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        originScript = self.getSource(tokens)

        statement = ctx.SQL_SELECT().getText() + self.getText(tokens, SQLLexer.SQLSTATEMENT_CHANNEL)
        parsedObject = {'name': 'SELECT', 'statement': statement}

        # 获取提示信息
        hint = self.getHint(tokens)

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        # 如果SQL没有结尾，要返回没有结尾的标志
        if (ctx.SQL_END() is None) or ((ctx.SQL_END().getText() != ';') and (ctx.SQL_END().getText() != '\n/')):
            self.isFinished = False

        self.originScripts = originScript
        self.parsedObject = parsedObject
        self.hints = hint
        self.errorCode = errorCode
        self.errorMsg = errorMsg
        return parsedObject, originScript, hint, errorCode, errorMsg

    def visitSqlCommitRollback(self, ctx: SQLParser.SqlCommitRollbackContext):
        # 获取源文件
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        originScript = self.getSource(tokens)

        parsedObject = {}
        if ctx.SQL_COMMIT() is not None:
            parsedObject = {'name': 'COMMIT', 'statement': ctx.SQL_COMMIT().getText()}
        if ctx.SQL_ROLLBACK() is not None:
            parsedObject = {'name': 'ROLLBACK', 'statement': ctx.SQL_ROLLBACK().getText()}

        # 获取提示信息
        hint = self.getHint(tokens)

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        # 如果SQL没有结尾，要返回没有结尾的标志
        self.originScripts = originScript
        self.parsedObject = parsedObject
        self.hints = hint
        self.errorCode = errorCode
        self.errorMsg = errorMsg
        return parsedObject, originScript, hint, errorCode, errorMsg

    def visitSqlDeclare(self, ctx: SQLParser.SqlDeclareContext):
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end + 1]

        parsedObject = {}
        if ctx.SQL_DECLARE() is not None:
            statement = ctx.SQL_DECLARE().getText() + self.getText(tokens, SQLLexer.SQLSTATEMENT_CHANNEL)
            parsedObject = {
                'name': 'DECLARE',
                'statement': statement}
        if ctx.SQL_BEGIN() is not None:
            statement = ctx.SQL_BEGIN().getText() + self.getText(tokens, SQLLexer.SQLSTATEMENT_CHANNEL)
            parsedObject = {
                'name': 'BEGIN',
                'statement': statement}

        # 包含注释和提示
        originScript = self.getSource(tokens)

        # 获取提示信息
        hint = self.getHint(tokens)

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        # 如果SQL没有结尾，要返回没有结尾的标志
        if (ctx.SQL_SLASH() is None) or (ctx.SQL_SLASH().getText() != '\n/'):
            self.isFinished = False

        self.originScripts = originScript
        self.parsedObject = parsedObject
        self.hints = hint
        self.errorCode = errorCode
        self.errorMsg = errorMsg
        return parsedObject, originScript, hint, errorCode, errorMsg

    def visitSqlCreateProcedure(self, ctx: SQLParser.SqlCreateProcedureContext):
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        
        statement = ctx.SQL_CREATE_PROCEDURE().getText() + self.getText(tokens, SQLLexer.SQLSTATEMENT_CHANNEL)
        parsedObject = {
            'name': 'PROCEDURE',
            'statement': statement}

        # 包含注释和提示
        originScript = self.getSource(tokens)

        # 获取提示信息
        hint = self.getHint(tokens)

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        # 如果SQL没有结尾，要返回没有结尾的标志
        if (ctx.SQL_SLASH() is None) or (ctx.SQL_SLASH().getText() != '\n/'):
            self.isFinished = False

        self.originScripts = originScript
        self.parsedObject = parsedObject
        self.hints = hint
        self.errorCode = errorCode
        self.errorMsg = errorMsg
        return parsedObject, originScript, hint, errorCode, errorMsg
