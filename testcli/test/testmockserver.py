# -*- coding: utf-8 -*-
import time

import uvicorn
import urllib3
from fastapi import FastAPI, UploadFile, File
from multiprocessing import Process
from typing import Any, Dict

# 进程和端口信息
appHost = "127.0.0.1"
appPort = 8000

# 全局进程信息（即mockApp的信息）
proc = None

# 创建fastapi对象
mockApp = FastAPI()


def runServer():
    """
    This function to run configured uvicorn server.
    """
    uvicorn.run(
        app=mockApp,
        host=appHost,
        port=appPort,
        log_level="critical"
    )


def startServer():
    """
    This function to start a new process (start the server).
    """
    global proc
    # create process instance and set the target to run function.
    # use daemon mode to stop the process whenever the program stopped.
    proc = Process(target=runServer, args=(), daemon=True)
    proc.start()


def stopServer():
    """
    This function to join (stop) the process (stop the server).
    """
    global proc
    if proc:
        # join (stop) the process with a timeout setten to 0.25 seconds.
        # using timeout (the optional arg) is too important in order to
        # enforce the server to stop.
        join = getattr(proc, "join")
        join(0.25)


def waitServerRunning():
    httpHandler = urllib3.PoolManager()
    healthURL = "http://" + str(appHost) + ":" + str(appPort) + "/health"
    while True:
        try:
            ret = httpHandler.request(
                method="GET",
                url=healthURL,
                retries=False,
                timeout=2.0,
            )
            data = ret.data.decode('utf-8')
            if data == "{\"status\":\"OK\"}":
                break
        except urllib3.exceptions.TimeoutError:
            # 没有链接上，等待2秒钟后再试
            time.sleep(2)
            pass


@mockApp.post('/fileUpload')
def fileUpload(my_file: UploadFile = File(...)):
    print(my_file)
    return {"status": "OK"}


@mockApp.get('/jsonfiltertest')
def health():
    return {
        "data1": "data1XXXX",
        "data2": "data2XXXX",
        "data3": "data3XXXX",
        "data4": {
            "subdata4": "subdata4XXX"
        },
        "data5": [{"data51": {"subdata51": "subdata51XXX"}}, {"data51": {"subdata52": "subdata52XXX"}}]
    }


@mockApp.get('/timeoutTest')
def timeoutTest():
    # 休息10秒后再回应
    time.sleep(10)
    return {"status": "OK"}


@mockApp.get('/health')
def health():
    return {"status": "OK"}


@mockApp.post('/echo')
def echo(request: Dict[Any, Any]):
    return request


# 主程序
if __name__ == '__main__':
    startServer()
    waitServerRunning()
    time.sleep(3600)
