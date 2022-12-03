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
        self.sshHandler = None
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

    def setSshHandler(self, sshHandler):
        self.sshHandler = sshHandler

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

    def getSshHandler(self):
        return self.sshHandler

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
        sshContext.setSshHandler(sshHandler)
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
        if sshContext.getSshHandler() is not None:
            sshHandler = sshContext.getSshHandler()
            stdin, stdout, stderr = sshHandler.exec_command(command)
            stdout.channel.set_combine_stderr(True)
            stdin.close()
            consoleOutput = str(stdout.read().decode('UTF-8')).strip()
            yield {
                "type": "result",
                "title": None,
                "rows": None,
                "headers": None,
                "columnTypes": None,
                "status": consoleOutput
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
