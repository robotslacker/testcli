# -*- coding: utf-8 -*-
import queue
import time
import psutil
import threading
import sqlite3
import copy
from queue import Queue

# 默认启动的监控线程数量
defaultWorkerCount = 3

# 默认的监控频度
defaultMonitorFreq = 10

# 所有采集线程
workerThreads = []

# 线程运行标志, 如果为False，则线程中断后续工作，平和退出
threadRunningFlag = False

# 所有需要监控的任务列表
monitorTasks = {}
monitorTaskQueue = Queue()

# 所有的监控结果列表
monitorResults = []

# 当前任务ID序号，总是自增1
currentTaskId = 0


# 任务调度分配, 扫描monitorTasks，把需要进行监控检查的项目放入到
class monitorScheduler(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global monitorTasks
        global monitorTaskQueue

        while True:
            # 如果已经不需要继续运行，则直接退出
            if not threadRunningFlag:
                break
            # 遍历所有列表，如果需要进行性能监控，则将监控任务放入到队列中
            for taskId, monitorTask in monitorTasks.items():
                if monitorTask["status"] in ["SUBMITTED", "STOPPED"]:
                    # 任务已经结束或者尚未启动，不考虑
                    continue
                if monitorTask["last"] is not None:
                    # 判断期限是否已经到达，需要进行下一次采集
                    if "FREQ" not in monitorTask["param"].keys():
                        interVal = defaultMonitorFreq
                    else:
                        interVal = int(monitorTask["param"]["FREQ"])
                    if time.time() <= monitorTask["last"] + int(interVal):
                        # 时间还不到，继续等待
                        continue
                monitorTaskQueue.put(
                    {
                        "param": copy.copy(monitorTask["param"]),
                        "taskId": taskId,
                        "taskName": monitorTask["taskName"],
                    }
                )
                monitorTasks[taskId].update({"last": time.time()})
                if monitorTask["param"]["TAG"] in ["cpu_count", "cpu_count_physical"]:
                    monitorTasks[taskId].update({"status": "STOPPED"})
            time.sleep(3)


# 调度线程
schedulerThread = monitorScheduler()


# 监控数据采集器
class monitorWorker(threading.Thread):
    def __init__(self, threadID, xlogFile):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.runningTasks = []
        self.xlogFileHandle = None
        if xlogFile is not None:
            self.xlogFileHandle = sqlite3.connect(
                database=xlogFile,
                check_same_thread=False,
            )

    def appendTestResult(
            self,
            monitorTime,
            taskId,
            taskName,
            monitorItem,
            monitorValue
    ):
        if self.xlogFileHandle is not None:
            cursor = self.xlogFileHandle.cursor()
            data = (
                monitorTime,
                taskId,
                taskName,
                monitorItem,
                str(monitorValue)
            )
            cursor.execute(
                "Insert Into TestCli_PerfLog(MonitorTime,TaskId,TaskName,MonitorItem,MonitorValue) "
                "Values(?,?,?,?,?)",
                data
            )
            cursor.close()
            self.xlogFileHandle.commit()
            monitorResults.append(
                {
                    "monitorTime": monitorTime,
                    "taskId": taskId,
                    "taskName": taskName,
                    "item": monitorItem,
                    "value": monitorValue
                }
            )

    def run(self):
        global monitorResults
        global monitorTaskQueue

        while True:
            # 如果已经不需要继续运行，则直接退出
            if not threadRunningFlag:
                break

            try:
                task = monitorTaskQueue.get_nowait()
            except queue.Empty:
                # 队列中不存在内容，直接跳过
                time.sleep(3)
                continue

            param = task["param"]
            taskId = task["taskId"]
            taskName = task["taskName"]
            if param["TAG"] == "cpu_count":
                self.appendTestResult(
                    monitorTime=time.time(),
                    taskId=taskId,
                    taskName=taskName,
                    monitorItem="cpu_count",
                    monitorValue={"cpu_count": psutil.cpu_count()}
                )
                continue
            elif param["TAG"] == "cpu_count_physical":
                self.appendTestResult(
                    monitorTime=time.time(),
                    taskId=taskId,
                    taskName=taskName,
                    monitorItem="cpu_count_physical",
                    monitorValue={"cpu_count_physical": psutil.cpu_count(logical=False)}
                )
                continue
            elif param["TAG"] == "cpu_times":
                cpu_times = psutil.cpu_times()
                monitorValue = {
                    "user": cpu_times.user,
                    "system": cpu_times.system,
                    "idle": cpu_times.idle,
                    "interrupt": cpu_times.interrupt,
                    "dpc": cpu_times.dpc
                }
                self.appendTestResult(
                    monitorTime=time.time(),
                    taskId=taskId,
                    taskName=taskName,
                    monitorItem="cpu_time",
                    monitorValue=monitorValue
                )
                continue
            elif param["TAG"] == "cpu_times_percpu":
                cpu_times = psutil.cpu_times(percpu=True)
                monitorValues = []
                for cpu_time in cpu_times:
                    monitorValues.append(
                        {
                            "user": cpu_time.user,
                            "system": cpu_time.system,
                            "idle": cpu_time.idle,
                            "interrupt": cpu_time.interrupt,
                            "dpc": cpu_time.dpc
                        }
                    )
                self.appendTestResult(
                    monitorTime=time.time(),
                    taskId=taskId,
                    taskName=taskName,
                    monitorItem="cpu_times_percpu",
                    monitorValue=monitorValues
                )
                continue

    def addTask(self, task):
        self.runningTasks.append(task)


def stopMonitorManager():
    global threadRunningFlag
    global schedulerThread
    global workerThreads
    global monitorTaskQueue

    # 退出所有工作线程
    threadRunningFlag = False
    for worker in workerThreads:
        if worker.is_alive():
            worker.join(timeout=5)
    # 退出采集线程
    if schedulerThread.is_alive():
        schedulerThread.join(timeout=5)

    # 清空任务队列
    monitorTaskQueue.empty()


def executeMonitorRequest(cls, requestObject):
    global threadRunningFlag
    global monitorTasks
    global workerThreads
    global currentTaskId
    global schedulerThread

    if requestObject["action"] == "startManager":
        # 标记线程运行
        threadRunningFlag = True

        # 启动调度进程
        schedulerThread.start()

        # 启动采集进程
        if requestObject["workerThreads"] is None:
            workerCount = defaultWorkerCount
        else:
            workerCount = int(requestObject["workerThreads"])
        for nPos in range(0, workerCount):
            worker = monitorWorker(nPos, cls.xlogFileFullPath)
            worker.start()
            workerThreads.append(worker)
        yield {
            "type": "result",
            "title": None,
            "rows": None,
            "headers": None,
            "columnTypes": None,
            "status": "Monitor manager has started."
        }
        return
    if requestObject["action"] == "stopManager":
        # 退出所有工作线程
        stopMonitorManager()
        yield {
            "type": "result",
            "title": None,
            "rows": None,
            "headers": None,
            "columnTypes": None,
            "status": "Monitor manager has stopped."
        }
        return
    if requestObject["action"] == "createTask":
        taskLock = threading.Lock()

        # 添加任务列表
        try:
            taskLock.acquire()
            monitorTasks.update(
                {
                    currentTaskId:
                    {
                        "taskName": requestObject["taskName"],
                        "param": requestObject["param"],
                        "status": "SUBMITTED",
                        "worker": None,
                        "last": None,
                    }
                }
            )
            currentTaskId = currentTaskId + 1
        finally:
            taskLock.release()

        yield {
            "type": "result",
            "title": None,
            "rows": None,
            "headers": None,
            "columnTypes": None,
            "status": "Monitor task [" + str(requestObject["taskName"]) + "] has added."
        }
        return
    if requestObject["action"] == "startTask":
        if str(requestObject["taskName"]).upper() == "ALL":
            startedTasks = 0
            for taskId, monitorTask in monitorTasks.items():
                if monitorTask["status"] == "SUBMITTED":
                    monitorTasks[taskId]["status"] = "RUNNING"
                    startedTasks = startedTasks + 1
            yield {
                "type": "result",
                "title": None,
                "rows": None,
                "headers": None,
                "columnTypes": None,
                "status": "Total [" + str(startedTasks) + "] tasks has been started."
            }
            return
        else:
            startedTasks = 0
            taskName = str(requestObject["taskName"])
            for taskId, monitorTask in monitorTasks.items():
                if monitorTask["taskName"] != taskName:
                    continue
                if monitorTask["status"] == "SUBMITTED":
                    monitorTasks[taskId]["status"] = "RUNNING"
                    startedTasks = startedTasks + 1
            yield {
                "type": "result",
                "title": None,
                "rows": None,
                "headers": None,
                "columnTypes": None,
                "status": "Total [" + str(startedTasks) + "] tasks has been started."
            }
            return
    if requestObject["action"] == "stopTask":
        if str(requestObject["taskName"]).upper() == "ALL":
            stoppedTasks = 0
            for taskId, monitorTask in monitorTasks.items():
                if monitorTask["status"] in ["RUNNING", "SUBMITTED"]:
                    monitorTasks[taskId]["status"] = "STOPPED"
                    stoppedTasks = stoppedTasks + 1
            yield {
                "type": "result",
                "title": None,
                "rows": None,
                "headers": None,
                "columnTypes": None,
                "status": "Total [" + str(stoppedTasks) + "] tasks has been stopped."
            }
            return
        else:
            stoppedTasks = 0
            taskName = str(requestObject["taskName"])
            for taskId, monitorTask in monitorTasks.items():
                if monitorTask["taskName"] != taskName:
                    continue
                if monitorTask["status"] in ["RUNNING", "SUBMITTED"]:
                    monitorTasks[taskId]["status"] = "STOPPED"
                    stoppedTasks = stoppedTasks + 1
            yield {
                "type": "result",
                "title": None,
                "rows": None,
                "headers": None,
                "columnTypes": None,
                "status": "Total [" + str(stoppedTasks) + "] tasks has been stopped."
            }
            return
    if requestObject["action"] == "listTask":
        headers = ["taskId", "taskName", "taskParam", "status", "lastActiveTime"]
        rows = []
        for taskId, monitorTask in monitorTasks.items():
            rows.append(
                (
                    taskId,
                    monitorTask["taskName"],
                    monitorTask["param"],
                    monitorTask["status"],
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(monitorTask["last"]))
                )
            )
        if len(rows) == 1:
            status = "Total [" + str(len(rows)) + "] task selected."
        else:
            status = "Total [" + str(len(rows)) + "] tasks selected."
        yield {
            "type": "result",
            "title": None,
            "rows": rows,
            "headers": headers,
            "columnTypes": None,
            "status": status
        }
    if requestObject["action"] == "reportTask":
        if str(requestObject["taskName"]).upper() == "ALL":
            headers = ["timeStamp", "item", "value"]
            rows = []
            for monitorResult in monitorResults:
                row = (
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(monitorResult["monitorTime"])),
                    monitorResult["item"],
                    monitorResult["value"],
                )
                rows.append(row)
            yield {
                "type": "result",
                "title": None,
                "rows": rows,
                "headers": headers,
                "columnTypes": None,
                "status": "Total [" + str(len(rows)) + "] rows are collected."
            }
        else:
            taskName = str(requestObject["taskName"])
            headers = ["timeStamp", "item", "value"]
            rows = []
            for monitorResult in monitorResults:
                if monitorResult["taskName"] != taskName:
                    continue
                row = (
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(monitorResult["monitorTime"])),
                    monitorResult["item"],
                    monitorResult["value"],
                )
                rows.append(row)
            yield {
                "type": "result",
                "title": None,
                "rows": rows,
                "headers": headers,
                "columnTypes": None,
                "status": "Total [" + str(len(rows)) + "] rows are collected."
            }
