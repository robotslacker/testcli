# -*- coding: utf-8 -*-
import time
import paramiko
import io
import copy
from ..common import rewriteStatement

sshSession = {}
sshCurrentSessionName = "NONAME"


class SshContext:
    def __init__(self):
        self.host = ""
        self.port = 22
        self.user = ""
        self.pwd = None
        self.key = None
        self.options = {
            "encoding": None
        }
        self.sshTransport = None
        self.sftpHandler = None

    def setHost(self, host: str):
        self.host = host

    def setPort(self, port: int):
        self.port = port

    def setUser(self, user: str):
        self.user = user

    def setPassword(self, password: str):
        self.pwd = password

    def setKey(self, key):
        self.key = key

    def setSshTransport(self, sshTransport):
        self.sshTransport = sshTransport

    def setSftpHandler(self, sftpHandler):
        self.sftpHandler = sftpHandler

    def getHost(self):
        return self.host

    def getPort(self):
        return self.port

    def getUser(self):
        return self.user

    def getPassword(self):
        return self.pwd

    def getKey(self):
        return self.key

    def getSshTransport(self):
        return self.sshTransport

    def getSftpHandler(self):
        return self.sftpHandler

    def getOptions(self):
        return copy.copy(self.options)

    def getOption(self, option):
        return self.options.get(option)

    def setOptions(self, options):
        self.options = copy.copy(options)


def rewriteSshRequest(cls, requestObject, commandScriptFile: str):
    """
        重写SSH的请求信息
    """

    # 保留原脚本
    rawRequestObject = copy.copy(requestObject)
    rewrotedCommand = ""

    if "host" in requestObject:
        statement = requestObject["host"]
        newStatement = rewriteStatement(cls=cls, statement=statement, commandScriptFile=commandScriptFile)
        if statement != newStatement:
            requestObject.update({"host": newStatement})
    if "user" in requestObject:
        statement = requestObject["user"]
        newStatement = rewriteStatement(cls=cls, statement=statement, commandScriptFile=commandScriptFile)
        if statement != newStatement:
            requestObject.update({"user": newStatement})
    if "password" in requestObject:
        statement = requestObject["password"]
        newStatement = rewriteStatement(cls=cls, statement=statement, commandScriptFile=commandScriptFile)
        if statement != newStatement:
            requestObject.update({"password": newStatement})
    if "command" in requestObject:
        statement = requestObject["command"]
        newStatement = rewriteStatement(cls=cls, statement=statement, commandScriptFile=commandScriptFile)
        if statement != newStatement:
            requestObject.update({"command": newStatement})

    # 语句发生了变化
    if rawRequestObject != requestObject:
        rewrotedCommand = "Your request has been change to :\nREWROTED CMD>"
        # 记录被变量信息改写的命令
        if requestObject["action"] == "connect":
            rewrotedCommand = \
                rewrotedCommand + "_SSH CONNECT " + requestObject["host"] + " WITH USER " + requestObject["user"]
            if "password" in requestObject:
                rewrotedCommand = rewrotedCommand + " PASSWORD " + requestObject["password"]
            if "keyFile" in requestObject:
                rewrotedCommand = rewrotedCommand + " KEYFILE " + requestObject["keyFile"]
        if requestObject["action"] == "execute":
            commandSplits = str(requestObject["command"]).split('\n')
            rewrotedCommand = rewrotedCommand + " _SSH EXECUTE " + commandSplits[0]
            if len(commandSplits) > 1:
                for nIter in range(1, len(commandSplits)):
                    rewrotedCommand = rewrotedCommand + "\nREWROTED    > " + commandSplits[nIter]
    if len(rewrotedCommand) == 0:
        return requestObject, []
    else:
        return requestObject, [rewrotedCommand, ]


