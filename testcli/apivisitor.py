# -*- coding: utf-8 -*-
from antlr4.Token import Token
import re

from .antlrgen.APIParser import APIParser
from .antlrgen.APIParserVisitor import APIParserVisitor
from .antlrgen.APILexer import APILexer


class APIVisitor(APIParserVisitor):
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
            if token.channel != APILexer.HINT_CHANNEL:
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
            if token.channel == APILexer.HINT_CHANNEL:
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
    def visitProg(self, ctx: APIParser.ProgContext):
        self.visitChildren(ctx)
        return self.isFinished, self.parsedObject, self.originScripts, self.hints, self.errorCode, self.errorMsg
    
    def visitCommand(self, ctx: APIParser.CommandContext):
        return self.visitChildren(ctx)
        
    def visitExit(self, ctx: APIParser.ExitContext):
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

    def visitQuit(self, ctx: APIParser.QuitContext):
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

    def visitUse(self, ctx: APIParser.UseContext):
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

    def visitSleep(self, ctx: APIParser.SleepContext):
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

    def visitEcho(self, ctx: APIParser.EchoContext):
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

    def visitStart(self, ctx: APIParser.StartContext):
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

    def visitSingleExpression(self, ctx: APIParser.SingleExpressionContext):
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

    def visitExpression(self, ctx: APIParser.ExpressionContext):
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

    def visitSet(self, ctx: APIParser.SetContext):
        parsedObject = {'name': 'SET'}

        expression_list = []
        for expression in ctx.singleExpression():
            result, script, hint, code, message = self.visit(expression)
            expression_list.append(result)

        if len(expression_list) >= 1:
            parsedObject.update({'optionName': expression_list[0]})
        if len(expression_list) >= 2:
            parsedObject.update({'optionValue': expression_list[1]})
        if len(expression_list) >= 3:
            for i in range(2, len(expression_list)):
                parsedObject.update({("optionValue" + str(i)): expression_list[i]})

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

    def visitLoadmap(self, ctx:APIParser.LoadmapContext):
        
        parsedObject = {'name': 'LOADMAP' , 'rule': ctx.getRuleIndex() }
    
        expression_list = []
        for expression in ctx.expression():
            result, script, hint, code, message =  self.visit(expression)
            expression_list.append(result)
        
        parsedObject.update({'expression' : expression_list})
        
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

    def visitWheneverError(self, ctx:APIParser.WheneverErrorContext):
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

    def visitSpool(self, ctx: APIParser.SpoolContext):
        content = ctx.String().getText()
        
        parsedObject = {'name': 'SPOOL', 'param': content}
    
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        # 源文件
        originScript = self.getSource(tokens)
        # 提示信息
        hint = self.getHint(tokens)
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message
            self.isFinished = False

        self.parsedObject.append(parsedObject)
        self.originScripts.append(originScript)
        self.hints.append(hint)
        self.errorCode.append(errorCode)
        self.errorMsg.append(errorMsg)

        return parsedObject, originScript, hint, errorCode, errorMsg

    # Visit a parse tree produced by APIParser#internal.
    def visitInternal(self, ctx:APIParser.InternalContext):
        
        parsedObject = {'name': 'INTERNAL' , 'rule': ctx.getRuleIndex() }

        expression_list = []
        for expression in ctx.expression():
            result, script, hint, code, message =  self.visit(expression)
            expression_list.append(result)
        
        parsedObject.update({'expression' : expression_list})

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
    #
    def visitScript(self, ctx:APIParser.ScriptContext):
        errorCode = 0
        errorMsg = None
        
        # 脚本结束可能是%}，也可能是文件结束符
        origin = ctx.ScriptBlock().getText().rpartition('%}')
        if origin[1] == '%}':
            # 正常结束
            block = origin[0]
        else:
            # 无%}
            block = origin[2]
            errorCode = -1
            self.isFinished = False
        
        parsedObject = {'name': ctx.SCRIPT_OPEN().getText(), 'rule': ctx.getRuleIndex(), 'block': block}
    
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        # 源文件
        originScript = self.getSource(tokens)
        # 提示信息
        hint = self.getHint(tokens)
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message
            self.isFinished = False

        self.parsedObject.append(parsedObject)
        self.originScripts.append(originScript)
        self.hints.append(hint)
        self.errorCode.append(errorCode)
        self.errorMsg.append(errorMsg)

        return  parsedObject, originScript, hint, errorCode, errorMsg


    """
        Http消息节点
    """
    def visitHttp(self, ctx: APIParser.HttpContext):
        parsedObject = {'name': 'HTTP'}
        
        # HTTP_OPEN的格式是 ### STRING的格式
        # 分割STRING作为title属性返回
        title = ctx.HTTP_OPEN().getText().partition(' ')[2]
        
        if (title is not None) and title != '':
            title = title.splitlines()[0].strip()

        if (title is not None) and (title != ''):
            parsedObject.update({ 'title': title })
        
        #  HTTP消息的处理
        result, script, hint, code, message =  self.visit(ctx.httpMessage())
        parsedObject.update(result)

        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        # 源文件
        originScript = self.getSource(tokens)
        # 提示信息
        hint = self.getHint(tokens)
        errorCode = 0
        errorMsg = None

        # 异常结束
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message
            self.isFinished = False
        
        # 是否是###结束分界符结束
        if ctx.HTTP_CLOSE() is None:
            errorCode = -1
            self.isFinished = False

        self.parsedObject = parsedObject
        self.originScripts = originScript
        self.hints = hint
        self.errorCode = errorCode
        self.errorMsg = errorMsg

        return parsedObject, originScript, hint, errorCode, errorMsg

    """
        处理HTTP消息规范部分
    """
    def visitHttpMessage(self, ctx:APIParser.HttpMessageContext):
        
        parsedObject = {}
        
        # 处理请求行
        result, script, hint, code, message =  self.visit(ctx.httpRequestLine())
        parsedObject.update(result)
        
        # 处理请求域
        if(ctx.httpHeaderFields() is not None):
            result, script, hint, code, message =  self.visit(ctx.httpHeaderFields())
            parsedObject.update(result)
        
        # 请求消息体
        if(ctx.httpMessageBody() is not None):
            result, script, hint, code, message =  self.visit(ctx.httpMessageBody())
            parsedObject.update(result)
        
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
        
        return  parsedObject, originScript, hint, errorCode, errorMsg
        

    """
        处理请求行
    """
    def visitHttpRequestLine(self, ctx:APIParser.HttpRequestLineContext):
        parsedObject = {}
        
        # 请求方法
        result, script, hint, code, message =  self.visit(ctx.httpMethod())
        parsedObject.update(result)
        
        # 请求目标
        result, script, hint, code, message =  self.visit(ctx.httpRequestTarget())
        parsedObject.update(result)
        
        # 请求目标中有http版本信息
        # 分离Http版本号和Http请求目标地址
        if result['httpRequestTarget'] is not None:
            data = result['httpRequestTarget'].split('HTTP/',1)
            if(len(data)>1):
                parsedObject.update({'httpRequestTarget': data[0].strip(), 'httpVersion': 'HTTP/'+data[1]})
        
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
        
        return  parsedObject, originScript, hint, errorCode, errorMsg


    """
        处理请求方法
    """
    def visitHttpMethod(self, ctx:APIParser.HttpMethodContext):
        
        parsedObject = {}

        # 直接复制请求方法
        if(ctx.HttpMethod() is not None):
            parsedObject.update({'httpMethod':ctx.HttpMethod().getText()})
        
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

        return  parsedObject, originScript, hint, errorCode, errorMsg


    """
        处理请求目标
    """
    def visitHttpRequestTarget(self, ctx:APIParser.HttpRequestTargetContext):

        parsedObject = { 'httpRequestTarget':None}
        if (ctx.HttpRequestTarget() is not None):
            parsedObject.update({'httpRequestTarget':ctx.HttpRequestTarget().getText()})
        
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

        return  parsedObject, originScript, hint, errorCode, errorMsg


    """
        处理请求域
    """
    def visitHttpHeaderFields(self, ctx:APIParser.HttpHeaderFieldsContext):
        parsedObject = {}
        
        # 多个请求域定义
        for field in ctx.httpHeaderField():
            result, script, hint, code, message = self.visit(field)
            parsedObject.update(result)

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
    
        return  parsedObject, originScript, hint, errorCode, errorMsg


    """
        处理请求域定义
    """
    def visitHttpHeaderField(self, ctx:APIParser.HttpHeaderFieldContext):
        parsedObject = {}
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
        
        # 请求域定义名称
        result, script, hint, code, message = self.visit(ctx.httpFieldName())
        key = result['value']
        # 请求域定义值
        result, script, hint, code, message = self.visit(ctx.httpFieldValue())
        value = result['value']
        
        # 合并生成新的KV值
        parsedObject.update({key: value})

        return  parsedObject, originScript, hint, errorCode, errorMsg


    """
        处理请求域定义名称部分
    """
    def visitHttpFieldName(self, ctx:APIParser.HttpFieldNameContext):
        parsedObject = { 'value': ctx.HttpFieldName().getText() }
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
        
        return  parsedObject, originScript, hint, errorCode, errorMsg



    """
        处理请求域定义值部分
    """
    def visitHttpFieldValue(self, ctx:APIParser.HttpFieldValueContext):
        
        parsedObject = {'value': ctx.HttpFieldValue().getText()}
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
        
        return  parsedObject, originScript, hint, errorCode, errorMsg


    """
        处理消息体
    """
    def visitHttpMessageBody(self, ctx:APIParser.HttpMessageBodyContext):
        
        parsedObject = {}
        # 普通消息体内容可能有多个部分，只保留了最后一个部分
        # 合规的消息体不会产生这种情况
        for content in ctx.httpMessageBodyContent():
            result, script, hint, code, message = self.visit(content)
            parsedObject.update(result)
        
        # 处理multipart boundary
        for boundary in ctx.httpMultipart(): 
            result, script, hint, code, message = self.visit(boundary)
            parsedObject.update(result)
        
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
        
        return  parsedObject, originScript, hint, errorCode, errorMsg


    """
        处理multipart
    """
    def visitHttpMultipart(self, ctx:APIParser.HttpMultipartContext):

        parsedObject = {}
        
        # 多个boundary 
        multipart = []
        for boundary in ctx.httpMultipartBoundary():
            result, script, hint, code, message = self.visit(boundary)
            multipart.append(result)
        
        if len(multipart) > 0:
            parsedObject.update({'multipart': multipart})
        
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
        
        return  parsedObject, originScript, hint, errorCode, errorMsg

    """
        处理multipart boundary部分
    """
    def visitHttpMultipartBoundary(self, ctx:APIParser.HttpMultipartBoundaryContext):
        parsedObject = {}
        
        # 处理boundary的请求域部分
        if ctx.httpHeaderFields() is not None:
            result, script, hint, code, message = self.visit(ctx.httpHeaderFields())
            parsedObject.update(result)

        # 处理boundary的内容部分
        if ctx.httpMessageBodyContent() is not None:
            result, script, hint, code, message = self.visit(ctx.httpMessageBodyContent())
            parsedObject.update(result)

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
            
        return  parsedObject, originScript, hint, errorCode, errorMsg

    """
        处理消息体的内容部分
    """
    def visitHttpMessageBodyContent(self, ctx:APIParser.HttpMessageBodyContentContext):
        
        # 内容操作部分
        operates = []
        for operate in ctx.httpMessageBodyOperate(): 
            result, script, hint, code, message = self.visit(operate)
            operates.append(result)
        
        # 内容部分
        # 可以直接取内容的文字
        contents = []
        for content in ctx.httpMessageBodyOther():
            result, script, hint, code, message = self.visit(content)
            contents.append(result)
        
        parsedObject = {'operate': operates, 'content': contents}
        
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

        return  parsedObject, originScript, hint, errorCode, errorMsg


    """
        处理内容操作部分
        操作符号包含在词中，需要把操作符号和内容分离开来
        *** 操作符也可以在词法定义中定义
    """
    def visitHttpMessageBodyOperate(self, ctx:APIParser.HttpMessageBodyOperateContext):
        parsedObject = {}
        
        data = ctx.HttpMessageBodyOperate().getText()
        
        if(data.find('>>!') == 0) :
            parsedObject.update({'operator': '>>!'})
            parsedObject.update({'content': data.partition('>>!')[2]})
        elif (data.find('>!') == 0) :
            parsedObject.update({'operator': '>!'})
            parsedObject.update({'content': data.partition('>!')[2]})
        elif (data.find('>') == 0) :
            parsedObject.update({'operator': '>'})
            parsedObject.update({'content': data.partition('>')[2]})
        elif (data.find('<') == 0) :
            parsedObject.update({'operator': '<'})
            parsedObject.update({'content': data.partition('<')[2]})
        
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

        return  parsedObject, originScript, hint, errorCode, errorMsg

    """
        操作内容部分
    """
    def visitHttpMessageBodyOther(self, ctx:APIParser.HttpMessageBodyOtherContext):
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

        return  originScript, originScript, hint, errorCode, errorMsg
