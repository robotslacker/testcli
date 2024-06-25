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
            "sleepTime": ctx.SLEEP_SEMICOLON().getText()
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

    def visitStart(self, ctx: APIParser.StartContext):
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

    def visitSet(self, ctx: APIParser.SetContext):
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

    def visitScript(self, ctx: APIParser.ScriptContext):
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

    def visitLoad(self, ctx: APIParser.LoadContext):
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

    def visitLoop(self, ctx: APIParser.LoopContext):
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

    def visitJob(self, ctx: APIParser.JobContext):
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

    def visitSsh(self, ctx: APIParser.SshContext):
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

    def visitData(self, ctx: APIParser.DataContext):
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

    def visitCompare(self, ctx: APIParser.CompareContext):
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
            errorMsg = "missing HTTP_CLOSE before <EOF>"
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
        key = None
        if ctx.httpHeaderFieldName() is not None:
            result, code, message = self.visit(ctx.httpHeaderFieldName())
            key = result['value']

        # 请求域定义值
        value = None
        if ctx.httpHeaderFieldValue() is not None:
            result, code, message = self.visit(ctx.httpHeaderFieldValue())
            value = result['value']
        
        # 合并生成新的KV值
        if key is not None:
            parsedObject.update({key: value})

        return parsedObject, errorCode, errorMsg

    """
        处理请求域定义名称部分
    """
    def visitHttpHeaderFieldName(self, ctx: APIParser.HttpHeaderFieldNameContext):
        if ctx.HttpHeaderFieldName() is None:
            parsedObject = {'value': ''}
        else:
            parsedObject = {'value': str(ctx.HttpHeaderFieldName().getText()).strip()}

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
        if ctx.HttpHeaderFieldValue() is None:
            parsedObject = {'value': ''}
        else:
            parsedObject = {'value': str(ctx.HttpHeaderFieldValue().getText()).strip()}

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

    """
        处理帮助命令
    """
    def visitHelp(self, ctx: APIParser.HelpContext):
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

    """
        处理性能监控命令
    """
    def visitMonitor(self, ctx: APIParser.MonitorContext):
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

    """
        处理APISET命令
    """
    def visitApiset(self, ctx: APIParser.ApisetContext):
        parsedObject = {'name': 'HTTPSET'}

        if ctx.APISET_PROXY() is not None:
            parsedObject.update({'option': 'PROXY'})
            if ctx.APISET_EXPRESSION() is not None:
                proxyAddress = str(ctx.APISET_EXPRESSION().getText()).strip()
                if proxyAddress.startswith('"') and proxyAddress.endswith('"'):
                    proxyAddress = proxyAddress[1:-1]
                elif proxyAddress.startswith("'") and proxyAddress.endswith("'"):
                    proxyAddress = proxyAddress[1:-1]
                parsedObject.update({'value': proxyAddress})
            else:
                parsedObject.update({'value': ""})
        if ctx.APISET_HTTPSVERIFY() is not None:
            parsedObject.update({'option': 'HTTPS_VERIFY'})
            if ctx.APISET_ON() is not None:
                parsedObject.update({'value': "ON"})
            if ctx.APISET_OFF() is not None:
                parsedObject.update({'value': "OFF"})

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
        处理API的SESSION命令
    """
    def visitSession(self, ctx: APIParser.SessionContext):
        parsedObject = {'name': 'HTTPSESSION'}

        if ctx.SESSION_SAVE() is not None:
            parsedObject.update({'action': "SAVE"})
        if ctx.SESSION_SHOW() is not None:
            parsedObject.update({'action': "SHOW"})
        if ctx.SESSION_RELEASE() is not None:
            parsedObject.update({'action': "RELEASE"})
        if ctx.SESSION_RESTORE() is not None:
            parsedObject.update({'action': "RESTORE"})
        if ctx.SESSION_NAME() is not None:
            sessionName = ctx.SESSION_NAME().getText()
            if sessionName.startswith('"') and sessionName.endswith('"'):
                sessionName = sessionName[1:-1]
            elif sessionName.startswith("'") and sessionName.endswith("'"):
                sessionName = sessionName[1:-1]
            parsedObject.update({'sessionName': sessionName})
        else:
            parsedObject.update({'sessionName': ""})

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        self.parsedObject = parsedObject
        self.errorCode = errorCode
        self.errorMsg = errorMsg

    def visitPlugin(self, ctx: APIParser.PluginContext):
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