def executeSshRequest(cls, requestObject):
    global sshSession
    global sshCurrentSessionName

    try:
        if requestObject["action"] == "connect":
            sshContext = SshContext()
            sshContext.setHost(host=requestObject["host"])
            sshContext.setUser(user=requestObject["user"])
            if "password" in requestObject:
                sshContext.setPassword(password=requestObject["password"])
            if "keyFile" in requestObject:
                keyFileName = requestObject["keyFile"]
                keyFile = open(file=keyFileName, mode='r')
                keyStr = keyFile.read()
                keyFile = io.StringIO(keyStr)
                privateKey = paramiko.RSAKey.from_private_key(keyFile)
                sshContext.setKey(privateKey)
            func = getattr(paramiko, 'Transport')
            transport = func((sshContext.getHost(), sshContext.getPort()))
            transport.connect(
                username=sshContext.getUser(),
                password=sshContext.getPassword(),
                pkey=sshContext.getKey()
            )
            sshHandler = paramiko.SSHClient()
            sshHandler.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            sshHandler._transport = transport
            sshContext.setSshTransport(sshHandler._transport)

            sftpHandler = sshHandler.open_sftp()
            # 如果不使用chdir，则第一次getcwd永远返回的都是None
            sftpHandler.chdir(".")
            sshContext.setSftpHandler(sftpHandler)

            # 备份当前会话的基本信息
            sshSession[sshCurrentSessionName] = sshContext

            yield {
                "type": "result",
                "title": None,
                "rows": None,
                "headers": None,
                "columnTypes": None,
                "status": "SSH connected"
            }
            return
        if requestObject["action"] == "disconnect":
            sshConect = sshSession[sshCurrentSessionName]
            if sshConect.getSshTransport() is not None:
                sshConect.getSshTransport().close()
            if sshConect.getSftpHandler() is not None:
                sshConect.getSftpHandler().close()
            yield {
                "type": "result",
                "title": None,
                "rows": None,
                "headers": None,
                "columnTypes": None,
                "status": "SSH disconnected"
            }
            return
        if requestObject["action"] == "execute":
            command = requestObject["command"]
            # 执行命令
            if sshCurrentSessionName not in sshSession.keys():
                yield {
                    "type": "error",
                    "message": "SSH not connected."
                }
                return
            sshContext = sshSession[sshCurrentSessionName]
            sshEncoding = sshContext.getOption('encoding')
            if sshEncoding is None:
                sshEncoding = cls.testOptions.get('SSH_ENCODING')
            if sshContext.getSshTransport() is not None:
                sshTransport = sshContext.getSshTransport()
                # 打开SSH访问， 合并错误输出到当前输出
                channel = sshTransport.open_session()
                channel.set_combine_stderr(True)

                # 执行远程的命令
                channel.exec_command(command=str(command).encode(encoding=sshEncoding, errors="ignore"))

                consoleOutputBytes = bytes()
                while True:
                    if channel.exit_status_ready():
                        # 程序已经运行结束
                        break
                    else:
                        # 记录收到的标准输出信息
                        while True:
                            if channel.recv_ready():
                                readByte = channel.recv(1)
                                if readByte == bytes('\n', 'ascii'):
                                    yield {
                                        "type": "result",
                                        "title": None,
                                        "rows": None,
                                        "headers": None,
                                        "columnTypes": None,
                                        "status": consoleOutputBytes.decode(encoding=sshEncoding, errors="ignore")
                                    }
                                    consoleOutputBytes = bytes()
                                else:
                                    consoleOutputBytes = consoleOutputBytes + readByte
                            else:
                                break

                    # 避免后台长时作业时CPU过度占用
                    time.sleep(0.5)

                # 要等待最后完成
                while not channel.eof_received:
                    time.sleep(0.5)

                # 可能包含再最后一批的消息里头
                while True:
                    if channel.recv_ready():
                        readByte = channel.recv(1)
                        if readByte == bytes('\n', 'ascii'):
                            yield {
                                "type": "result",
                                "title": None,
                                "rows": None,
                                "headers": None,
                                "columnTypes": None,
                                "status": consoleOutputBytes.decode(encoding=sshEncoding, errors="ignore")
                            }
                            consoleOutputBytes = bytes()
                        else:
                            consoleOutputBytes = consoleOutputBytes + readByte
                    else:
                        break

                # 处理回显的最后一行没有回车换行的情况
                if len(consoleOutputBytes) != 0:
                    yield {
                        "type": "result",
                        "title": None,
                        "rows": None,
                        "headers": None,
                        "columnTypes": None,
                        "status": consoleOutputBytes.decode(encoding=sshEncoding, errors="ignore")
                    }

                # 获得命令的返回状态
                ret = channel.recv_exit_status()
                # 关闭SSH访问
                channel.close()

                yield {
                    "type": "result",
                    "title": None,
                    "rows": None,
                    "headers": None,
                    "columnTypes": None,
                    "status": "< Command finished with [" + str(ret) + "]"
                }
            else:
                yield {
                    "type": "result",
                    "title": None,
                    "rows": None,
                    "headers": None,
                    "columnTypes": None,
                    "status": "SSH not connected."
                }
                return
        if requestObject["action"] == "save":
            sessionName = str(requestObject["sessionName"])
            # 备份当前会话的基本信息
            sshContext = sshSession[sshCurrentSessionName]
            sshSession[sessionName] = sshContext
            yield {
                "type": "result",
                "title": None,
                "rows": None,
                "headers": None,
                "columnTypes": None,
                "status": "SSH session saved."
            }
            return
        if requestObject["action"] == "set":
            if sshCurrentSessionName not in sshSession.keys():
                yield {
                    "type": "error",
                    "message": "SSH not connected."
                }
                return
            if str(requestObject["option"]).lower() == "encoding":
                sshOptions = sshSession[sshCurrentSessionName].getOptions()
                sshOptions.update(
                    {
                        "encoding": requestObject["value"]
                    }
                )
                sshSession[sshCurrentSessionName].setOptions(sshOptions)
            else:
                yield {
                    "type": "error",
                    "message": "Unkonwn ssh option [" + requestObject["option"] + "]."
                }
            return
        if requestObject["action"] == "restore":
            sshCurrentSessionName = str(requestObject["sessionName"])
            yield {
                "type": "result",
                "title": None,
                "rows": None,
                "headers": None,
                "columnTypes": None,
                "status": "SSH session restored."
            }
            return

        if requestObject["action"] == "sftp_cwd":
            if sshCurrentSessionName not in sshSession.keys():
                yield {
                    "type": "error",
                    "message": "SFTP not connected."
                }
                return
            sshContext = sshSession[sshCurrentSessionName]
            sftpHandler = sshContext.getSftpHandler()
            yield {
                "type": "result",
                "title": None,
                "rows": None,
                "headers": None,
                "columnTypes": None,
                "status": str(sftpHandler.getcwd())
            }
            return
        if requestObject["action"] == "sftp_chmod":
            if sshCurrentSessionName not in sshSession.keys():
                yield {
                    "type": "error",
                    "message": "SFTP not connected."
                }
                return
            sshContext = sshSession[sshCurrentSessionName]
            sftpHandler = sshContext.getSftpHandler()
            # chmod的参数为8进制整数，所以这里要转换一下
            sftpHandler.chmod(path=requestObject["fileName"], mode=int(requestObject["fileMod"], 8))
            yield {
                "type": "result",
                "title": None,
                "rows": None,
                "headers": None,
                "columnTypes": None,
                "status": None
            }
            return
        if requestObject["action"] == "sftp_chdir":
            if sshCurrentSessionName not in sshSession.keys():
                yield {
                    "type": "error",
                    "message": "SFTP not connected."
                }
                return
            sshContext = sshSession[sshCurrentSessionName]
            sftpHandler = sshContext.getSftpHandler()
            sftpHandler.chdir(path=requestObject["dir"])
            yield {
                "type": "result",
                "title": None,
                "rows": None,
                "headers": None,
                "columnTypes": None,
                "status": None
            }
            return
        if requestObject["action"] == "sftp_chown":
            if sshCurrentSessionName not in sshSession.keys():
                yield {
                    "type": "error",
                    "message": "SFTP not connected."
                }
                return
            sshContext = sshSession[sshCurrentSessionName]
            sftpHandler = sshContext.getSftpHandler()
            sftpHandler.chown(path=requestObject["fileName"], uid=requestObject["uid"], gid=requestObject["gid"])
            yield {
                "type": "result",
                "title": None,
                "rows": None,
                "headers": None,
                "columnTypes": None,
                "status": None
            }
            return
        if requestObject["action"] == "sftp_mkdir":
            if sshCurrentSessionName not in sshSession.keys():
                yield {
                    "type": "error",
                    "message": "SFTP not connected."
                }
                return
            sshContext = sshSession[sshCurrentSessionName]
            sftpHandler = sshContext.getSftpHandler()
            # mkdir的mode的参数为8进制整数，所以这里要转换一下
            try:
                sftpHandler.mkdir(path=requestObject["dir"], mode=int(requestObject["dirMod"], 8))
            except OSError as oe:
                yield {
                    "type": "error",
                    "message": "mkdir failed. OSError (" + str(oe) + ")"
                }
                return
            yield {
                "type": "result",
                "title": None,
                "rows": None,
                "headers": None,
                "columnTypes": None,
                "status": None
            }
            return
        if requestObject["action"] == "sftp_put":
            if sshCurrentSessionName not in sshSession.keys():
                yield {
                    "type": "error",
                    "message": "SFTP not connected."
                }
                return
            sshContext = sshSession[sshCurrentSessionName]
            sftpHandler = sshContext.getSftpHandler()
            try:
                sftpHandler.put(localpath=requestObject["localFile"],
                                remotepath=requestObject["remoteFile"])
            except OSError as oe:
                yield {
                    "type": "error",
                    "message": "upload failed. OSError(" + str(oe) + ")"
                }
                return
            yield {
                "type": "result",
                "title": None,
                "rows": None,
                "headers": None,
                "columnTypes": None,
                "status": None
            }
            return
        if requestObject["action"] == "sftp_get":
            if sshCurrentSessionName not in sshSession.keys():
                yield {
                    "type": "error",
                    "message": "SFTP not connected."
                }
                return
            sshContext = sshSession[sshCurrentSessionName]
            sftpHandler = sshContext.getSftpHandler()
            try:
                sftpHandler.get(localpath=requestObject["localFile"],
                                remotepath=requestObject["remoteFile"])
            except OSError as oe:
                yield {
                    "type": "error",
                    "message": "download failed. OSError(" + str(oe.filename) + ")"
                }
                return
            yield {
                "type": "result",
                "title": None,
                "rows": None,
                "headers": None,
                "columnTypes": None,
                "status": None
            }
            return
        if requestObject["action"] == "sftp_remove":
            if sshCurrentSessionName not in sshSession.keys():
                yield {
                    "type": "error",
                    "message": "SFTP not connected."
                }
                return
            sshContext = sshSession[sshCurrentSessionName]
            sftpHandler = sshContext.getSftpHandler()
            try:
                sftpHandler.remove(path=requestObject["file"])
            except OSError as oe:
                yield {
                    "type": "error",
                    "message": "remove failed. OSError(" + str(oe.filename) + ")"
                }
                return
            yield {
                "type": "result",
                "title": None,
                "rows": None,
                "headers": None,
                "columnTypes": None,
                "status": None
            }
            return
        if requestObject["action"] == "sftp_rename":
            if sshCurrentSessionName not in sshSession.keys():
                yield {
                    "type": "error",
                    "message": "SFTP not connected."
                }
                return
            sshContext = sshSession[sshCurrentSessionName]
            sftpHandler = sshContext.getSftpHandler()
            try:
                sftpHandler.rename(oldpath=requestObject["oldFile"], newpath=requestObject["newFile"])
            except OSError as oe:
                yield {
                    "type": "error",
                    "message": "rename failed. OSError(" + str(oe.filename) + ")"
                }
                return
            yield {
                "type": "result",
                "title": None,
                "rows": None,
                "headers": None,
                "columnTypes": None,
                "status": None
            }
            return
        if requestObject["action"] == "sftp_listdir":
            if sshCurrentSessionName not in sshSession.keys():
                yield {
                    "type": "error",
                    "message": "SFTP not connected."
                }
                return
            sshContext = sshSession[sshCurrentSessionName]
            sftpHandler = sshContext.getSftpHandler()
            try:
                diritems = sftpHandler.listdir(path=requestObject["dir"])
                result = []
                for diritem in diritems:
                    result.append([diritem, ])
                yield {
                    "type": "result",
                    "title": None,
                    "rows": result,
                    "headers": ["fileName", ],
                    "columnTypes": None,
                    "status": None
                }
            except OSError as oe:
                yield {
                    "type": "error",
                    "message": "listdir failed. OSError(" + str(oe.filename) + ")"
                }
                return
            return
        if requestObject["action"] == "sftp_truncate":
            if sshCurrentSessionName not in sshSession.keys():
                yield {
                    "type": "error",
                    "message": "SFTP not connected."
                }
                return
            sshContext = sshSession[sshCurrentSessionName]
            sftpHandler = sshContext.getSftpHandler()
            try:
                sftpHandler.truncate(path=requestObject["file"], size=requestObject["fileSize"])
                yield {
                    "type": "result",
                    "title": None,
                    "rows": None,
                    "headers": None,
                    "columnTypes": None,
                    "status": None
                }
            except OSError as oe:
                yield {
                    "type": "error",
                    "message": "truncate failed. OSError(" + str(oe.filename) + ")"
                }
                return
            return

    except paramiko.ssh_exception.AuthenticationException:
        yield {
            "type": "error",
            "message": "AuthenticationException failed."
        }
    except Exception as ex:
        import traceback
        print('traceback.print_exc():\n%s' % traceback.print_exc())
        print('traceback.format_exc():\n%s' % traceback.format_exc())

        yield {
            "type": "error",
            "message": "SSH Exception :" + repr(ex)
        }
