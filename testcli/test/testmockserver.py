# -*- coding: utf-8 -*-
import uvicorn
from fastapi import FastAPI
from multiprocessing import Process

# 全局进程信息（即mockApp的信息）
proc = None

# 创建fastapi对象
mockApp = FastAPI()


def runMockServer():
    """
    This function to run configured uvicorn server.
    """
    uvicorn.run(app=mockApp, host="127.0.0.1", port=8000)


def startMockServer():
    """
    This function to start a new process (start the server).
    """
    global proc
    # create process instance and set the target to run function.
    # use daemon mode to stop the process whenever the program stopped.
    proc = Process(target=runMockServer, args=(), daemon=True)
    proc.start()


def stopMockServer():
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


@mockApp.get('/')
def home():
    return {"message": "Hello World"}


# 主程序
if __name__ == '__main__':
    uvicorn.run(mockApp, host="127.0.0.1", port=8000)
