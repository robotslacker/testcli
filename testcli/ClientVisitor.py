from antlr4.Token import Token
import re

if __name__ is not None and "." in __name__:
    from .antlrgen.ClientParser import ClientParser
    from .antlrgen.ClientParserVisitor import ClientParserVisitor
    from .antlrgen.ClientLexer import ClientLexer
else:
    from antlrgen.ClientParser import ClientParser
    from antlrgen.ClientParserVisitor import ClientParserVisitor
    from antlrgen.ClientLexer import ClientLexer


class ClientVisitor(ClientParserVisitor):

    def __init__(self, tokens, defaultNameSpace = None):
        # 词法符号表
        self.tokens = tokens
        # 解析空间 API/MYSQL，先转换成大写
        self.defaultNameSpace = None if defaultNameSpace is None else defaultNameSpace.upper()
        # 解析是否正常完成
        self.isFinished = True
        # 返回去掉了注释信息的解析结果
        self.parsedObject = []
        # 包含了所有注释信息的原语句（格式保持不变，包括空行，换行符号等)
        self.originScripts = []
        # 有意义的注释信息(即用-- [Hint] 开头的SQL语句, 或者用# [Hint]|// [Hint] 开头的API语句), 一个语句有多个注释信息的，用数组返回
        self.hints = []
        # 如果成功，返回0； 如果失败，返回-1； 
        self.errorCode = []
        # 如果成功，返回空；如果失败，返回解析的错误提示信息
        self.errorMsg = []
    
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
            if token.channel != ClientLexer.HINT_CHANNEL:
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
    def getSource(self, tokens):
        
        # 返回单一通道的信息
        return ''.join(token.text for token in tokens)

    
    """
        功能：返回提示文本
        参数：
            tokens 分词数组
        返回：
            指定分词数组中提示分词文本
    """
    def getHint(self, tokens):
        hints = []
        for token in tokens:
            if token.channel == ClientLexer.HINT_CHANNEL:
                # 使用提示[Hint]分割字符串 
                # FIXME [Hint] 大小写区分
                pattern = '\[ *Hint *\]'
                hint_arr = re.split(pattern, token.text, flags=re.IGNORECASE)
                if(len(hint_arr)>1):
                    hint = hint_arr[1]
                else:
                    hint = None
                if hint is not None:
                    # 删除后面的换行符号
                    tmp = hint.splitlines()
                    if(len(tmp)>0):
                        hint = tmp[0].strip()
                    else:
                        hint=''
                if (hint is not None) and (hint!= ''):
                    hints.append(hint)
        
        if (len(hints) == 0):
            return None
        if (len(hints) == 1):
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
    def visitProg(self, ctx:ClientParser.ProgContext):
        self.visitChildren(ctx)
        return self.isFinished, self.parsedObject, self.originScripts, self.hints, self.errorCode, self.errorMsg
    
    # 处理所有的命令
    def visitCommands(self, ctx:ClientParser.CommandsContext):
        return self.visitChildren(ctx)


    # 保存命令结果
    def visitCommand(self, ctx:ClientParser.CommandContext):
        return self.visitChildren(ctx)
        
    # 退出命令
    def visitExit(self, ctx:ClientParser.ExitContext):
        parsedObject = {'name': 'EXIT', 'rule': ctx.getRuleIndex()}
        
        if (ctx.INT() is not None):
            parsedObject.update({'param': ctx.INT().getText()})

        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        # 源文件
        originScript = self.getSource(tokens)
        # 提示信息
        hint = self.getHint(tokens)
        errorCode = 0
        errorMsg = None

        self.parsedObject.append(parsedObject)
        self.originScripts.append(originScript)
        self.hints.append(hint)
        self.errorCode.append(errorCode)
        self.errorMsg.append(errorMsg)

        return  parsedObject, originScript, hint, errorCode, errorMsg

    # 
    def visitQuit(self, ctx:ClientParser.QuitContext):

        parsedObject = {'name': 'QUIT', 'rule': ctx.getRuleIndex()}
        
        if (ctx.INT() is not None):
            parsedObject.update({'param': ctx.INT().getText()})

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
    def visitUse(self, ctx:ClientParser.UseContext):
        errorCode = 0
        errorMsg = None
        
        parsedObject = {'name': 'USE', 'rule': ctx.getRuleIndex() }
    
        param = None
        if ctx.API() is not None:
            param = 'API'
        elif ctx.SQL() is not None:
            param = 'SQL'
        
        if (param is not None):
            parsedObject.update({'param': param })
        else:
            errorCode = -1
            self.isFinished = False
        
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        # 源文件
        originScript = self.getSource(tokens)
        # 提示信息
        hint = self.getHint(tokens)
            
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
    def visitSleep(self, ctx:ClientParser.SleepContext):

        parsedObject = {'name': 'SLEEP', 'rule': ctx.getRuleIndex() }
    
        errorCode = 0
        errorMsg = None
        
        param = None
        if(ctx.INT() is not None):
            param = ctx.INT().getText()
        if(ctx.DECIMAL() is not None):
            param = ctx.DECIMAL().getText()

        if(param is None):
            errorCode = -1
            self.isFinished = False
        else:
            parsedObject.update({'param': param})

        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        # 源文件
        originScript = self.getSource(tokens)
        # 提示信息
        hint = self.getHint(tokens)
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

    # 会话连接
    # 可能是SQL连接，也可能是API连接
    def visitConnect(self, ctx: ClientParser.ConnectContext):
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

        self.originScripts.append(originScript)
        self.parsedObject.append(parsedObject)
        self.hints.append(hint)
        self.errorCode.append(errorCode)
        self.errorMsg.append(errorMsg)

        return parsedObject, originScript, hint, errorCode, errorMsg

    def visitConnectjdbc(self, ctx: ClientParser.ConnectjdbcContext):
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

    def visitConnectlocal(self, ctx: ClientParser.ConnectlocalContext):
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

    def visitConnectlocalService(self, ctx: ClientParser.ConnectlocalServiceContext):
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

    def visitConnectService(self, ctx: ClientParser.ConnectServiceContext):
        parsedObject = {}
        if ctx.CONNECT_STRING() is not None:
            parsedObject.update({'service': ctx.CONNECT_STRING().getText()})

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
    def visitConnectUserInfo(self, ctx: ClientParser.ConnectUserInfoContext):
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

    # Visit a parse tree produced by ClientParser#connectUser.
    def visitConnectUser(self, ctx:ClientParser.ConnectUserContext):
        parsedObject = {}
        if ctx.CONNECT_STRING() is not None:
            parsedObject.update({'username': ctx.CONNECT_STRING().getText()})
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]

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

    # Visit a parse tree produced by ClientParser#connectPassword.
    def visitConnectPassword(self, ctx:ClientParser.ConnectPasswordContext):
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

    def visitConnectDriver(self, ctx: ClientParser.ConnectDriverContext):
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

    def visitConnectDriverSchema(self, ctx: ClientParser.ConnectDriverSchemaContext):
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

    def visitConnectDriverType(self, ctx: ClientParser.ConnectDriverSchemaContext):
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

    def visitConnectHost(self, ctx: ClientParser.ConnectHostContext):
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

    def visitConnectPort(self, ctx: ClientParser.ConnectPortContext):
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

    def visitConnectParameters(self, ctx: ClientParser.ConnectParametersContext):
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

    def visitConnectParameter(self, ctx: ClientParser.ConnectParameterContext):
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

    def visitConnectParameterName(self, ctx: ClientParser.ConnectParameterNameContext):
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

    def visitConnectParameterValue(self, ctx: ClientParser.ConnectParameterValueContext):
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

    #
    def visitDisconnect(self, ctx:ClientParser.DisconnectContext):
        
        parsedObject = {'name': 'DISCONNECT', 'rule': ctx.getRuleIndex() }
    
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

    def visitSession(self, ctx:ClientParser.SessionContext):

        if ctx.SAVE() is not None:
            type = 'SAVE'
        elif ctx.RELEASE() is not None:
            type = 'RELEASE'
        elif ctx.RESTORE() is not None:
            type = 'RESTORE'
        elif ctx.SAVECONFIG() is not None:
            type = 'SAVECONFIG'
        elif ctx.SHOW() is not None: 
            type = 'SHOW'

        parsedObject = {'name':  'SESSION '+ type , 'rule': ctx.getRuleIndex() }
        if ctx.String() is not None:
            parsedObject.update({'param' : ctx.String().getText()});
            
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

    # 执行脚本命令
    def visitStart(self, ctx: ClientParser.StartContext):
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

        return  parsedObject, originScript, hint, errorCode, errorMsg

    def visitLoadmap(self, ctx:ClientParser.LoadmapContext):
        
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

    # 
    def visitWheneverError(self, ctx:ClientParser.WheneverErrorContext):
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


    # 
    def visitSpool(self, ctx:ClientParser.SpoolContext):
        
        content = ctx.String().getText()
        
        parsedObject = {'name': 'SPOOL' , 'rule': ctx.getRuleIndex(), 'param': content }
    
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
    def visitEcho(self, ctx:ClientParser.EchoContext):
        
        errorCode = 0
        errorMsg = None

        parsedObject = {'name': 'ECHO' , 'rule': ctx.getRuleIndex() }    
        
        # 删除BLOCK 末尾的 ECHO OFF
        block = ctx.EchoBlock().getText()
        pattern = '\n *echo\s+off'
        blocks = re.split(pattern, block, flags=re.IGNORECASE)
        if(len(blocks)>1):
            parsedObject.update({'block': blocks[0]})
        else:
            errorCode = -1
            self.isFinished = False
            
        # param
        param = ctx.ECHO_OPEN().getText().partition(' ')[2]
        if param is not None:
            param = param.splitlines()[0] 
            parsedObject.update({'param': param})

        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        # 源文件
        originScript = self.getSource(tokens)
        # 提示信息
        hint = self.getHint(tokens)
        
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


    def visitLoadDriver(self, ctx:ClientParser.LoadmapContext):
        
        parsedObject = {'name': 'LOADDRIVER' , 'rule': ctx.getRuleIndex() }
    
        expression_list = []
        for expression in ctx.expression():
            result, script, hint, code, message =  self.visit(expression)
            expression_list.append(result)
        if(len(expression_list)>0):
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

    def visitSingleExpression(self, ctx: ClientParser.SingleExpressionContext):
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

    def visitExpression(self, ctx: ClientParser.ExpressionContext):
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


    # Visit a parse tree produced by ClientParser#internal.
    def visitInternal(self, ctx:ClientParser.InternalContext):
        
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

    def visitSet(self, ctx: ClientParser.SetContext):
        parsedObject = {'name': 'SET'}
    
        expression_list = []
        for expression in ctx.singleExpression():
            result, script, hint, code, message = self.visit(expression)
            expression_list.append(result)

        print("expresslist = " + str(expression_list))
        if len(expression_list) >= 1:
            parsedObject.update({'optionName': expression_list[0]})
        if len(expression_list) >= 2:
            parsedObject.update({'optionValue': expression_list[1]})
        if len(expression_list) >= 3:
            for i in range(2, len(expression_list)):
                parsedObject.update({("optionValue" + str(iter)): expression_list[i]})

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

        self.parsedObject.append(parsedObject)
        self.originScripts.append(originScript)
        self.hints.append(hint)
        self.errorCode.append(errorCode)
        self.errorMsg.append(errorMsg)

        return parsedObject, originScript, hint, errorCode, errorMsg

    #
    def visitScript(self, ctx:ClientParser.ScriptContext):
        errorCode = 0
        errorMsg = None
        
        # 脚本结束可能是%}，也可能是文件结束符
        origin = ctx.ScriptBlock().getText().rpartition('%}')
        block = None
        if(origin[1] == '%}'):
            # 正常结束
            block = origin[0]
        else:
            # 无%}
            block = origin[2]
            errorCode = -1
            self.isFinished = False
        
        parsedObject = {'name': ctx.SCRIPT_OPEN().getText() , 'rule': ctx.getRuleIndex(), 'block': block }
    
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        # 源文件
        originScript = self.getSource(tokens)
        # 提示信息
        hint = self.getHint(tokens)
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


    """
        Http消息节点
    """
    def visitHttp(self, ctx:ClientParser.HttpContext):
        
        # 如果名字空间是 SQL HTTP语句就不解析
        if self.defaultNameSpace == 'MYSQL':
            return None

        parsedObject = {'name': 'HTTP', 'rule': ctx.getRuleIndex() }
        
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
        if (ctx.exception is not None):
            errorCode = -1
            errorMsg = ctx.exception.message
            self.isFinished = False
        
        # 是否是###结束分界符结束
        if (ctx.HTTP_CLOSE() is None):
            errorCode = -1
            self.isFinished = False


        self.parsedObject.append(parsedObject)
        self.originScripts.append(originScript)
        self.hints.append(hint)
        self.errorCode.append(errorCode)
        self.errorMsg.append(errorMsg)

        return  parsedObject, originScript, hint, errorCode, errorMsg

    """
        处理HTTP消息规范部分
    """
    def visitHttpMessage(self, ctx:ClientParser.HttpMessageContext):
        
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
    def visitHttpRequestLine(self, ctx:ClientParser.HttpRequestLineContext):
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
    def visitHttpMethod(self, ctx:ClientParser.HttpMethodContext):
        
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
    def visitHttpRequestTarget(self, ctx:ClientParser.HttpRequestTargetContext):

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
    def visitHttpHeaderFields(self, ctx:ClientParser.HttpHeaderFieldsContext):
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
    def visitHttpHeaderField(self, ctx:ClientParser.HttpHeaderFieldContext):
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
    def visitHttpFieldName(self, ctx:ClientParser.HttpFieldNameContext):
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
    def visitHttpFieldValue(self, ctx:ClientParser.HttpFieldValueContext):
        
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
    def visitHttpMessageBody(self, ctx:ClientParser.HttpMessageBodyContext):
        
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
    def visitHttpMultipart(self, ctx:ClientParser.HttpMultipartContext):

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
    def visitHttpMultipartBoundary(self, ctx:ClientParser.HttpMultipartBoundaryContext):
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
    def visitHttpMessageBodyContent(self, ctx:ClientParser.HttpMessageBodyContentContext):
        
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
    def visitHttpMessageBodyOperate(self, ctx:ClientParser.HttpMessageBodyOperateContext):
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
    def visitHttpMessageBodyOther(self, ctx:ClientParser.HttpMessageBodyOtherContext):
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


    # Loop Until
    def visitLoopUntil(self, ctx:ClientParser.LoopUntilContext):

        parsedObject = {'name': 'LOOP UNTIL' , 'rule': ctx.getRuleIndex() }
        
        if (ctx.INT() is not None):
            parsedObject.update({'param': ctx.INT().getText()})

        if (ctx.expression() is not None):
            result, script, hint, code, message =  self.visit(ctx.expression())
            parsedObject.update({'expression': result})

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
    def visitLoop(self, ctx:ClientParser.LoopContext):
        parsedObject = {'name': 'LOOP' , 'rule': ctx.getRuleIndex() }
        
        pairs = []
        for pair in ctx.loopPair():
            result, script, hint, code, message =  self.visit(pair)
            pairs.append(result)
        
        parsedObject.update({'pair': pairs })

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

    def visitLoopPair(self, ctx:ClientParser.LoopPairContext):

        parsedObject = {}

        if (ctx.String() is not None) and (ctx.expression() is not None):
            result, script, hint, code, message =  self.visit(ctx.expression())
            parsedObject.update({ctx.String().getText() : result})

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
    

    # 
    def visitAssert(self, ctx:ClientParser.AssertContext):
        parsedObject = {'name': 'ASSERT' , 'rule': ctx.getRuleIndex() }

        expression = []
        for express in ctx.expression():
            result, script, hint, code, message =  self.visit(express)
            expression.append(result)
        
        parsedObject.update({'expression' : expression })

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


    # 解析SQL语句
    def visitSql(self, ctx:ClientParser.SqlContext):
        # 如果名字空间是 API SQL语句就不解析
        if self.defaultNameSpace == 'API':
            return None
        return self.visitChildren(ctx)


    # SQL Create 语句 
    def visitSqlCreate(self, ctx:ClientParser.SqlCreateContext):

        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        
        statement = ctx.SQL_CREATE().getText() + self.getText(tokens, ClientLexer.SQLSTATEMENT_CHANNEL)
        
        parsedObject = {'name': 'CREATE' , 'rule': ctx.getRuleIndex(), 'statement': statement }
        # 包含注释和提示
        originScript = self.getSource(tokens)
        # 句子中的提示
        hint = self.getHint(tokens)

        errorCode = 0
        errorMsg = None
        if (ctx.exception is not None):
            errorCode = -1
            errorMsg = ctx.exception.message
            self.isFinished = False
        # 
        if (ctx.SQL_END() is None) or ((ctx.SQL_END().getText() != ';') and (ctx.SQL_END().getText() != '\n/')):
            errorCode = -1
            self.isFinished = False

        self.parsedObject.append(parsedObject)
        self.originScripts.append(originScript)
        self.hints.append(hint)
        self.errorCode.append(errorCode)
        self.errorMsg.append(errorMsg)

        return  parsedObject, originScript, hint, errorCode, errorMsg

    def visitSqlReplace(self, ctx:ClientParser.SqlReplaceContext):
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        
        statement = ctx.SQL_REPLACE().getText() + self.getText(tokens, ClientLexer.SQLSTATEMENT_CHANNEL)
        
        parsedObject = {'name': 'REPLACE' , 'rule': ctx.getRuleIndex(), 'statement': statement }
        # 包含注释和提示
        originScript = self.getSource(tokens)
        # 句子中的提示
        hint = self.getHint(tokens)
        errorCode = 0
        errorMsg = None
        if (ctx.exception is not None):
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

        return  parsedObject, originScript, hint, errorCode, errorMsg

    # 
    def visitSqlInsert(self, ctx:ClientParser.SqlInsertContext):
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        
        statement = ctx.SQL_INSERT().getText() + self.getText(tokens, ClientLexer.SQLSTATEMENT_CHANNEL)
        
        parsedObject = {'name': 'INSERT' , 'rule': ctx.getRuleIndex(), 'statement': statement }
        # 包含注释和提示
        originScript = self.getSource(tokens)
        # 句子中的提示
        hint = self.getHint(tokens)
        errorCode = 0
        errorMsg = None
        if (ctx.exception is not None):
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

        return  parsedObject, originScript, hint, errorCode, errorMsg


    # 
    def visitSqlUpdate(self, ctx:ClientParser.SqlUpdateContext):
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        
        statement = ctx.SQL_UPDATE().getText() + self.getText(tokens, ClientLexer.SQLSTATEMENT_CHANNEL)
        
        parsedObject = {'name': 'UPDATE' , 'rule': ctx.getRuleIndex(), 'statement': statement }
        # 包含注释和提示
        originScript = self.getSource(tokens)
        # 句子中的提示
        hint = self.getHint(tokens)
        
        errorCode = 0
        errorMsg = None
        if (ctx.exception is not None):
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

        return  parsedObject, originScript, hint, errorCode, errorMsg


    # 删除语句
    def visitSqlDelete(self, ctx:ClientParser.SqlDeleteContext):
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        # 不包含注释
        statement = self.getText(tokens)
        
        parsedObject = {'name': 'DELETE' , 'rule': ctx.getRuleIndex(), 'statement': statement }
        # 包含注释和提示
        originScript = self.getSource(tokens)
        # 句子中的提示
        hint = self.getHint(tokens)
        errorCode = 0
        errorMsg = None
        if (ctx.exception is not None):
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

        return  parsedObject, originScript, hint, errorCode, errorMsg


    # 
    def visitSqlSelect(self, ctx:ClientParser.SqlSelectContext):
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        
        # SQL Statement
        statement = ctx.SQL_SELECT().getText() + self.getText(tokens, ClientLexer.SQLSTATEMENT_CHANNEL)
        
        parsedObject = {'name': 'SELECT' , 'rule': ctx.getRuleIndex(), 'statement': statement }
        # 包含注释和提示
        originScript = self.getSource(tokens)
        # 句子中的提示
        hint = self.getHint(tokens)
        errorCode = 0
        errorMsg = None
        if (ctx.exception is not None) :
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

        return  parsedObject, originScript, hint, errorCode, errorMsg


    def visitSqlDeclare(self, ctx:ClientParser.SqlDeclareContext):
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        
        statement = ctx.SQL_DECLARE().getText() + self.getText(tokens, ClientLexer.SQLSTATEMENT_CHANNEL)
        
        parsedObject = {'name': 'DECLARE' , 'rule': ctx.getRuleIndex(), 'statement': statement }
        # 包含注释和提示
        originScript = self.getSource(tokens)
        # 句子中的提示
        hint = self.getHint(tokens)
        errorCode = 0
        errorMsg = None
        if (ctx.exception is not None):
            errorCode = -1
            errorMsg = ctx.exception.message
            self.isFinished = False
        
        if (ctx.SQL_SLASH() is None) or (ctx.SQL_SLASH().getText() != '\n/'):
            errorCode = -1
            self.isFinished = False

        self.parsedObject.append(parsedObject)
        self.originScripts.append(originScript)
        self.hints.append(hint)
        self.errorCode.append(errorCode)
        self.errorMsg.append(errorMsg)

        return  parsedObject, originScript, hint, errorCode, errorMsg


    def visitSqlCreateProcedure(self, ctx:ClientParser.SqlCreateProcedureContext):
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        
        statement = ctx.SQL_CREATE_PROCEDURE().getText() + self.getText(tokens, ClientLexer.SQLSTATEMENT_CHANNEL)
        
        parsedObject = {'name': 'PROCEDURE' , 'rule': ctx.getRuleIndex(), 'statement': statement }
        # 包含注释和提示
        originScript = self.getSource(tokens)
        # 句子中的提示
        hint = self.getHint(tokens)
        errorCode = 0
        errorMsg = None
        if (ctx.exception is not None):
            errorCode = -1
            errorMsg = ctx.exception.message
            self.isFinished = False

        if (ctx.SQL_SLASH() is None) or (ctx.SQL_SLASH().getText() != '\n/'):
            errorCode = -1
            self.isFinished = False

        self.parsedObject.append(parsedObject)
        self.originScripts.append(originScript)
        self.hints.append(hint)
        self.errorCode.append(errorCode)
        self.errorMsg.append(errorMsg)

        return parsedObject, originScript, hint, errorCode, errorMsg

    def visitSqlUnknown(self, ctx: ClientParser.SqlUnknownContext):
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]

        # 不包含注释
        statement = self.getText(tokens)
        
        parsedObject = {'name': 'Unknown', 'rule': ctx.getRuleIndex(), 'statement': statement}

        # 包含注释和提示
        originScript = self.getSource(tokens)

        # 句子中的提示
        hint = self.getHint(tokens)
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        self.parsedObject.append(parsedObject)
        self.originScripts.append(originScript)
        self.hints.append(hint)
        self.errorCode.append(errorCode)
        self.errorMsg.append(errorMsg)

        return  parsedObject, originScript, hint, errorCode, errorMsg
