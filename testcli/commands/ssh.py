# -*- coding: utf-8 -*-
import paramiko
import io

sshSession = {}
sshCurrentSessionName = "NONAME"


class SshContext:
    def __init__(self):
        self.host = ""
        self.port = 22
        self.user = ""
        self.pwd = None
        self.key = None
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


def executeSshRequest(cls, requestObject):
    global sshSession
    global sshCurrentSessionName

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

        sftpHandler = paramiko.SFTPClient.from_transport(transport)
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
        if sshConect.getSshHandler() is not None:
            sshConect.getSshHandler().close()
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
        sshContext = sshSession[sshCurrentSessionName]
        if sshContext.getSshTransport() is not None:
            sshTransport = sshContext.getSshTransport()
            # 打开SSH访问
            channel = sshTransport.open_session()
            channel.set_combine_stderr(True)
            # 执行远程的命令
            channel.exec_command(command)
            consoleOutputBytes = bytes()
            while True:
                if channel.exit_status_ready():
                    # 程序已经运行结束
                    break
                else:
                    # 记录收到的屏幕信息
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
                                    "status": consoleOutputBytes.decode(encoding='utf-8')
                                }
                                consoleOutputBytes = bytes()
                            else:
                                consoleOutputBytes = consoleOutputBytes + readByte
                        else:
                            break
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
                            "status": consoleOutputBytes.decode(encoding='utf-8')
                        }
                        consoleOutputBytes = bytes()
                    else:
                        consoleOutputBytes = consoleOutputBytes + readByte
                else:
                    break
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
