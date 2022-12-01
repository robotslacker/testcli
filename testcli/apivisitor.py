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
        return ctx.getSourceInterval()

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
        return self.isFinished, self.parsedObject, self.errorCode, self.errorMsg
    
    def visitCommand(self, ctx: APIParser.CommandContext):
        return self.visitChildren(ctx)

    def visitExit(self, ctx: APIParser.ExitContext):
        parsedObject = {'name': 'EXIT'}

        if ctx.INT() is not None:
            parsedObject.update({'exitValue': int(ctx.INT().getText())})
        else:
            parsedObject.update({'exitValue': 0})

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        self.parsedObject = parsedObject
        self.errorCode = errorCode
        self.errorMsg = errorMsg

    def visitQuit(self, ctx: APIParser.QuitContext):
        parsedObject = {'name': 'QUIT'}

        if ctx.INT() is not None:
            parsedObject.update({'exitValue': int(ctx.INT().getText())})
        else:
            parsedObject.update({'exitValue': 0})

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        self.parsedObject = parsedObject
        self.errorCode = errorCode
        self.errorMsg = errorMsg

    def visitUse(self, ctx: APIParser.UseContext):
        parsedObject = {'name': 'USE'}
        nameSpace = None
        if ctx.USE_API() is not None:
            nameSpace = 'API'
        elif ctx.USE_SQL() is not None:
            nameSpace = 'SQL'
        parsedObject.update({'nameSpace': nameSpace})

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        self.parsedObject = parsedObject
        self.errorCode = errorCode
        self.errorMsg = errorMsg

    def visitSleep(self, ctx: APIParser.SleepContext):
        parsedObject = {
            'name': 'SLEEP',
            "sleepTime": int(ctx.INT().getText())
        }

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        self.parsedObject = parsedObject
        self.errorCode = errorCode
        self.errorMsg = errorMsg

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

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        self.parsedObject = parsedObject
        self.errorCode = errorCode
        self.errorMsg = errorMsg

    def visitStart(self, ctx: APIParser.StartContext):
        parsedObject = {'name': 'START'}
        if ctx.START_INT() is not None:
            parsedObject.update({'loopTimes': int(ctx.START_INT().getText())})
        else:
            parsedObject.update({'loopTimes': 1})

        expression_list = []
        if ctx.START_EXPRESSION() is not None:
            for expression in ctx.START_EXPRESSION():
                expression_list.append(str(expression.getText()))
        parsedObject.update({'scriptList': expression_list})

        # 处理错误信息
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = 1
            errorMsg = ctx.exception.message
            self.isFinished = False

        self.parsedObject = parsedObject
        self.errorCode = errorCode
        self.errorMsg = errorMsg

    def visitSet(self, ctx: APIParser.SetContext):
        parsedObject = {'name': 'SET'}

        expression_list = []
        for expression in ctx.SET_EXPRESSION():
            expression_list.append(str(expression.getText()))

        if ctx.SET_AT():
            parsedObject.update({'scope': "global"})
        else:
            parsedObject.update({'scope': "local"})
        if len(expression_list) >= 1:
            parsedObject.update({'optionName': expression_list[0]})
        if len(expression_list) >= 2:
            optionValue = " ".join(expression_list[1:])
            parsedObject.update({"optionValue": optionValue})

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        self.parsedObject = parsedObject
        self.errorCode = errorCode
        self.errorMsg = errorMsg

    def visitWhenever(self, ctx: APIParser.WheneverContext):
        parsedObject = {'name': 'WHENEVER'}

        if ctx.WHENEVER_CONTINUE():
            parsedObject.update({"action": 'continue'})
        if ctx.WHENEVER_EXIT():
            parsedObject.update({"action": 'exit'})
        if ctx.WHENEVER_ERROR():
            parsedObject.update({"condition": 'error'})

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        self.parsedObject = parsedObject
        self.errorCode = errorCode
        self.errorMsg = errorMsg

    def visitIf(self, ctx: APIParser.IfContext):
        parsedObject = {'name': 'IF'}

        if ctx.IF_EXPRESSION() is not None:
            expression = str(ctx.IF_EXPRESSION().getText()).strip()
            if expression.startswith('{%'):
                expression = expression[2:]
            if expression.endswith('%}'):
                expression = expression[:-2]
            expression = expression.strip()
            parsedObject.update({'expression': expression})
        else:
            parsedObject.update({'expression': ""})

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        self.parsedObject = parsedObject
        self.errorCode = errorCode
        self.errorMsg = errorMsg

    def visitEndif(self, ctx: APIParser.EndifContext):
        parsedObject = {'name': 'ENDIF'}

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        self.parsedObject = parsedObject
        self.errorCode = errorCode
        self.errorMsg = errorMsg

    def visitSpool(self, ctx: APIParser.SpoolContext):
        content = ctx.String().getText()

        parsedObject = {'name': 'SPOOL', 'file': content}

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        self.parsedObject = parsedObject
        self.errorCode = errorCode
        self.errorMsg = errorMsg

    def visitScript(self, ctx: APIParser.ScriptContext):
        parsedObject = {'name': 'SCRIPT'}

        # 删除BLOCK 末尾的 %}
        if ctx.ScriptBlock() is not None:
            block = ctx.ScriptBlock().getText()
            if str(block).endswith('%}'):
                block = str(block[:-2])
                if str(block).endswith('{%'):
                    block = str(block[2:])
                block = block.strip()
                parsedObject.update({'block': block})
            else:
                self.isFinished = False
        else:
            self.isFinished = False

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        self.parsedObject = parsedObject
        self.errorCode = errorCode
        self.errorMsg = errorMsg

    def visitAssert(self, ctx: APIParser.AssertContext):
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

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        self.parsedObject = parsedObject
        self.errorCode = errorCode
        self.errorMsg = errorMsg

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
            parsedObject.update({'title': title})

        # 获取源文件
        hints = []
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        for token in tokens:
            if token.channel == APILexer.COMMENT_CHANNEL:
                commentLine = str(token.text).strip()
                matchObj = re.match(r"//\s+@(.*)$", commentLine, re.DOTALL)
                if matchObj:
                    hints.append(matchObj.group(1))
        parsedObject.update({'hints': hints})

        #  HTTP消息的处理
        if ctx.httpMessage() is not None:
            result, code, message = self.visit(ctx.httpMessage())
            parsedObject.update(result)

        # 处理错误信息
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message
            self.isFinished = False
        
        # 是否是###结束分界符结束
        if ctx.HTTP_CLOSE() is None:
            errorCode = -1
            self.isFinished = False

        self.parsedObject = parsedObject
        self.errorCode = errorCode
        self.errorMsg = errorMsg

        return parsedObject, errorCode, errorMsg

    """
        处理HTTP消息规范部分
    """
    def visitHttpMessage(self, ctx: APIParser.HttpMessageContext):
        parsedObject = {}
        
        # 处理请求行
        result, code, message = self.visit(ctx.httpRequestLine())
        parsedObject.update(result)

        # 处理请求域
        if ctx.httpHeaderFields() is not None:
            result, code, message = self.visit(ctx.httpHeaderFields())
            parsedObject.update(result)
        
        # 请求消息体
        if ctx.httpMessageBody() is not None:
            result, code, message = self.visit(ctx.httpMessageBody())
            parsedObject.update(result)

        # 处理错误信息
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message
        
        return parsedObject, errorCode, errorMsg

    """
        处理请求行
    """
    def visitHttpRequestLine(self, ctx: APIParser.HttpRequestLineContext):
        parsedObject = {}
        
        # 请求方法
        result, code, message = self.visit(ctx.httpMethod())
        parsedObject.update(result)
        
        # 请求目标
        result, code, message = self.visit(ctx.httpRequestTarget())
        parsedObject.update(result)

        fields = {}
        httpVersion = ""

        # 请求目标中有http版本信息
        # 分离Http版本号和Http请求目标地址
        if result['httpRequestTarget'] is not None:
            data = result['httpRequestTarget'].split('HTTP/', 1)
            if len(data) > 1:
                httpRequestTarget = str(data[0].strip())
                httpVersion = ('HTTP/'+data[1]).strip()
                data = httpRequestTarget.split("?")
                if len(data) > 1:
                    httpRequestURL = data[0].strip().replace("\n", "").replace(" ", "").replace("\t", "")
                    httpFieldstr = data[1].strip().replace("\n", "").replace(" ", "").replace("\t", "")
                    httpFields = httpFieldstr.split("&")
                    for httpField in httpFields:
                        httpFieldName, httpFieldValue = httpField.split('=')
                        fields[httpFieldName] = httpFieldValue
                else:
                    httpRequestURL = httpRequestTarget.strip().replace("\n", "").replace(" ", "").replace("\t", "")
            else:
                httpRequestTarget = result['httpRequestTarget']
                httpRequestURL = httpRequestTarget.strip().replace("\n", "").replace(" ", "").replace("\t", "")
            parsedObject.update(
                {
                    'httpRequestTarget': httpRequestURL,
                    'httpFields': fields,
                    'httpVersion': httpVersion
                })
        
        # 错误信息处理
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message
        
        return parsedObject, errorCode, errorMsg

    """
        处理请求方法
    """
    def visitHttpMethod(self, ctx: APIParser.HttpMethodContext):
        parsedObject = {}

        # 直接复制请求方法
        if ctx.HttpMethod() is not None:
            parsedObject.update({'httpMethod': ctx.HttpMethod().getText()})

        # 处理错误信息
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        return parsedObject, errorCode, errorMsg

    """
        处理请求目标
    """
    def visitHttpRequestTarget(self, ctx: APIParser.HttpRequestTargetContext):
        parsedObject = {'httpRequestTarget': None}
        if ctx.HttpRequestTarget() is not None:
            parsedObject.update({'httpRequestTarget': ctx.HttpRequestTarget().getText()})
        
        # 处理错误信息
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        return parsedObject, errorCode, errorMsg

    """
        处理请求域
    """
    def visitHttpHeaderFields(self, ctx: APIParser.HttpHeaderFieldsContext):
        parsedObject = {}

        headers = {}
        # 多个请求域定义
        for field in ctx.httpHeaderField():
            result, code, message = self.visit(field)
            for headerName, headerValue in result.items():
                headers[headerName] = headerValue
        parsedObject.update({"headers": headers})

        # 错误处理
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message
    
        return parsedObject, errorCode, errorMsg

    """
        处理请求域定义
    """
    def visitHttpHeaderField(self, ctx: APIParser.HttpHeaderFieldContext):
        parsedObject = {}

        # 处理错误信息
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message
        
        # 请求域定义名称
        result, code, message = self.visit(ctx.httpHeaderFieldName())
        key = result['value']
        # 请求域定义值
        result, code, message = self.visit(ctx.httpHeaderFieldValue())
        value = result['value']
        
        # 合并生成新的KV值
        parsedObject.update({key: value})

        return parsedObject, errorCode, errorMsg

    """
        处理请求域定义名称部分
    """
    def visitHttpHeaderFieldName(self, ctx: APIParser.HttpHeaderFieldNameContext):
        parsedObject = {'value': ctx.HttpHeaderFieldName().getText()}

        # 处理错误信息
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message
        
        return parsedObject, errorCode, errorMsg

    """
        处理请求域定义值部分
    """
    def visitHttpHeaderFieldValue(self, ctx: APIParser.HttpHeaderFieldValueContext):
        parsedObject = {'value': ctx.HttpHeaderFieldValue().getText()}

        # 处理错误信息
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message
        
        return parsedObject, errorCode, errorMsg

    """
        处理消息体
    """
    def visitHttpMessageBody(self, ctx: APIParser.HttpMessageBodyContext):
        parsedObject = {}
        # 普通消息体内容可能有多个部分，只保留了最后一个部分
        # 合规的消息体不会产生这种情况
        for content in ctx.httpMessageBodyContent():
            result, code, message = self.visit(content)
            parsedObject.update(result)
        
        # 处理multipart boundary
        for boundary in ctx.httpMultipart(): 
            result, code, message = self.visit(boundary)
            parsedObject.update(result)
        
        # 处理错误信息
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message
        
        return parsedObject, errorCode, errorMsg

    """
        处理multipart
    """
    def visitHttpMultipart(self, ctx: APIParser.HttpMultipartContext):
        parsedObject = {}
        
        # 多个boundary 
        multipart = []
        for boundary in ctx.httpMultipartBoundary():
            result, code, message = self.visit(boundary)
            multipart.append(result)
        
        if len(multipart) > 0:
            parsedObject.update({'multipart': multipart})

        # 处理错误信息
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message
        
        return parsedObject, errorCode, errorMsg

    """
        处理multipart boundary部分
    """
    def visitHttpMultipartBoundary(self, ctx: APIParser.HttpMultipartBoundaryContext):
        parsedObject = {}
        
        # 处理boundary的请求域部分
        if ctx.httpHeaderFields() is not None:
            result, code, message = self.visit(ctx.httpHeaderFields())
            parsedObject.update(result)

        # 处理boundary的内容部分
        if ctx.httpMessageBodyContent() is not None:
            result, code, message = self.visit(ctx.httpMessageBodyContent())
            parsedObject.update(result)

        # 处理错误信息
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message
            
        return parsedObject, errorCode, errorMsg

    """
        处理消息体的内容部分
    """
    def visitHttpMessageBodyContent(self, ctx: APIParser.HttpMessageBodyContentContext):
        # 内容操作部分
        operates = []
        for operate in ctx.httpMessageBodyOperate(): 
            result, code, message = self.visit(operate)
            operates.append(result)
        
        # 内容部分
        # 可以直接取内容的文字
        contents = []
        for content in ctx.httpMessageBodyOther():
            result, code, message = self.visit(content)
            contents.append(result)
        
        parsedObject = {'operate': operates, 'contents': contents}

        # 处理错误信息
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        return parsedObject, errorCode, errorMsg

    """
        处理内容操作部分
        操作符号包含在词中，需要把操作符号和内容分离开来
        *** 操作符也可以在词法定义中定义
    """
    def visitHttpMessageBodyOperate(self, ctx: APIParser.HttpMessageBodyOperateContext):
        parsedObject = {}
        
        data = ctx.HttpMessageBodyOperate().getText()
        
        if data.find('>>!') == 0:
            parsedObject.update({'operator': '>>!'})
            parsedObject.update({'content': data.partition('>>!')[2]})
        elif data.find('>!') == 0:
            parsedObject.update({'operator': '>!'})
            parsedObject.update({'content': data.partition('>!')[2]})
        elif data.find('>') == 0:
            parsedObject.update({'operator': '>'})
            parsedObject.update({'content': data.partition('>')[2]})
        elif data.find('<') == 0:
            parsedObject.update({'operator': '<'})
            parsedObject.update({'content': data.partition('<')[2]})
        
        # 处理错误信息
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        return parsedObject, errorCode, errorMsg

    """
        操作内容部分
    """
    def visitHttpMessageBodyOther(self, ctx: APIParser.HttpMessageBodyOtherContext):
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        # 源文件
        originScript = self.getSource(tokens)

        # 处理错误信息
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        return originScript, errorCode, errorMsg
