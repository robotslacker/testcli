# -*- coding: utf-8 -*-
import queue
import time
import psutil
import threading
import sqlite3
import copy
import re
import sys
from queue import Queue

# 默认启动的监控线程数量
defaultWorkerCount = 3

# 默认的监控频度
defaultMonitorFreq = 30

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
class MonitorScheduler(threading.Thread):
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
                if monitorTask["status"] in ["SUBMITTED", "STOPPED", "FAILED"]:
                    # 任务已经结束或者尚未启动，不考虑
                    continue
                if "TAG" not in monitorTask["param"].keys():
                    # TAG是必须的参数，不可忽略
                    monitorTasks[taskId].update(
                        {
                            "status": "FAILED",
                            "description": "Missed parameter TAG in task description.",
                        })
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
                    # 一次性作业，没有必要重复多次检查
                    monitorTasks[taskId].update(
                        {
                            "status": "STOPPED"
                        }
                    )
            # 每次检查完成后都休息一会，避免CPU过于繁忙
            time.sleep(3)


# 调度线程
schedulerThread = MonitorScheduler()


def bytes2human(n):
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value, s)
    return "%sB" % n


# 监控数据采集器
class MonitorWorker(threading.Thread):
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
        global monitorTasks

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

            param = dict(task["param"])
            taskId = task["taskId"]
            taskName = task["taskName"]
            if param["TAG"] == "cpu_count":
                self.appendTestResult(
                    monitorTime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
                    taskId=taskId,
                    taskName=taskName,
                    monitorItem="cpu_count",
                    monitorValue={"cpu_count": psutil.cpu_count()}
                )
                continue
            elif param["TAG"] == "cpu_count_physical":
                self.appendTestResult(
                    monitorTime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
                    taskId=taskId,
                    taskName=taskName,
                    monitorItem="cpu_count_physical",
                    monitorValue={"cpu_count_physical": psutil.cpu_count(logical=False)}
                )
                continue
            elif param["TAG"] == "cpu_times":
                cpu_times = psutil.cpu_times()
                if 'win32' == str(sys.platform).lower():
                    monitorValue = {
                        "user": cpu_times.user,
                        "system": cpu_times.system,
                        "idle": cpu_times.idle,
                        "interrupt": cpu_times.interrupt,
                        "dpc": cpu_times.dpc,
                    }
                elif 'darwin' == str(sys.platform).lower():
                    monitorValue = {
                        "user": cpu_times.user,
                        "system": cpu_times.system,
                        "idle": cpu_times.idle,
                        "count": cpu_times.count,
                        "index": cpu_times.index,
                        "nice": cpu_times.nice,
                    }
                else:
                    monitorValue = {
                        "user": cpu_times.user,
                        "system": cpu_times.system,
                        "idle": cpu_times.idle,
                        "iowait": cpu_times.iowait,
                        "irq": cpu_times.irq,
                        "softirq": cpu_times.softirq,
                        "steal": cpu_times.steal
                    }
                self.appendTestResult(
                    monitorTime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
                    taskId=taskId,
                    taskName=taskName,
                    monitorItem="cpu_time",
                    monitorValue=monitorValue
                )
                continue
            elif param["TAG"] == "cpu_percent":
                cpu_percent = psutil.cpu_percent()
                monitorValue = {
                    "ratio": cpu_percent,
                }
                self.appendTestResult(
                    monitorTime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
                    taskId=taskId,
                    taskName=taskName,
                    monitorItem="cpu_percent",
                    monitorValue=monitorValue
                )
                continue
            elif param["TAG"] == "memory":
                memoryStatis = psutil.virtual_memory()
                monitorValues = [{
                    "available": bytes2human(memoryStatis.available),
                    "free": bytes2human(memoryStatis.free),
                    "total": bytes2human(memoryStatis.total),
                    "percent": memoryStatis.percent,
                }]
                self.appendTestResult(
                    monitorTime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
                    taskId=taskId,
                    taskName=taskName,
                    monitorItem="memory",
                    monitorValue=monitorValues
                )
            elif param["TAG"] == "network":
                if "NAME" in param.keys():
                    nicFilter = str(param["NAME"])
                    if nicFilter.startswith("'") and nicFilter.endswith("'"):
                        nicFilter = nicFilter[1:-1]
                    elif nicFilter.startswith('"') and nicFilter.endswith('"'):
                        nicFilter = nicFilter[1:-1]
                    networkStatis = dict(psutil.net_io_counters(pernic=True))
                    for nicName in networkStatis.keys():
                        if re.match(pattern=nicFilter, string=nicName, flags=re.IGNORECASE):
                            networkStatis1 = networkStatis[nicName]
                            time.sleep(1)
                            networkStatis = psutil.net_io_counters(pernic=True)
                            networkStatis2 = networkStatis[nicName]
                            monitorValues = [
                                {
                                    "nicName": nicName,
                                    "bytes_sent": bytes2human(networkStatis2.bytes_sent),
                                    "bytes_recv": bytes2human(networkStatis2.bytes_recv),
                                    "errin": bytes2human(networkStatis2.errin),
                                    "errout": bytes2human(networkStatis2.errout),
                                    "dropin": bytes2human(networkStatis2.dropin),
                                    "dropout": bytes2human(networkStatis2.dropout),
                                    "netin": bytes2human(networkStatis2.bytes_recv - networkStatis1.bytes_recv),
                                    "netout": bytes2human(networkStatis2.bytes_sent - networkStatis1.bytes_sent),
                                }
                            ]
                            self.appendTestResult(
                                monitorTime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
                                taskId=taskId,
                                taskName=taskName,
                                monitorItem="network",
                                monitorValue=monitorValues
                            )
                else:
                    networkStatis1 = psutil.net_io_counters()
                    time.sleep(1)
                    networkStatis2 = psutil.net_io_counters()
                    monitorValues = [{
                        "nicName": "GLOBAL",
                        "bytes_sent": bytes2human(networkStatis2.bytes_sent),
                        "bytes_recv": bytes2human(networkStatis2.bytes_recv),
                        "errin": bytes2human(networkStatis2.errin),
                        "errout": bytes2human(networkStatis2.errout),
                        "dropin": bytes2human(networkStatis2.dropin),
                        "dropout": bytes2human(networkStatis2.dropout),
                        "netin": bytes2human(networkStatis2.bytes_recv - networkStatis1.bytes_recv),
                        "netout": bytes2human(networkStatis2.bytes_sent - networkStatis1.bytes_sent),
                    }]
                    self.appendTestResult(
                        monitorTime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
                        taskId=taskId,
                        taskName=taskName,
                        monitorItem="network",
                        monitorValue=monitorValues
                    )
            elif param["TAG"] == "disk":
                if "NAME" in param.keys():
                    diskFilter = param["NAME"]
                    if diskFilter.startswith("'") and diskFilter.endswith("'"):
                        diskFilter = diskFilter[1:-1]
                    elif diskFilter.startswith('"') and diskFilter.endswith('"'):
                        diskFilter = diskFilter[1:-1]
                    diskStatis = dict(psutil.disk_io_counters(perdisk=True))
                    for diskName in diskStatis.keys():
                        if re.match(pattern=diskFilter, string=diskName, flags=re.IGNORECASE):
                            diskStatis1 = diskStatis[diskName]
                            time.sleep(1)
                            diskStatis2 = psutil.disk_io_counters(perdisk=True)[diskName]
                            monitorValues = [{
                                "diskName": diskName,
                                "read_count": diskStatis2.read_count,
                                "write_count": diskStatis2.write_count,
                                "read_bytes": bytes2human(diskStatis2.read_bytes),
                                "write_bytes": bytes2human(diskStatis2.write_bytes),
                                "read_time": str(diskStatis2.read_time) + "ms",
                                "write_time": str(diskStatis2.write_time) + "ms",
                                "read_speed": bytes2human(diskStatis2.read_bytes - diskStatis1.read_bytes) + "/s",
                                "write_speed": bytes2human(diskStatis2.write_bytes - diskStatis1.write_bytes) + "/s",
                            }]
                            self.appendTestResult(
                                monitorTime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
                                taskId=taskId,
                                taskName=taskName,
                                monitorItem="disk",
                                monitorValue=monitorValues
                            )
                else:
                    diskStatis1 = psutil.disk_io_counters()
                    time.sleep(1)
                    diskStatis2 = psutil.disk_io_counters()
                    monitorValues = [{
                        "diskName": "GLOBAL",
                        "read_count": diskStatis2.read_count,
                        "write_count": diskStatis2.write_count,
                        "read_bytes": bytes2human(diskStatis2.read_bytes),
                        "write_bytes": bytes2human(diskStatis2.write_bytes),
                        "read_time": str(diskStatis2.read_time) + "ms",
                        "write_time": str(diskStatis2.write_time) + "ms",
                        "read_speed": bytes2human(diskStatis2.read_bytes - diskStatis1.read_bytes) + "/s",
                        "write_speed": bytes2human(diskStatis2.write_bytes - diskStatis1.write_bytes) + "/s",
                    }]
                    self.appendTestResult(
                        monitorTime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
                        taskId=taskId,
                        taskName=taskName,
                        monitorItem="disk",
                        monitorValue=monitorValues
                    )
            elif param["TAG"] == "process":
                if "NAME" not in param.keys() and "EXE" not in param.keys() and "USERNAME" not in param.keys():
                    taskLock = threading.Lock()
                    # 添加任务列表
                    try:
                        taskLock.acquire()
                        monitorTasks.update(
                            {
                                taskId:
                                    {
                                        "taskName": taskName,
                                        "param": param,
                                        "status": "FAILED",
                                        "worker": None,
                                        "last": None,
                                        "description":
                                            "Missed filter option [USERNAME/NAME/EXE] for process monitor."
                                    }
                            }
                        )
                    finally:
                        taskLock.release()
                    continue
                nameFilter = None
                if "NAME" in param.keys():
                    nameFilter = param["NAME"]
                    if nameFilter.startswith("'") and nameFilter.endswith("'"):
                        nameFilter = nameFilter[1:-1]
                    elif nameFilter.startswith('"') and nameFilter.endswith('"'):
                        nameFilter = nameFilter[1:-1]
                userNameFilter = None
                if "USERNAME" in param.keys():
                    userNameFilter = param["USERNAME"]
                    if userNameFilter.startswith("'") and userNameFilter.endswith("'"):
                        userNameFilter = userNameFilter[1:-1]
                    elif userNameFilter.startswith('"') and userNameFilter.endswith('"'):
                        userNameFilter = userNameFilter[1:-1]
                exeFilter = None
                if "EXE" in param.keys():
                    exeFilter = param["EXE"]
                    if exeFilter.startswith("'") and exeFilter.endswith("'"):
                        exeFilter = exeFilter[1:-1]
                    elif exeFilter.startswith('"') and exeFilter.endswith('"'):
                        exeFilter = exeFilter[1:-1]
                for proc in psutil.process_iter(
                        ["username", "name", "exe",
                         "cmdline", "status", "num_threads",
                         "create_time", "cpu_percent",
                         "memory_info", "memory_percent"]
                ):
                    # 性能问题说明：
                    # 1. 只读取非常必要的列，不获取额外的列信息
                    # 2. 每次获取后都采用快照方式，不要直接去读取
                    with proc.oneshot():
                        try:
                            username = proc.username()
                        except psutil.AccessDenied:
                            username = "AccessDenied."
                        if userNameFilter is not None:
                            if not re.match(pattern=userNameFilter, string=username, flags=re.IGNORECASE):
                                continue
                        if nameFilter is not None:
                            if not re.match(pattern=nameFilter, string=proc.name(), flags=re.IGNORECASE):
                                continue
                        try:
                            exe = proc.exe()
                        except psutil.AccessDenied:
                            exe = "AccessDenied."
                        if exeFilter is not None:
                            if not re.match(pattern=exeFilter, string=exe, flags=re.IGNORECASE):
                                continue
                        try:
                            cmdLine = proc.cmdline()
                        except psutil.AccessDenied:
                            cmdLine = "AccessDenied."
                        try:
                            files = len(proc.open_files())
                        except psutil.AccessDenied:
                            files = 0
                        monitorValues = [{
                            "pid": proc.pid,
                            "username": username,
                            "name": proc.name(),
                            "cmdline": cmdLine,
                            "status": proc.status(),
                            "threads": proc.num_threads(),
                            "files": files,
                            "exec": exe,
                            "create_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(proc.create_time())),
                            "cpu_percent": proc.cpu_percent(),
                            "cpu_times_user": proc.cpu_times().user,
                            "cpu_times_sys": proc.cpu_times().system,
                            "mem_rss": bytes2human(proc.memory_info().rss),
                            "mem_vms": bytes2human(proc.memory_info().vms),
                            "mem_percent": proc.memory_percent(),
                        }]
                        self.appendTestResult(
                            monitorTime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
                            taskId=taskId,
                            taskName=taskName,
                            monitorItem="process",
                            monitorValue=monitorValues
                        )
            else:
                taskLock = threading.Lock()
                # 添加任务列表
                try:
                    taskLock.acquire()
                    monitorTasks.update(
                        {
                            taskId:
                                {
                                    "taskName": taskName,
                                    "param": param,
                                    "status": "FAILED",
                                    "worker": None,
                                    "last": None,
                                    "description": "Invalid TAG " + param["TAG"] + " in task description."
                                }
                        }
                    )
                finally:
                    taskLock.release()
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
        # 设置程序运行选项
        cls.testOptions.set("MONITORMANAGER", "ON")

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
            worker = MonitorWorker(nPos, cls.xlogFileFullPath)
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
        # 设置程序运行选项
        cls.testOptions.set("MONITORMANAGER", "OFF")

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
                        "description": None
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
        headers = ["taskId", "taskName", "taskParam", "status", "lastActiveTime", "description"]
        rows = []
        for taskId, monitorTask in monitorTasks.items():
            rows.append(
                (
                    taskId,
                    monitorTask["taskName"],
                    monitorTask["param"],
                    monitorTask["status"],
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(monitorTask["last"])),
                    monitorTask["description"],
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
                    monitorResult["monitorTime"],
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
