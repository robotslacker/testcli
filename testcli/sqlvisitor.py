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
        # 如果成功，返回0； 如果失败，返回-1；
        self.errorCode = 0
        # 如果成功，返回空；如果失败，返回解析的错误提示信息
        self.errorMsg = None

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
        return self.isFinished, self.parsedObject, self.errorCode, self.errorMsg
    
    def visitCommand(self, ctx: SQLParser.CommandContext):
        return self.visitChildren(ctx)
        
    def visitExit(self, ctx: SQLParser.ExitContext):
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

    def visitQuit(self, ctx: SQLParser.QuitContext):
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

    def visitUse(self, ctx: SQLParser.UseContext):
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

    def visitSleep(self, ctx: SQLParser.SleepContext):
        parsedObject = {
            'name': 'SLEEP',
            "sleepTime": ctx.SLEEP_EXPRESSION().getText()
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

    def visitConnect(self, ctx: SQLParser.ConnectContext):
        parsedObject = {'name': 'CONNECT'}

        # 用户信息
        if ctx.connectlocal() is not None:
            result, code, message = self.visit(ctx.connectlocal())
            parsedObject.update(result)
        if ctx.connectjdbc() is not None:
            result, code, message = self.visit(ctx.connectjdbc())
            parsedObject.update(result)

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        self.parsedObject = parsedObject
        self.errorCode = errorCode
        self.errorMsg = errorMsg

    def visitConnectjdbc(self, ctx: SQLParser.ConnectjdbcContext):
        parsedObject = {}
        if ctx.connectUserInfo() is not None:
            result, code, message = self.visit(ctx.connectUserInfo())
            parsedObject.update(result)
        if ctx.connectDriver() is not None:
            result, code, message = self.visit(ctx.connectDriver())
            parsedObject.update(result)
        if ctx.connectDriverSchema() is not None:
            result, code, message = self.visit(ctx.connectDriverSchema())
            parsedObject.update(result)
        if ctx.connectDriverType() is not None:
            result, code, message = self.visit(ctx.connectDriverType())
            parsedObject.update(result)
        if ctx.connectHost() is not None:
            result, code, message = self.visit(ctx.connectHost())
            parsedObject.update(result)
        if ctx.connectPort() is not None:
            result, code, message = self.visit(ctx.connectPort())
            parsedObject.update(result)
        if ctx.connectService() is not None:
            result, code, message = self.visit(ctx.connectService())
            parsedObject.update(result)
        if ctx.connectParameters() is not None:
            result, code, message = self.visit(ctx.connectParameters())
            parsedObject.update(result)

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        return parsedObject, errorCode, errorMsg

    def visitConnectlocal(self, ctx: SQLParser.ConnectlocalContext):
        parsedObject = {}
        if ctx.connectlocalService() is not None:
            result, code, message = self.visit(ctx.connectlocalService())
            parsedObject.update(result)

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        return parsedObject, errorCode, errorMsg

    def visitConnectlocalService(self, ctx: SQLParser.ConnectlocalServiceContext):
        parsedObject = {}
        if ctx.CONNECT_STRING() is not None:
            parsedObject.update({'localService': ctx.CONNECT_STRING().getText()})

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        return parsedObject, errorCode, errorMsg

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

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        return parsedObject, errorCode, errorMsg

    # connect中的用户信息
    def visitConnectUserInfo(self, ctx: SQLParser.ConnectUserInfoContext):
        parsedObject = {}

        # 用户名
        if ctx.connectUser() is not None:
            result, code, message = self.visit(ctx.connectUser())
            parsedObject.update(result)

        # password
        if ctx.connectPassword() is not None:
            result, code, message = self.visit(ctx.connectPassword())
            parsedObject.update(result)

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        return parsedObject, errorCode, errorMsg

    def visitConnectUser(self, ctx: SQLParser.ConnectUserContext):
        parsedObject = {}
        if ctx.CONNECT_STRING() is not None:
            parsedObject.update({'username': ctx.CONNECT_STRING().getText()})

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        return parsedObject, errorCode, errorMsg

    def visitConnectPassword(self, ctx: SQLParser.ConnectPasswordContext):
        parsedObject = {}
        if ctx.CONNECT_STRING() is not None:
            password = str(ctx.CONNECT_STRING().getText()).strip()
            if password.startswith('"') and password.endswith('"'):
                password = password[1:-1]
            elif password.startswith("'") and password.endswith("'"):
                password = password[1:-1]
            parsedObject.update({'password': password})

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        return parsedObject, errorCode, errorMsg

    def visitConnectDriver(self, ctx: SQLParser.ConnectDriverContext):
        parsedObject = {}
        if ctx.JDBC() is not None:
            parsedObject.update({'driver': "jdbc"})

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        return parsedObject, errorCode, errorMsg

    def visitConnectDriverSchema(self, ctx: SQLParser.ConnectDriverSchemaContext):
        parsedObject = {}
        if ctx.CONNECT_STRING() is not None:
            parsedObject.update({'driverSchema': ctx.CONNECT_STRING().getText()})

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        return parsedObject, errorCode, errorMsg

    def visitConnectDriverType(self, ctx: SQLParser.ConnectDriverSchemaContext):
        parsedObject = {}
        if ctx.CONNECT_STRING() is not None:
            parsedObject.update({'driverType': ctx.CONNECT_STRING().getText()})

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        return parsedObject, errorCode, errorMsg

    def visitConnectHost(self, ctx: SQLParser.ConnectHostContext):
        parsedObject = {'host': ctx.getText()}

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message
        return parsedObject, errorCode, errorMsg

    def visitConnectPort(self, ctx: SQLParser.ConnectPortContext):
        parsedObject = {'port': ctx.getText()}

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message
        return parsedObject, errorCode, errorMsg

    def visitConnectParameters(self, ctx: SQLParser.ConnectParametersContext):
        parsedObject = {}

        # 连接参数信息
        if ctx.connectParameter() is not None:
            parameters = []
            for parameter in ctx.connectParameter():
                result, code, message = self.visit(parameter)
                if code != 0:
                    errorCode = code
                    errorMsg = message
                    return parsedObject, errorCode, errorMsg
                parameters.append(result)
            parsedObject.update(
                {
                    "parameters": parameters
                }
            )

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        return parsedObject, errorCode, errorMsg

    def visitConnectParameter(self, ctx: SQLParser.ConnectParameterContext):
        parsedObject = {}

        if ctx.connectParameterName() is not None:
            result, code, message = self.visit(ctx.connectParameterName())
            parsedObject.update(result)

        if ctx.connectParameterValue() is not None:
            result, code, message = self.visit(ctx.connectParameterValue())
            parsedObject.update(result)

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message
        return parsedObject, errorCode, errorMsg

    def visitConnectParameterName(self, ctx: SQLParser.ConnectParameterNameContext):
        parsedObject = {'parameterName': ctx.getText()}

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message
        return parsedObject, errorCode, errorMsg

    def visitConnectParameterValue(self, ctx: SQLParser.ConnectParameterValueContext):
        parsedObject = {'parameterValue': ctx.getText()}

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message
        return parsedObject, errorCode, errorMsg

    def visitDisconnect(self, ctx: SQLParser.DisconnectContext):
        parsedObject = {'name': 'DISCONNECT'}

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        self.parsedObject = parsedObject
        self.errorCode = errorCode
        self.errorMsg = errorMsg

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
        param = ctx.ECHO().getText().partition(' ')[2]
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

    def visitLoop(self, ctx: SQLParser.LoopContext):
        parsedObject = {'name': 'LOOP'}
        if ctx.LOOP_END() is not None:
            parsedObject.update({"rule": "END"})
        elif ctx.LOOP_BREAK():
            parsedObject.update({"rule": "BREAK"})
        elif ctx.LOOP_CONTINUE():
            parsedObject.update({"rule": "CONTINUE"})
        elif ctx.LOOP_UNTIL():
            if ctx.LOOP_BEGIN() is not None:
                parsedObject.update({"rule": "BEGIN"})
            else:
                parsedObject.update({"rule": "UNTIL"})
                # 如果有两个INT，则第一个是最大循环次数，第二个是循环间隔
                # 如果只有一个INT，则第一个是循环间隔，没有最大循环次数
                if len(list(ctx.LOOP_INT())) == 2:
                    parsedObject.update({"interval": int(ctx.LOOP_INT()[1].getText())})
                    parsedObject.update({"limit": int(ctx.LOOP_INT()[0].getText())})
                else:
                    parsedObject.update({"interval": int(ctx.LOOP_INT()[0].getText())})
                    parsedObject.update({"limit": -1})
        if ctx.LOOP_EXPRESSION() is not None:
            expression = str(ctx.LOOP_EXPRESSION().getText())
            if expression.startswith("{%"):
                expression = expression[2:]
            if expression.endswith("%}"):
                expression = expression[:-2]
            expression = expression.strip()
            parsedObject.update({"until": expression})

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

    def visitJob(self, ctx: SQLParser.JobContext):
        parsedObject = {'name': 'JOB'}

        if ctx.JOB_MANGER() is not None:
            if ctx.JOB_ON():
                parsedObject.update({"action": "startJobmanager"})
            if ctx.JOB_OFF():
                parsedObject.update({"action": "stopJobmanager"})
        elif ctx.JOB_SHOW() is not None:
            jobName = str(ctx.JOB_EXPRESSION()[0].getText()).strip()
            parsedObject.update({"action": "show"})
            parsedObject.update({"jobName": jobName})
        elif ctx.JOB_WAIT() is not None:
            parsedObject.update({"action": "wait"})
            param = {}
            paramKey = None
            nPos = 0
            for expression in ctx.JOB_EXPRESSION():
                if nPos == 0:
                    jobName = str(expression.getText()).strip()
                    parsedObject.update({"jobName": jobName})
                else:
                    if paramKey is None:
                        paramKey = str(expression.getText()).strip()
                    else:
                        paramValue = str(expression.getText()).strip()
                        param[paramKey] = paramValue
                        paramKey = None
                nPos = nPos + 1
            parsedObject.update({"param": param})
        elif ctx.JOB_SHUTDOWN() is not None:
            jobName = str(ctx.JOB_EXPRESSION()[0].getText()).strip()
            parsedObject.update({"action": "shutdown"})
            parsedObject.update({"jobName": jobName})
        elif ctx.JOB_ABORT() is not None:
            jobName = str(ctx.JOB_EXPRESSION()[0].getText()).strip()
            parsedObject.update({"action": "abort"})
            parsedObject.update({"jobName": jobName})
        elif ctx.JOB_START() is not None:
            jobName = str(ctx.JOB_EXPRESSION()[0].getText()).strip()
            parsedObject.update({"action": "start"})
            parsedObject.update({"jobName": jobName})
        elif ctx.JOB_TIMER() is not None:
            timerPoint = str(ctx.JOB_EXPRESSION()[0].getText()).strip()
            parsedObject.update({"action": "timer"})
            parsedObject.update({"timerPoint": timerPoint})
        elif ctx.JOB_DEREGISTER() is not None:
            parsedObject.update({"action": "deregister"})
        elif ctx.JOB_REGISTER() is not None:
            jobName = str(ctx.JOB_EXPRESSION()[0].getText()).strip()
            parsedObject.update({"action": "register"})
            parsedObject.update({"jobName": jobName})
        elif ctx.JOB_SET() is not None:
            parsedObject.update({"action": "set"})
            param = {}
            paramKey = None
            nPos = 0
            for expression in ctx.JOB_EXPRESSION():
                if nPos == 0:
                    jobName = str(expression.getText()).strip()
                    parsedObject.update({"jobName": jobName})
                else:
                    if paramKey is None:
                        paramKey = str(expression.getText()).strip()
                    else:
                        paramValue = str(expression.getText()).strip()
                        param[paramKey] = paramValue
                        paramKey = None
                nPos = nPos + 1
            parsedObject.update({"param": param})
        elif ctx.JOB_CREATE() is not None:
            parsedObject.update({"action": "create"})
            param = {}
            paramKey = None
            nPos = 0
            for expression in ctx.JOB_EXPRESSION():
                if nPos == 0:
                    jobName = str(expression.getText()).strip()
                    parsedObject.update({"jobName": jobName})
                else:
                    if paramKey is None:
                        paramKey = str(expression.getText()).strip()
                    else:
                        paramValue = str(expression.getText()).strip()
                        param[paramKey] = paramValue
                        paramKey = None
                nPos = nPos + 1
            parsedObject.update({"param": param})

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

    def visitSsh(self, ctx: SQLParser.SshContext):
        parsedObject = {'name': 'SSH'}

        if ctx.SSH_SAVE() is not None:
            parsedObject.update({"action": "save"})
            if ctx.SSH_EXPRESSION() is not None:
                parsedObject.update({"sessionName": str(ctx.SSH_EXPRESSION()[0].getText())})
            else:
                parsedObject.update({"sessionName": None})
        elif ctx.SSH_RESTORE() is not None:
            parsedObject.update({"action": "restore"})
            if ctx.SSH_EXPRESSION() is not None:
                parsedObject.update({"sessionName": str(ctx.SSH_EXPRESSION()[0].getText())})
            else:
                parsedObject.update({"sessionName": None})
        elif ctx.SSH_SET() is not None:
            parsedObject.update({"action": "set"})
            option = str(ctx.SSH_EXPRESSION()[0].getText())
            value = str(ctx.SSH_EXPRESSION()[1].getText())
            if (option.startswith('"') and option.endswith('"')) or (option.startswith("'") and option.endswith("'")):
                option = option[1:-1]
            if (option.startswith('"') and option.endswith('"')) or (option.startswith("'") and option.endswith("'")):
                value = value[1:-1]
            parsedObject.update({"option": option})
            parsedObject.update({"value": value})
        elif ctx.SSH_DISCONNECT() is not None:
            parsedObject.update({"action": "disconnect"})
        elif ctx.SSH_EXECUTE() is not None:
            parsedObject.update({"action": "execute"})
            parsedObject.update({"command": ""})
            commands = []
            for expression in ctx.SSH_EXPRESSION():
                commands.append(str(expression.getText()))
            command = str(" ".join(commands)).strip()
            if (
                    (command.startswith('"') and not command.endswith('"')) or
                    (command.startswith("'") and not command.endswith("'"))
            ):
                # 括号不闭合
                self.isFinished = False
                self.parsedObject = parsedObject
                self.errorCode = 1
                self.errorMsg = "Missing <EOF> un-closed qutote string."
                return
            if command.startswith('"') and command.endswith('"'):
                command = command[1:-1]
            if command.startswith("'") and command.endswith("'"):
                command = command[1:-1]
            pairQuote = True
            for quoteChar in ['"', "'"]:
                for char in command:
                    if char == quoteChar:
                        pairQuote = not pairQuote
                if not pairQuote:
                    self.isFinished = False
                    self.parsedObject = parsedObject
                    self.errorCode = 1
                    self.errorMsg = "Missing <EOF> un-closed qutote string."
                    return
            parsedObject.update({"command": command})
        elif ctx.SSH_CONNECT() is not None:
            parsedObject.update({"action": "connect"})
            sshHost = str(ctx.SSH_EXPRESSION()[0].getText())
            if (
                    (sshHost.startswith('"') and sshHost.endswith('"')) or
                    (sshHost.startswith("'") and sshHost.endswith("'"))
            ):
                sshHost = sshHost[1:-1]
            parsedObject.update({"host": sshHost})
            if ctx.SSH_USER() is not None:
                parsedObject.update({"user": str(ctx.SSH_EXPRESSION()[1].getText())})
            if ctx.SSH_PASSWORD() is not None:
                parsedObject.update({"password": str(ctx.SSH_EXPRESSION()[2].getText())})
            if ctx.SSH_KEYFILE() is not None:
                keyFileName = str(ctx.SSH_EXPRESSION()[2].getText())
                if keyFileName.startswith('"') and keyFileName.endswith('"'):
                    keyFileName = keyFileName[1:-1]
                parsedObject.update({"keyFile": keyFileName})
        # 处理SFTP命令
        elif ctx.SFTP_CHMOD() is not None:
            parsedObject.update({"action": "sftp_chmod"})
            fileName = str(ctx.SSH_EXPRESSION()[0].getText())
            fileMod = str(ctx.INT()[0].getText())
            parsedObject.update({"fileName": fileName})
            parsedObject.update({"fileMod": fileMod})
        elif ctx.SFTP_GETCWD() is not None:
            parsedObject.update({"action": "sftp_cwd"})
        elif ctx.SFTP_CHDIR() is not None:
            parsedObject.update({"action": "sftp_chdir"})
            parsedObject.update({"dir": str(ctx.SSH_EXPRESSION()[0].getText())})
        elif ctx.SFTP_MKDIR() is not None:
            parsedObject.update({"action": "sftp_mkdir"})
            parsedObject.update({"dir": str(ctx.SSH_EXPRESSION()[0].getText())})
            parsedObject.update({"dirMod": str(ctx.INT()[0].getText())})
        elif ctx.SFTP_CHOWN() is not None:
            parsedObject.update({"action": "sftp_chown"})
            fileName = str(ctx.SSH_EXPRESSION()[0].getText())
            uid = int(ctx.INT()[0].getText())
            gid = int(ctx.INT()[1].getText())
            parsedObject.update({"fileName": fileName})
            parsedObject.update({"uid": uid})
            parsedObject.update({"gid": gid})
        elif ctx.SFTP_GET() is not None:
            parsedObject.update({"action": "sftp_get"})
            parsedObject.update({"remoteFile": str(ctx.SSH_EXPRESSION()[0].getText())})
            parsedObject.update({"localFile": str(ctx.SSH_EXPRESSION()[1].getText())})
        elif ctx.SFTP_PUT() is not None:
            parsedObject.update({"action": "sftp_put"})
            parsedObject.update({"localFile": str(ctx.SSH_EXPRESSION()[0].getText())})
            parsedObject.update({"remoteFile": str(ctx.SSH_EXPRESSION()[1].getText())})
        elif ctx.SFTP_REMOVE() is not None:
            parsedObject.update({"action": "sftp_remove"})
            parsedObject.update({"file": str(ctx.SSH_EXPRESSION()[0].getText())})
        elif ctx.SFTP_RENAME() is not None:
            parsedObject.update({"action": "sftp_rename"})
            parsedObject.update({"oldFile": str(ctx.SSH_EXPRESSION()[0].getText())})
            parsedObject.update({"newFile": str(ctx.SSH_EXPRESSION()[1].getText())})
        elif ctx.SFTP_LISTDIR() is not None:
            parsedObject.update({"action": "sftp_listdir"})
            parsedObject.update({"dir": str(ctx.SSH_EXPRESSION()[0].getText())})
        elif ctx.SFTP_TRUNCATE() is not None:
            parsedObject.update({"action": "sftp_truncate"})
            parsedObject.update({"file": str(ctx.SSH_EXPRESSION()[0].getText())})
            fileSize = int(ctx.INT()[0].getText())
            parsedObject.update({"fileSize": fileSize})

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

    def visitCompare(self, ctx: SQLParser.CompareContext):
        parsedObject = {'name': 'COMPARE'}

        # 重置比较选项
        if ctx.COMPARE_RESET() is not None:
            parsedObject.update({'action': "reset"})

        # 比较选项
        compareOptions = {}
        if len(ctx.COMPARE_CASE()) != 0:
            compareOptions.update({"case": True})
        if len(ctx.COMPARE_NOCASE()) != 0:
            compareOptions.update({"case": False})
        if len(ctx.COMPARE_MASK()) != 0:
            compareOptions.update({"mask": True})
        if len(ctx.COMPARE_NOMASK()) != 0:
            compareOptions.update({"mask": False})
        if len(ctx.COMPARE_IGBLANK()) != 0:
            compareOptions.update({"igblank": True})
        if len(ctx.COMPARE_NOIGBLANK()) != 0:
            compareOptions.update({"igblank": False})
        if len(ctx.COMPARE_TRIM()) != 0:
            compareOptions.update({"trim": True})
        if len(ctx.COMPARE_NOTRIM()) != 0:
            compareOptions.update({"trim": False})
        output = []
        if len(ctx.COMPARE_CONSOLE()) != 0:
            output.append("console")
        if len(ctx.COMPARE_DIFFFILE()) != 0:
            output.append("diffFile")
        if len(ctx.COMPARE_HTMLFILE()) != 0:
            output.append("htmlFile")
        if len(output) != 0:
            compareOptions.update({"output": output})
        if ctx.COMPARE_LCS() is not None:
            compareOptions.update({"algorithm": "lcs"})
        if ctx.COMPARE_MYERS() is not None:
            compareOptions.update({"algorithm": "myers"})
        if ctx.COMPARE_DIFFLIB() is not None:
            compareOptions.update({"algorithm": "difflib"})
        if ctx.COMPARE_ENCODING() is not None:
            if ctx.COMPARE_WORK() is not None:
                compareOptions.update({"workEncoding": (ctx.COMPARE_EXPRESSION()[0].getText())})
            if ctx.COMPARE_REFERENCE() is not None:
                compareOptions.update({"refEncoding": (ctx.COMPARE_EXPRESSION()[0].getText())})
        parsedObject.update({'compareOptions': compareOptions})

        # maskline命令
        if ctx.COMPARE_MASKLINE() is not None:
            parsedObject.update({'action': "mask"})
            if ctx.COMPARE_EXPRESSION() is not None:
                parsedObject.update({'source': str(ctx.COMPARE_EXPRESSION()[0].getText())})
                if len(ctx.COMPARE_EXPRESSION()) > 1:
                    parsedObject.update({'target': str(ctx.COMPARE_EXPRESSION()[1].getText())})
        if ctx.COMPARE_NOMASKLINE() is not None:
            parsedObject.update({'action': "nomask"})
            if ctx.COMPARE_EXPRESSION() is not None:
                parsedObject.update({'source': str(ctx.COMPARE_EXPRESSION()[0].getText())})

        # skipline命令
        if ctx.COMPARE_SKIPLINE() is not None:
            parsedObject.update({'action': "skip"})
            if ctx.COMPARE_EXPRESSION() is not None:
                skipLine = str(ctx.COMPARE_EXPRESSION()[0].getText()).strip()
                if skipLine.startswith("'") and skipLine.endswith("'"):
                    skipLine = skipLine[1:-1]
                elif skipLine.startswith('"') and skipLine.endswith('"'):
                    skipLine = skipLine[1:-1]
                parsedObject.update({'source': skipLine})
        if ctx.COMPARE_NOSKIPLINE() is not None:
            parsedObject.update({'action': "noskip"})
            if ctx.COMPARE_EXPRESSION() is not None:
                skipLine = str(ctx.COMPARE_EXPRESSION()[0].getText()).strip()
                if skipLine.startswith("'") and skipLine.endswith("'"):
                    skipLine = skipLine[1:-1]
                elif skipLine.startswith('"') and skipLine.endswith('"'):
                    skipLine = skipLine[1:-1]
                parsedObject.update({'source': skipLine})

        # SET
        if ctx.COMPARE_SET() is not None:
            parsedObject.update({'action': "set"})

        # 非特殊设置选项，即默认的Compare命令
        if ctx.COMPARE_SET() is None and \
                ctx.COMPARE_SKIPLINE() is None and \
                ctx.COMPARE_NOSKIPLINE() is None and \
                ctx.COMPARE_MASKLINE() is None and \
                ctx.COMPARE_NOMASKLINE() is None and \
                ctx.COMPARE_RESET() is None and \
                ctx.COMPARE_EXPRESSION() is not None:
            parsedObject.update({'action': "compare"})
            parsedObject.update({'targetFile': str(ctx.COMPARE_EXPRESSION()[0].getText())})
            if len(ctx.COMPARE_EXPRESSION()) > 1:
                parsedObject.update({'referenceFile': str(ctx.COMPARE_EXPRESSION()[1].getText())})

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

    def visitData(self, ctx: SQLParser.DataContext):
        parsedObject = {'name': 'DATA'}

        if ctx.DATA_SET() is not None:
            parsedObject.update({"action": "set"})
            if ctx.DATA_SEEDFILE() is not None:
                parsedObject.update({"option": "seedDir"})
                if len(ctx.DATA_EXPRESSION()) != 0:
                    seedDir = str(ctx.DATA_EXPRESSION()[0].getText()).strip()
                    if seedDir.startswith('"') and seedDir.endswith('"'):
                        seedDir = seedDir[1:-1]
                    elif seedDir.startswith("'") and seedDir.endswith("'"):
                        seedDir = seedDir[1:-1]
                    parsedObject.update({"seedDir": seedDir})
            if ctx.DATA_HDFSUSER() is not None:
                parsedObject.update({"option": "hdfsUser"})
                if len(ctx.DATA_EXPRESSION()) != 0:
                    hdfsUser = str(ctx.DATA_EXPRESSION()[0].getText()).strip()
                    if hdfsUser.startswith('"') and hdfsUser.endswith('"'):
                        hdfsUser = hdfsUser[1:-1]
                    elif hdfsUser.startswith("'") and hdfsUser.endswith("'"):
                        hdfsUser = hdfsUser[1:-1]
                    parsedObject.update({"hdfsUser": hdfsUser})

        if ctx.DATA_CONVERT() is not None:
            parsedObject.update({"action": "convert"})
            parsedObject.update({"sourceFileType": str(ctx.DATA_FILETYPE()[0].getText())})
            parsedObject.update({"targetFileType": str(ctx.DATA_FILETYPE()[1].getText())})
            sourceFile = str(ctx.DATA_EXPRESSION()[0].getText())
            targetFile = str(ctx.DATA_EXPRESSION()[1].getText())
            if sourceFile.startswith('"') and sourceFile.endswith('"'):
                sourceFile = sourceFile[1:-1]
            elif sourceFile.startswith("'") and sourceFile.endswith("'"):
                sourceFile = sourceFile[1:-1]
            if targetFile.startswith('"') and targetFile.endswith('"'):
                targetFile = targetFile[1:-1]
            elif targetFile.startswith("'") and targetFile.endswith("'"):
                targetFile = targetFile[1:-1]
            parsedObject.update({"sourceFile": sourceFile})
            parsedObject.update({"targetFile": targetFile})

        if ctx.DATA_CREATE() is not None:
            parsedObject.update({"action": "create"})
            parsedObject.update({"fileType": str(ctx.DATA_FILETYPE()[0].getText())})
            targetFile = str(ctx.DATA_EXPRESSION()[0].getText())
            if targetFile.startswith('"') and targetFile.endswith('"'):
                targetFile = targetFile[1:-1]
            elif targetFile.startswith("'") and targetFile.endswith("'"):
                targetFile = targetFile[1:-1]
            parsedObject.update({"targetFile": targetFile})
            if ctx.DATA_ROWS() is not None:
                parsedObject.update({"rowCount": int(ctx.DATA_INT().getText())})
            else:
                # 默认输出是1行
                parsedObject.update({"rowCount": 1})
            columnExpression = ""
            if ctx.DATACOLUMN_CONTENT() is not None:
                columnExpression = str(ctx.DATACOLUMN_CONTENT().getText()).strip()
                if columnExpression.endswith(')'):
                    columnExpression = columnExpression[:-1]
            parsedObject.update({"columnExpression": str(columnExpression)})

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

    def visitStart(self, ctx: SQLParser.StartContext):
        parsedObject = {'name': 'START'}

        # 第一个参数为脚本名称，随后的参数为运行参数
        argv = []
        if ctx.START_EXPRESSION() is not None:
            nPos = 0
            for expression in ctx.START_EXPRESSION():
                if nPos == 0:
                    parsedObject.update({'script': str(expression.getText())})
                    nPos = nPos + 1
                else:
                    argv.append(str(expression.getText()))
        else:
            parsedObject.update({'script': None})
        parsedObject.update({"argv": argv})

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

    def visitExpression(self, ctx: SQLParser.ExpressionContext):
        expression = ctx.getText()

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        return expression, errorCode, errorMsg

    def visitSet(self, ctx: SQLParser.SetContext):
        parsedObject = {'name': 'SET'}

        expression_list = []
        for expression in ctx.SET_EXPRESSION():
            expression_list.append(str(expression.getText()))

        if len(expression_list) >= 1:
            parsedObject.update({'optionName': expression_list[0]})
        if len(expression_list) >= 2:
            optionValue = " ".join(expression_list[1:])
            if ((optionValue.startswith('"') and optionValue.endswith('"')) or
                    (optionValue.startswith("'") and optionValue.endswith("'"))):
                optionValue = optionValue[1:-1]
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
            
        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        self.parsedObject = parsedObject
        self.errorCode = errorCode
        self.errorMsg = errorMsg

    def visitHost(self, ctx: SQLParser.HostContext):
        parsedObject = {'name': 'HOST'}

        # 删除BLOCK 末尾的 ECHO OFF
        if ctx.HOST_EXPRESSION() is not None:
            script = str(ctx.HOST_EXPRESSION().getText()).strip().strip('"').strip("'").strip("\n")
            script = script.replace("\n", " & ")
            parsedObject.update({'script': script})

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        self.parsedObject = parsedObject
        self.errorCode = errorCode
        self.errorMsg = errorMsg

    def visitLoad(self, ctx: SQLParser.LoadContext):
        parsedObject = {'name': 'LOAD'}

        # 加载的选项
        if ctx.LOAD_PLUGIN() is not None:
            parsedObject.update({"option": "PLUGIN"})
            pluginFile = str((ctx.LOAD_EXPRESSION()[0].getText())).strip()
            pluginFile = pluginFile.strip('"').strip("'")
            parsedObject.update({"pluginFile": pluginFile})
        if ctx.LOAD_SCRIPT() is not None:
            parsedObject.update({"option": "SCRIPT"})
            pluginFile = str((ctx.LOAD_EXPRESSION()[0].getText())).strip()
            pluginFile = pluginFile.strip('"').strip("'")
            parsedObject.update({"scriptFile": pluginFile})
        if ctx.LOAD_MAP() is not None:
            parsedObject.update({"option": "MAP"})
            mapFile = str((ctx.LOAD_EXPRESSION()[0].getText())).strip()
            mapFile = mapFile.strip('"').strip("'")
            parsedObject.update({"mapFile": mapFile})
        if ctx.LOAD_JDBCDRIVER() is not None:
            parsedObject.update({"option": "JDBCDRIVER"})
        if len(ctx.LOAD_JDBCCLASS()) != 0:
            optionCtx = ctx.LOAD_JDBCCLASS()[0]
            start, _ = optionCtx.getSourceInterval()
            for token in ctx.parser._input.tokens[start+1:]:
                if str(token.text) != '=':
                    parsedObject.update({"driverClass": str(token.text)})
                    break
        if len(ctx.LOAD_JDBCURL()) != 0:
            optionCtx = ctx.LOAD_JDBCURL()[0]
            start, _ = optionCtx.getSourceInterval()
            for token in ctx.parser._input.tokens[start+1:]:
                if str(token.text) != '=':
                    jdbcurl = str(token.text).strip('"').strip("'")
                    parsedObject.update({"driverURL": str(jdbcurl)})
                    break
        if len(ctx.LOAD_JDBCFILE()) != 0:
            optionCtx = ctx.LOAD_JDBCFILE()[0]
            start, _ = optionCtx.getSourceInterval()
            for token in ctx.parser._input.tokens[start+1:]:
                if str(token.text) != '=':
                    driverFile = str(token.text).strip('"').strip("'")
                    parsedObject.update({"driverFile": driverFile})
                    break
        if len(ctx.LOAD_JDBCNAME()) != 0:
            optionCtx = ctx.LOAD_JDBCNAME()[0]
            start, _ = optionCtx.getSourceInterval()
            for token in ctx.parser._input.tokens[start+1:]:
                if str(token.text) != '=':
                    parsedObject.update({"driverName": str(token.text)})
                    break
        if len(ctx.LOAD_JDBCPROP()) != 0:
            optionCtx = ctx.LOAD_JDBCPROP()[0]
            start, _ = optionCtx.getSourceInterval()
            for token in ctx.parser._input.tokens[start+1:]:
                if str(token.text) != '=':
                    driverProps = str(token.text).strip('"').strip("'")
                    parsedObject.update({"driverProps": driverProps})
                    break

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        self.parsedObject = parsedObject
        self.errorCode = errorCode
        self.errorMsg = errorMsg

    def visitWhenever(self, ctx: SQLParser.WheneverContext):
        parsedObject = {'name': 'WHENEVER'}

        if ctx.WHENEVER_CONTINUE():
            parsedObject.update({"action": 'continue'})
        if ctx.WHENEVER_EXIT():
            parsedObject.update({"action": 'exit'})
        if ctx.WHENEVER_ERROR():
            parsedObject.update({"condition": 'error'})
        if ctx.WHENEVER_EXITCODE():
            parsedObject.update({"exitCode": int(ctx.WHENEVER_EXITCODE().getText())})
        else:
            parsedObject.update({"exitCode": 0})

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        self.parsedObject = parsedObject
        self.errorCode = errorCode
        self.errorMsg = errorMsg

    def visitIf(self, ctx: SQLParser.IfContext):
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

    def visitEndif(self, ctx: SQLParser.EndifContext):
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

    def visitSpool(self, ctx: SQLParser.SpoolContext):
        if ctx.SPOOL_EXPRESSION() is not None:
            content = str(ctx.SPOOL_EXPRESSION().getText()).strip()
            if content.startswith("'") and content.endswith("'"):
                content = content[1:-1]
            elif content.startswith('"') and content.endswith('"'):
                content = content[1:-1]
        else:
            content = ""

        if ctx.SPOOL_OFF() is not None:
            content = "OFF"
        parsedObject = {
            'name': 'SPOOL',
            'file': content
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

    def visitScript(self, ctx: SQLParser.ScriptContext):
        parsedObject = {'name': 'SCRIPT'}

        # 删除BLOCK 末尾的 %}
        if ctx.ScriptBlock() is not None:
            block = ctx.ScriptBlock().getText()
            if str(block).endswith('%}'):
                block = str(block[:-2])
                # 去掉第一个空行以及末尾不必要的空格
                block = block.lstrip('\n')
                block = block.rstrip()

                # 如果脚本仅有一行，则前导空格没有意义，直接去掉
                if len(block.split('\n')) == 1:
                    block = block.strip()

                # 替换所有的前导4字节空格（如果存在）
                block = block.replace('\t', '    ')
                minHeaderSpace = 99999
                for line in block.split('\n'):
                    if len(line) == 0:
                        continue
                    if minHeaderSpace > len(line) - len(line.lstrip()):
                        minHeaderSpace = len(line) - len(line.lstrip())
                # 如果脚本整体推进了4个空格，则认为没有推进（推进会让代码美观）
                if minHeaderSpace == 4:
                    newLines = []
                    for line in block.split('\n'):
                        newLines.append(line[4:])
                    block = "\n".join(newLines)
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

        if ctx.ASSERT_NAME() is not None:
            assertName = str(ctx.ASSERT_NAME().getText()).strip()
            if assertName.startswith('"') and assertName.endswith('"'):
                assertName = assertName[1:-1]
            if assertName.startswith("'") and assertName.endswith("'"):
                assertName = assertName[1:-1]
            parsedObject.update({'assertName': assertName})
        else:
            parsedObject.update({'assertName': None})

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        self.parsedObject = parsedObject
        self.errorCode = errorCode
        self.errorMsg = errorMsg

    def visitSql(self, ctx: SQLParser.SqlContext):
        return self.visitChildren(ctx)

    def visitSqlCreate(self, ctx: SQLParser.SqlCreateContext):
        # 获取源文件
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]

        statement = ctx.SQL_CREATE().getText() + self.getText(tokens, SQLLexer.SQLSTATEMENT_CHANNEL)
        parsedObject = {'name': 'CREATE', 'statement': statement}

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        # 如果SQL没有结尾，要返回没有结尾的标志
        if (ctx.SQL_END() is None) or ((ctx.SQL_END().getText() != ';') and (ctx.SQL_END().getText() != '\n/')):
            self.isFinished = False

        self.parsedObject = parsedObject
        self.errorCode = errorCode
        self.errorMsg = errorMsg

    def visitSqlDrop(self, ctx: SQLParser.SqlDropContext):
        # 获取源文件
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]

        statement = ctx.SQL_DROP().getText() + self.getText(tokens, SQLLexer.SQLSTATEMENT_CHANNEL)
        parsedObject = {'name': 'DROP', 'statement': statement}

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        # 如果SQL没有结尾，要返回没有结尾的标志
        if (ctx.SQL_END() is None) or ((ctx.SQL_END().getText() != ';') and (ctx.SQL_END().getText() != '\n/')):
            self.isFinished = False

        self.parsedObject = parsedObject
        self.errorCode = errorCode
        self.errorMsg = errorMsg

    def visitSqlReplace(self, ctx: SQLParser.SqlReplaceContext):
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        statement = ctx.SQL_REPLACE().getText() + self.getText(tokens, SQLLexer.SQLSTATEMENT_CHANNEL)
        parsedObject = {'name': 'REPLACE', 'statement': statement}

        # 处理错误信息
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message
            self.isFinished = False
        if (ctx.SQL_END() is None) or ((ctx.SQL_END().getText() != ';') and (ctx.SQL_END().getText() != '\n/')):
            errorCode = -1
            self.isFinished = False

        self.parsedObject = parsedObject
        self.errorCode = errorCode
        self.errorMsg = errorMsg

    def visitSqlInsert(self, ctx: SQLParser.SqlInsertContext):
        # 获取源文件
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        statement = ctx.SQL_INSERT().getText() + self.getText(tokens, SQLLexer.SQLSTATEMENT_CHANNEL)
        parsedObject = {'name': 'INSERT', 'statement': statement}

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        # 如果SQL没有结尾，要返回没有结尾的标志
        if (ctx.SQL_END() is None) or ((ctx.SQL_END().getText() != ';') and (ctx.SQL_END().getText() != '\n/')):
            self.isFinished = False

        self.parsedObject = parsedObject
        self.errorCode = errorCode
        self.errorMsg = errorMsg

    def visitSqlUpdate(self, ctx: SQLParser.SqlUpdateContext):
        # 获取源文件
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        statement = ctx.SQL_UPDATE().getText() + self.getText(tokens, SQLLexer.SQLSTATEMENT_CHANNEL)
        parsedObject = {'name': 'UPDATE', 'statement': statement}

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        # 如果SQL没有结尾，要返回没有结尾的标志
        if (ctx.SQL_END() is None) or ((ctx.SQL_END().getText() != ';') and (ctx.SQL_END().getText() != '\n/')):
            self.isFinished = False

        self.parsedObject = parsedObject
        self.errorCode = errorCode
        self.errorMsg = errorMsg

    def visitSqlDelete(self, ctx: SQLParser.SqlDeleteContext):
        # 获取源文件
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        statement = ctx.SQL_DELETE().getText() + self.getText(tokens, SQLLexer.SQLSTATEMENT_CHANNEL)
        parsedObject = {'name': 'DELETE', 'statement': statement}

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        # 如果SQL没有结尾，要返回没有结尾的标志
        if (ctx.SQL_END() is None) or ((ctx.SQL_END().getText() != ';') and (ctx.SQL_END().getText() != '\n/')):
            self.isFinished = False

        self.parsedObject = parsedObject
        self.errorCode = errorCode
        self.errorMsg = errorMsg

    def visitSqlSelect(self, ctx: SQLParser.SqlSelectContext):
        # 获取源文件
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        statement = ctx.SQL_SELECT().getText() + self.getText(tokens, SQLLexer.SQLSTATEMENT_CHANNEL)
        parsedObject = {'name': 'SELECT', 'statement': statement}

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        # 如果SQL没有结尾，要返回没有结尾的标志
        if (ctx.SQL_END() is None) or ((ctx.SQL_END().getText() != ';') and (ctx.SQL_END().getText() != '\n/')):
            self.isFinished = False

        self.parsedObject = parsedObject
        self.errorCode = errorCode
        self.errorMsg = errorMsg

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

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        # 如果SQL没有结尾，要返回没有结尾的标志
        if (ctx.SQL_SLASH() is None) or (ctx.SQL_SLASH().getText() != '\n/'):
            self.isFinished = False

        self.parsedObject = parsedObject
        self.errorCode = errorCode
        self.errorMsg = errorMsg

    def visitSqlCreateProcedure(self, ctx: SQLParser.SqlCreateProcedureContext):
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        statement = ctx.SQL_CREATE_PROCEDURE().getText() + self.getText(tokens, SQLLexer.SQLSTATEMENT_CHANNEL)
        parsedObject = {
            'name': 'PROCEDURE',
            'statement': statement}

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        # 如果SQL没有结尾，要返回没有结尾的标志
        if (ctx.SQL_SLASH() is None) or (ctx.SQL_SLASH().getText() != '\n/'):
            self.isFinished = False

        self.parsedObject = parsedObject
        self.errorCode = errorCode
        self.errorMsg = errorMsg

    def visitHelp(self, ctx: SQLParser.HelpContext):
        parsedObject = {'name': 'HELP'}

        parsedObject.update({'topic': ""})
        if ctx.HELP_COMMAND() is not None:
            parsedObject.update({'topic': str(ctx.HELP_COMMAND().getText()).strip().upper()})

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        self.parsedObject = parsedObject
        self.errorCode = errorCode
        self.errorMsg = errorMsg

    def visitMonitor(self, ctx: SQLParser.MonitorContext):
        parsedObject = {'name': 'MONITOR'}

        if ctx.MONITOR_MANAGER() is not None:
            if ctx.MONITOR_ON() is not None:
                parsedObject.update({'action': 'startManager'})
                if ctx.MONITOR_WORKERS() is not None:
                    workerThreads = int(ctx.MONITOR_EXPRESSION()[0].getText())
                else:
                    workerThreads = None
                parsedObject.update({'workerThreads': workerThreads})
            if ctx.MONITOR_OFF() is not None:
                parsedObject.update({'action': 'stopManager'})
        if ctx.MONITOR_CREATE() is not None:
            parsedObject.update({'action': 'createTask'})
            nPos = 0
            param = {}
            paramKey = None
            if len(ctx.MONITOR_EXPRESSION()) % 2 == 0:
                # 省略了taskName
                parsedObject.update({"taskName": "NO-NAME"})
                for expression in ctx.MONITOR_EXPRESSION():
                    if paramKey is None:
                        paramKey = str(expression.getText()).strip()
                    else:
                        paramValue = str(expression.getText()).strip()
                        param[paramKey.upper()] = paramValue
                        paramKey = None
                    nPos = nPos + 1
            else:
                for expression in ctx.MONITOR_EXPRESSION():
                    if nPos == 0:
                        parsedObject.update({"taskName": expression.getText().strip()})
                    else:
                        if paramKey is None:
                            paramKey = str(expression.getText()).strip()
                        else:
                            paramValue = str(expression.getText()).strip()
                            param[paramKey.upper()] = paramValue
                            paramKey = None
                    nPos = nPos + 1
            parsedObject.update({"param": param})
        if ctx.MONITOR_START() is not None:
            parsedObject.update({"action": "startTask"})
            taskName = str(ctx.MONITOR_EXPRESSION()[0].getText()).strip()
            parsedObject.update({"taskName": taskName})
        if ctx.MONITOR_STOP() is not None:
            parsedObject.update({"action": "stopTask"})
            taskName = str(ctx.MONITOR_EXPRESSION()[0].getText()).strip()
            parsedObject.update({"taskName": taskName})
        if ctx.MONITOR_REPORT() is not None:
            parsedObject.update({"action": "reportTask"})
            taskName = str(ctx.MONITOR_EXPRESSION()[0].getText()).strip()
            parsedObject.update({"taskName": taskName})
        if ctx.MONITOR_LIST() is not None:
            parsedObject.update({"action": "listTask"})

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        self.parsedObject = parsedObject
        self.errorCode = errorCode
        self.errorMsg = errorMsg

    def visitPlugin(self, ctx: SQLParser.PluginContext):
        parsedObject = {'name': 'PLUGIN'}

        pluginName = str(ctx.PLUGIN().getText()).strip()
        if pluginName.startswith("_"):
            pluginName = pluginName[1:]
        parsedObject.update({"pluginName": pluginName})

        pluginArgs = []
        if ctx.PLUGIN_EXPRESSION() is not None:
            for expression in ctx.PLUGIN_EXPRESSION():
                if expression is not None:
                    arg = str(expression.getText())
                    if arg.startswith('"') and arg.endswith('"'):
                        arg = arg[1:-1]
                    elif arg.startswith("'") and arg.endswith("'"):
                        arg = arg[1:-1]
                    pluginArgs.append(arg)
        parsedObject.update(
            {"pluginArgs": pluginArgs}
        )

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        self.parsedObject = parsedObject
        self.errorCode = errorCode
        self.errorMsg = errorMsg
