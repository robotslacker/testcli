# -*- coding: utf-8 -*-
import multiprocessing
import threading
import time
import os
import datetime
import copy
from multiprocessing import Lock
import traceback

import click
import jpype
import socket
from .testcliexception import TestCliException
from .sqlclijdbc import connect as jdbcconnect


# 并发作业处理
'''
    通过JobManager来完成并发作业控制
    
    程序通过多进程的方式来实现并发操作，每一个并发度都是一个单独的进程，利用Python的MultiProcess来处理。
    
'''


# TestCli的Meta管理，使用H2数据库作为管理方式
class TestCliMeta(object):
    def __init__(self):
        self.JobManagerEnabled = False
        self.dbConn = None
        self.MetaServer = None
        self.MetaURL = None
        self.MetaPort = 0
        self.JarList = None
        self.appOptions = None
        self.agentErrorMessage = None

    def setJVMJarList(self, p_JarList):
        self.JarList = p_JarList

    def setAppOptions(self, appOptions):
        self.appOptions = appOptions

    def DisConnect(self):
        if self.dbConn is not None:
            self.dbConn.close()

    def ShutdownServer(self):
        if self.MetaServer is not None:
            # 先停止数据库连接
            if self.dbConn is not None:
                self.dbConn.close()
            # 再停止数据库服务
            try:
                self.MetaServer.stop()
                self.MetaServer.shutdown()
            except Exception:
                if "TESTCLI_DEBUG" in os.environ:
                    print('traceback.print_exc():\n%s' % traceback.print_exc())
                    print('traceback.format_exc():\n%s' % traceback.format_exc())
            self.MetaServer = None

    def StartAsServer(self):
        try:
            # 读取配置文件，并连接数据库
            m_MetaClass = self.appOptions.get("meta_driver", "driver")
            m_MetaDriverURL = self.appOptions.get("meta_driver", "jdbcurl")
            self.dbConn = jdbcconnect(jclassname=m_MetaClass, url=m_MetaDriverURL,
                                      driverArgs={'user': 'sa', 'password': 'sa'},
                                      jars=self.JarList)
            if self.dbConn is None:
                raise TestCliException("TestCli-0000: "
                                       "TestCliMeta:: Connect to meta failed! JobManager Aborted!")
            # 设置AutoCommit为False
            self.dbConn.setAutoCommit(False)

            # 获得一个可用的端口
            if "TESTCLI_METAPORT" in os.environ:
                self.MetaPort = int(os.environ["TESTCLI_METAPORT"])
            else:
                m_PortFileLocker = Lock()
                m_PortFileLocker.acquire()
                self.MetaPort = 0
                try:
                    sock = socket.socket()
                    sock.bind(('', 0))
                    self.MetaPort = sock.getsockname()[1]
                    sock.close()
                except Exception:
                    if "TESTCLI_DEBUG" in os.environ:
                        print('traceback.print_exc():\n%s' % traceback.print_exc())
                        print('traceback.format_exc():\n%s' % traceback.format_exc())
                    self.MetaPort = 0
                m_PortFileLocker.release()
                if self.MetaPort == 0:
                    raise TestCliException("TestCli-0000: "
                                           "TestCliMeta:: Can't get avalable port! JobManager Aborted!")

            # 启动一个TCP Server，用来给其他后续的H2连接（主要是子进程）
            # 端口号为随机获得，或者利用固定的参数
            self.MetaServer = jpype.JClass("org.h2.tools.Server").\
                createTcpServer("-tcp", "-tcpAllowOthers", "-tcpPort", str(self.MetaPort))
            self.MetaServer.start()
            self.MetaURL = "tcp://127.0.0.1:" + str(self.MetaPort)

            # 初始化Meta数据库表
            m_db_cursor = self.dbConn.cursor()

            m_SQL = "Create Table IF Not Exists TESTCLI_ServerInfo\n" \
                    "(\n" \
                    "    ProcessID       Integer,\n" \
                    "    ParentProcessID Integer,\n" \
                    "    ProcessPath     VARCHAR(500),\n" \
                    "    StartTime       TimeStamp,\n" \
                    "    EndTime         TimeStamp\n" \
                    ")"
            m_db_cursor.execute(m_SQL)
            m_SQL = "CREATE TABLE IF Not Exists TESTCLI_JOBS\n" \
                    "(\n" \
                    "    JOB_ID                     Integer,\n" \
                    "    JOB_Name                   VARCHAR(500),\n" \
                    "    JOB_TAG                    VARCHAR(500),\n" \
                    "    Starter_Interval           Integer,\n" \
                    "    Starter_Last_Active_Time   TimeStamp,\n" \
                    "    Parallel                   Integer,\n" \
                    "    Loop                       Integer,\n" \
                    "    Started_JOBS               Integer,\n" \
                    "    Failed_JOBS                Integer,\n" \
                    "    Finished_JOBS              Integer,\n" \
                    "    Active_JOBS                Integer,\n" \
                    "    Error_Message              VARCHAR(500),\n" \
                    "    Script                     VARCHAR(500),\n" \
                    "    Script_FullName            VARCHAR(500),\n" \
                    "    Think_Time                 Integer,\n" \
                    "    Timeout                    Integer,\n" \
                    "    Submit_Time                TimeStamp,\n" \
                    "    Start_Time                 TimeStamp,\n" \
                    "    End_Time                   TimeStamp,\n" \
                    "    Blowout_Threshold_Count    Integer,\n" \
                    "    Status                     VARCHAR(500)\n" \
                    ")"
            m_db_cursor.execute(m_SQL)
            m_SQL = "CREATE INDEX Idx_TESTCLI_JOBS_ID On TESTCLI_JOBS(JOB_ID)"
            m_db_cursor.execute(m_SQL)
            m_SQL = "CREATE INDEX Idx_TESTCLI_JOBS_TAG On TESTCLI_JOBS(JOB_TAG)"
            m_db_cursor.execute(m_SQL)

            m_SQL = "CREATE TABLE IF Not Exists TESTCLI_WORKERS\n" \
                    "(\n" \
                    "    JOB_ID                     Integer,\n" \
                    "    JOB_Name                   VARCHAR(500),\n" \
                    "    JOB_TAG                    VARCHAR(500),\n" \
                    "    WorkerHandler_ID           Integer,\n" \
                    "    ProcessID                  Integer,\n" \
                    "    start_time                 BIGINT,\n" \
                    "    end_time                   BIGINT,\n" \
                    "    exit_code                  Integer,\n" \
                    "    Finished_Status            VARCHAR(500),\n" \
                    "    Timer_Point                VARCHAR(500)\n" \
                    ")"
            m_db_cursor.execute(m_SQL)
            m_SQL = "CREATE INDEX Idx_TESTCLI_WORKERS_ID On TESTCLI_WORKERS(JOB_ID)"
            m_db_cursor.execute(m_SQL)
            m_SQL = "CREATE INDEX Idx_TESTCLI_WORKERS_TAG On TESTCLI_WORKERS(JOB_TAG)"
            m_db_cursor.execute(m_SQL)
            m_SQL = "CREATE INDEX Idx_TESTCLI_WORKERS_Process On TESTCLI_WORKERS(ProcessID)"
            m_db_cursor.execute(m_SQL)
            m_SQL = "CREATE INDEX Idx_TESTCLI_WORKERS_Name On TESTCLI_WORKERS(JOB_Name)"
            m_db_cursor.execute(m_SQL)

            m_SQL = "CREATE TABLE IF Not Exists TESTCLI_WORKERS_HISTORY\n" \
                    "(\n" \
                    "    JOB_ID                     Integer,\n" \
                    "    JOB_Name                   VARCHAR(500),\n" \
                    "    JOB_TAG                    VARCHAR(500),\n" \
                    "    WorkerHandler_ID           Integer,\n" \
                    "    ProcessID                  Integer,\n" \
                    "    start_time                 BIGINT,\n" \
                    "    end_time                   BIGINT,\n" \
                    "    exit_code                  Integer,\n" \
                    "    Finished_Status            VARCHAR(500),\n" \
                    "    Timer_Point                VARCHAR(500)\n" \
                    ")"
            m_db_cursor.execute(m_SQL)
            m_db_cursor.close()

            m_ProcessID = os.getpid()
            m_ParentProcessID = os.getppid()
            m_ProcessPath = os.path.dirname(__file__)
            m_SQL = "Insert Into TESTCLI_ServerInfo(ProcessID, ParentProcessID, ProcessPath, StartTime)" \
                    "Values(" + str(m_ProcessID) + "," + str(m_ParentProcessID) + \
                    ",'" + str(m_ProcessPath) + "', CURRENT_TIMESTAMP())"
            m_db_cursor = self.dbConn.cursor()
            m_db_cursor.execute(m_SQL)
            m_db_cursor.close()
            self.dbConn.commit()

            # 任务调度管理只有在Meta能够成功连接的情况下才可以使用
            self.JobManagerEnabled = False
        except TestCliException as se:
            raise se
        except Exception as e:
            if "TESTCLI_DEBUG" in os.environ:
                print('traceback.print_exc():\n%s' % traceback.print_exc())
                print('traceback.format_exc():\n%s' % traceback.format_exc())
            raise TestCliException("TestCli-0000: "
                                   "TestCliMeta:: " + str(e) + " JobManager Aborted!")

    def ConnectServer(self, p_MetaServerURL):
        if p_MetaServerURL is None:
            # 如果没有Meta的连接信息，直接退出
            return

        try:
            # 读取配置文件，并连接数据库
            m_MetaClass = self.appOptions.get("meta_driver", "driver")
            m_MetaDriverURL = self.appOptions.get("meta_driver", "jdbcurl")
            m_MetaDriverURL = m_MetaDriverURL.replace("mem", p_MetaServerURL + "/mem")
            self.dbConn = jdbcconnect(jclassname=m_MetaClass, url=m_MetaDriverURL,
                                      driverArgs={'user': 'sa', 'password': 'sa'},
                                      jars=self.JarList)
            if self.dbConn is None:
                if "TESTCLI_DEBUG" in os.environ:
                    print("DEBUG:: TestCliMeta:: Connect to meta failed! JobManager Connect Failed!")
                return

            # 设置AutoCommit为False
            self.dbConn.setAutoCommit(False)
        except Exception:
            if "TESTCLI_DEBUG" in os.environ:
                print('traceback.print_exc():\n%s' % traceback.print_exc())
                print('traceback.format_exc():\n%s' % traceback.format_exc())

    def DisConnectServer(self):
        if self.dbConn:
            self.dbConn.close()


# 工作进程信息
class Workers:
    def __init__(self):
        self.WorkerHandler_ID = 0      # 任务处理器编号，范围是1-parallel
        self.ProcessID = 0             # 进程信息，这里存放的是进程PID，如果没有进程存在，这里是0
        self.start_time = None         # 进程开始时间，这里存放的是UnixTimeStamp
        self.end_time = None           # 进程结束时间，这里存放的是UnixTimeStamp
        self.exit_code = 0             # 进程退出状态
        self.Finished_Status = ""      # 进程结束状态，有FINISHED, ABORTED, SHUTDOWN,
        self.Timer_Point = []          # 进程当前已经到达的聚合点


# 任务信息
class JOB:
    def __init__(self):
        self.id = 0
        self.job_name = ""

        # 进程启动的时候会利用starter的机制，即每次只启动部分进程数量，不断累积达到最高峰
        # 在进程数量已经达到最大并发数后，不再有这个限制，剩下的进程只要有空闲就会启动
        self.starter_interval = 0                 # starter 每次启动的时间间隔
        self.starter_last_active_time = None      # starter 最后启动脚本的时间，unix的时间戳
        self.parallel = 1                         # 程序并发度

        self.loop = 1                             # 需要循环的次数
        self.failed_jobs = 0                      # 已经失败的次数
        self.finished_jobs = 0                    # 已经完成的次数
        self.started_jobs = 0                     # 已经启动的次数
        self.active_jobs = 0                      # 当前活动的JOB数量

        self.error_message = None                 # 错误失败原因

        self.script = None                        # JOB计划执行的脚本
        self.script_fullname = None               # JOB计划执行的脚本全路径
        self.tag = None                           # JOB的标识，同一个TAG下保持相同的聚合点规则
        self.think_time = 0
        self.timeout = 0                          # 超时的秒数限制，0表示不限制
        self.submit_time = None
        self.start_time = None
        self.end_time = None
        self.blowout_threshold_count = 0          # 完全失败阈值，若达到该阈值，认为后续继续测试没有意义。0表示不做限制
        self.status = "Submitted"
        self.workers = {}                           # 当前任务的具体进程信息, WorkerHandler_ID, Worker
        self.transactionstaistics = []            # 当前JOB的transaction统计信息
        self.transactionhistory = []              # 当前JOB的transaction的历史信息

    # 返回JOB的编号信息
    def getJobID(self):
        return self.id

    # 设置JOBID
    def setJobID(self, p_nJobID):
        self.id = p_nJobID

    # 返回JOB的编号信息
    def getJobName(self):
        return self.job_name

    # 设置JOBID
    def setJobName(self, jobName):
        self.job_name = jobName

    # 返回任务提交的时间
    def getSubmitTime(self):
        return self.submit_time

    # 设置提交时间
    def setSubmitTime(self, p_szTime):
        self.submit_time = p_szTime

    # 返回进程当前的状态
    def getStatus(self):
        return self.status

    # 设置进程当前的状态
    def setStatus(self, p_Status: str):
        self.status = p_Status

    # 设置当前正在运行的JOB数量
    def setActiveJobs(self, p_active_jobs: int):
        self.active_jobs = p_active_jobs

    # 返回当前正在运行的JOB数量
    def getActiveJobs(self):
        return self.active_jobs

    # 返回当前已经失败的JOB数量
    def setFailedJobs(self, p_FailedJobs):
        self.failed_jobs = p_FailedJobs

    # 返回当前已经失败的JOB数量
    def getFailedJobs(self):
        return self.failed_jobs

    # 设置已经完成的JOB数量
    def setStartedJobs(self, p_StartedJobs):
        self.started_jobs = p_StartedJobs

    # 返回已经完成的JOB数量
    def getStartedJobs(self):
        return self.started_jobs

    # 设置已经完成的JOB数量
    def setFinishedJobs(self, p_FinishedJobs):
        self.finished_jobs = p_FinishedJobs

    # 返回已经完成的JOB数量
    def getFinishedJobs(self):
        return self.finished_jobs

    # 设置任务开始的时间
    def setStartTime(self, p_Start_Time):
        self.start_time = p_Start_Time

    # 返回任务开始的时间
    def getStartTime(self):
        return self.start_time

    # 设置任务结束的时间
    def setEndTime(self, p_End_Time):
        self.end_time = p_End_Time

    # 返回任务结束的时间
    def getEndTime(self):
        return self.end_time

    # 设置任务的并发程度
    def setParallel(self, p_Parallel):
        self.parallel = p_Parallel

    # 返回任务的并发程度
    def getParallel(self):
        return self.parallel

    # 设置任务的循环次数
    def setLoop(self, p_Loop):
        self.loop = p_Loop

    # 返回任务的循环次数
    def getLoop(self):
        return self.loop

    # 设置并发作业启动时每次启动间隔时间
    def setStarterInterval(self, p_StarterInterval):
        self.starter_interval = p_StarterInterval

    # 返回并发作业启动时每次启动间隔时间
    # 默认0，即不间隔
    def getStarterInterval(self):
        return self.starter_interval

    # 设置上一次Starter工作的时间
    def setStarterLastActiveTime(self, p_LastActiveTime):
        self.starter_last_active_time = p_LastActiveTime

    # 返回上一次Starter工作的时间
    def getStarterLastActiveTime(self):
        return self.starter_last_active_time

    # 设置正在执行的脚本名称
    def setScript(self, p_Script):
        self.script = p_Script

    # 返回正在执行的脚本名称
    def getScript(self):
        return self.script

    # 设置正在执行的脚本名称
    def setErrorMessage(self, p_ErrorMessage):
        self.error_message = p_ErrorMessage

    # 返回正在执行的脚本名称
    def getErrorMessage(self):
        return self.error_message

    # 设置正在执行的脚本文件全路径
    def setScriptFullName(self, p_ScriptFullName):
        self.script_fullname = p_ScriptFullName

    # 返回正在执行的脚本文件全路径
    def getScriptFullName(self):
        return self.script_fullname

    # 设置JOB每次Worker之间的考虑时间，即think_time
    def setThinkTime(self, p_ThinkTime):
        self.think_time = p_ThinkTime

    # 返回JOB每次Worker之间的考虑时间，即think_time
    def getThinkTime(self):
        return self.think_time

    # 设置JOB的超时时间
    def setTimeOut(self, p_TimeOut):
        self.timeout = p_TimeOut

    # 返回JOB的超时时间
    def getTimeOut(self):
        return self.timeout

    # 设置Blowout失败的数量阈值
    def setBlowoutThresHoldCount(self, p_BlowoutThresHoldCount):
        self.blowout_threshold_count = p_BlowoutThresHoldCount

    # 返回Blowout失败的数量阈值
    def getBlowoutThresHoldCount(self):
        return self.blowout_threshold_count

    # 设置JOB的标签
    def setTag(self, p_tag):
        self.tag = p_tag

    # 返回JOB的标签
    def getTag(self):
        return self.tag

    # 根据参数设置JOB的相关参数
    def setjob(self, p_ParameterName: str, p_ParameterValue: str):
        if p_ParameterName.strip().lower() == "parallel":
            self.setParallel(int(p_ParameterValue))
        elif p_ParameterName.strip().lower() == "starter_interval":
            self.setStarterInterval(int(p_ParameterValue))
        elif p_ParameterName.strip().lower() == "loop":
            self.setLoop(int(p_ParameterValue))
        elif p_ParameterName.strip().lower() == "script":
            self.setScript(p_ParameterValue)
        elif p_ParameterName.strip().lower() == "think_time":
            self.setThinkTime(int(p_ParameterValue))
        elif p_ParameterName.strip().lower() == "timeout":
            self.setTimeOut(int(p_ParameterValue))
        elif p_ParameterName.strip().lower() == "blowout_threshold_count":
            self.setBlowoutThresHoldCount(int(p_ParameterValue))
        elif p_ParameterName.strip().lower() == "tag":
            self.setTag(p_ParameterValue)
        else:
            raise TestCliException("Invalid JOB Parameter name. [" + str(p_ParameterName) + "]")

    # 返回所有JOB的任务列表
    def getWorkers(self):
        return self.workers.values()

    # 根据进程ID信息返回当前的Worker信息
    def getWorkerByProcessID(self, p_nProcessID):
        for worker in self.workers.values():
            if worker.ProcessID == p_nProcessID:
                return worker
        return None

    # 设置Worker信息
    def setWorker(self, p_Worker: Workers):
        if p_Worker.WorkerHandler_ID in self.workers.keys():
            self.workers[p_Worker.WorkerHandler_ID].start_time = p_Worker.start_time
            self.workers[p_Worker.WorkerHandler_ID].end_time = p_Worker.end_time
            self.workers[p_Worker.WorkerHandler_ID].exit_code = p_Worker.exit_code
            self.workers[p_Worker.WorkerHandler_ID].ProcessID = p_Worker.ProcessID
            self.workers[p_Worker.WorkerHandler_ID].Finished_Status = p_Worker.Finished_Status
            self.workers[p_Worker.WorkerHandler_ID].Timer_Point = p_Worker.Timer_Point
        else:
            m_Worker = Workers()
            m_Worker.WorkerHandler_ID = p_Worker.WorkerHandler_ID
            m_Worker.start_time = p_Worker.start_time
            m_Worker.end_time = p_Worker.end_time
            m_Worker.exit_code = p_Worker.exit_code
            m_Worker.ProcessID = p_Worker.ProcessID
            m_Worker.Finished_Status = p_Worker.Finished_Status
            m_Worker.Timer_Point = p_Worker.Timer_Point
            self.workers[p_Worker.WorkerHandler_ID] = copy.copy(m_Worker)

    # 启动作业
    # 返回一个包含WorkerHandlerID的列表
    def getWorkerStarter(self):
        currenttime = int(time.mktime(datetime.datetime.now().timetuple()))
        idleWorkerHandlerList = []
        if self.active_jobs >= self.parallel:
            # 如果当前活动进程数量已经超过了并发要求，直接退出
            return []
        if self.started_jobs >= self.loop * self.parallel:
            # 如果到目前位置，已经启动的进程数量超过了总数要求，直接退出
            return []
        if self.starter_interval != 0 and self.started_jobs < self.parallel:
            # 如果上一个批次启动时间到现在还不到限制时间要求，则不再启动
            if self.starter_last_active_time + self.starter_interval > currenttime:
                # 还不到可以启动进程的时间, 返回空列表
                return []

        # 循环判断每个JOB信息，考虑think_time以及starter_interval
        for nPos in range(0, self.parallel):
            if nPos in self.workers.keys():
                # 该Worker对应的相关信息已经存在
                if self.workers[nPos].ProcessID == 0:
                    # 进程处于空闲状态
                    if self.think_time != 0:
                        if self.workers[nPos].end_time + self.think_time > currenttime:
                            # 还不满足ThinkTime的限制要求，跳过
                            continue
                    if len(idleWorkerHandlerList) >= (self.parallel - self.active_jobs):
                        # 如果已经要启动的进程已经满足最大进程数限制，则不再考虑新进程
                        break
                    else:
                        idleWorkerHandlerList.append(nPos)
                else:
                    # 进程当前不空闲
                    continue
            else:
                # 不存在该Worker信息, 不需要考虑thinktime, 可以启动
                if len(idleWorkerHandlerList) >= (self.parallel - self.active_jobs):
                    # 如果已经要启动的进程已经满足最大进程数限制，则不再考虑新进程
                    break
                else:
                    idleWorkerHandlerList.append(nPos)
        # 更新批次启动时间的时间
        if self.starter_interval != 0:
            self.starter_last_active_time = currenttime
        return idleWorkerHandlerList

    # 启动作业任务
    def StartWorker(self, p_MetaConn, p_WorkerHandlerID: int, p_ProcessID: int):
        m_CurrentTime = int(time.mktime(datetime.datetime.now().timetuple()))

        m_Worker = Workers()
        m_Worker.ProcessID = p_ProcessID
        m_Worker.start_time = m_CurrentTime
        m_Worker.end_time = None
        self.workers[p_WorkerHandlerID] = m_Worker
        # 在SQLCLI_WORKER中创建对应记录
        m_db_cursor = p_MetaConn.cursor()
        m_SQL = "Insert into TESTCLI_WORKERS(" \
                "JOB_ID,JOB_Name, JOB_Tag, WorkerHandler_ID,ProcessID, Start_Time) " \
                "VALUES(?,?,?,?,?,?)"
        m_Data = [
            self.id,
            self.job_name,
            self.tag,
            p_WorkerHandlerID,
            p_ProcessID,
            m_CurrentTime
        ]
        m_db_cursor.execute(m_SQL, parameters=m_Data)
        m_db_cursor.close()
        p_MetaConn.commit()

    # 完成当前任务
    def FinishWorker(self, p_MetaConn, p_WorkerHandlerID, p_Worker_ExitCode: int, p_Worker_FinishedStatus: str):
        m_CurrentTime = int(time.mktime(datetime.datetime.now().timetuple()))
        # 清空当前Worker的结构信息
        self.workers[p_WorkerHandlerID].start_time = None
        self.workers[p_WorkerHandlerID].exit_code = 0
        self.workers[p_WorkerHandlerID].ProcessID = 0
        self.workers[p_WorkerHandlerID].Finished_Status = ""

        # Worker已经超时退出
        if p_Worker_ExitCode is None:
            p_Worker_ExitCode = -1

        # 在数据库中记录相关信息
        m_db_cursor = p_MetaConn.cursor()
        m_SQL = "Insert Into TESTCLI_WORKERS_HISTORY(JOB_ID,JOB_Name,JOB_TAG," \
                "       WorkerHandler_ID,ProcessID,Timer_Point," \
                "       Start_Time,End_Time,Exit_Code,Finished_Status) " \
                "SELECT JOB_ID,JOB_Name,JOB_TAG,WorkerHandler_ID,ProcessID,Timer_Point,Start_Time," + \
                str(m_CurrentTime) + "," + str(p_Worker_ExitCode) + ",'" + \
                p_Worker_FinishedStatus + "' " + \
                "FROM   TESTCLI_WORKERS " \
                "WHERE  JOB_ID=" + str(self.id) + " " + \
                "AND    WorkerHandler_ID=" + str(p_WorkerHandlerID)
        m_db_cursor.execute(m_SQL)
        # 归零TESTCLI_WORKERS中的信息
        m_SQL = "DELETE TESTCLI_WORKERS " + \
                "WHERE  JOB_ID=" + str(self.id) + " " + \
                "AND    WorkerHandler_ID=" + str(p_WorkerHandlerID)
        m_db_cursor.execute(m_SQL)
        m_db_cursor.close()
        p_MetaConn.commit()


# JOB任务的管理
class JOBManager(object):
    def __init__(self):
        # 进程管理的相关上下文信息
        # 来自于父进程，当子进程不进行特殊设置的时候，进程管理中用到的信息将集成父进程
        self.ProcessContextInfo = {}

        # 进程句柄信息
        self.processHandlerInfo = {}

        # 当前清理进程的状态, NOT-STARTED, RUNNING, WAITINGFOR_STOP, STOPPED
        # 如果WorkerStatus==WAITINGFOR_STOP 则Worker主动停止
        self.WorkerStatus = "NOT-STARTED"

        # 当前的JOB流水号, 初始为零，随后开始自增1
        self.JobID = 0

        # 记录当前Agent启动状态
        self.isAgentStarted = False

        # 记录Meta的数据库连接信息
        self.MetaConn = None

        # 更新Meta信息的锁
        self.MetaLockHandler = None

        # 是否为手动注册的Worker
        self.isManualRegister = False

    # 设置Meta的连接信息
    def setMetaConn(self, p_conn):
        self.MetaConn = p_conn

    # 设置当前后台代理进程的状态
    def setWorkerStatus(self, p_WorkerStatus):
        self.WorkerStatus = p_WorkerStatus

    # 获得当前清理进程的状态
    def getWorkerStatus(self):
        return self.WorkerStatus

    # 根据Job的进程ID返回指定的JOB信息
    def getJobByProcessID(self, p_szProcessID):
        # 返回指定的Job信息，如果找不到，返回None
        m_SQL = "SELECT     J.Job_ID,J.Job_Name,J.Starter_Interval, " \
                "           J.Starter_Last_Active_Time, J.Parallel, J.Loop, " \
                "           J.Started_JOBS, J.Failed_JOBS, J.Finished_JOBS, J.Active_JOBS, J.Error_Message, " \
                "           J.Script, J.Script_FullName, J.Think_Time,  J.Timeout, " \
                "           J.Submit_Time, J.Start_Time, J.End_Time, " \
                "           J.Blowout_Threshold_Count, J.Status, J.JOB_TAG " \
                "FROM   TESTCLI_JOBS J, TESTCLI_WORKERS T " \
                "WHERE  J.Job_ID = T.Job_ID " \
                "AND    T.ProcessID = " + str(p_szProcessID)
        m_db_cursor = self.MetaConn.cursor()
        m_db_cursor.execute(m_SQL)
        m_rs = m_db_cursor.fetchone()
        if m_rs is None:
            m_db_cursor.close()
            return None
        else:
            m_Job = JOB()
            m_Job.setJobID(m_rs[0])
            m_Job.setJobName(m_rs[1])
            m_Job.setStarterInterval(m_rs[2])
            m_Job.setStarterLastActiveTime(m_rs[3])
            m_Job.setParallel(m_rs[4])
            m_Job.setLoop(m_rs[5])
            m_Job.setStartedJobs(m_rs[6])
            m_Job.setFailedJobs(m_rs[7])
            m_Job.setFinishedJobs(m_rs[8])
            m_Job.setActiveJobs(m_rs[9])
            m_Job.setErrorMessage(m_rs[10])
            m_Job.setScript(m_rs[11])
            m_Job.setScriptFullName(m_rs[12])
            m_Job.setThinkTime(m_rs[13])
            m_Job.setTimeOut(m_rs[14])
            m_Job.setSubmitTime(m_rs[15])
            m_Job.setStartTime(m_rs[16])
            m_Job.setEndTime(m_rs[17])
            m_Job.setBlowoutThresHoldCount(m_rs[18])
            m_Job.setStatus(m_rs[19])
            m_Job.setTag(m_rs[20])
            m_db_cursor.close()

            # 获取Worker信息
            m_SQL = "SELECT WorkerHandler_ID,ProcessID,start_time,end_time,exit_code, Finished_Status,Timer_Point "  \
                    "FROM   TESTCLI_WORKERS WHERE JOB_ID=" + str(m_Job.getJobID())
            m_db_cursor = self.MetaConn.cursor()
            m_db_cursor.execute(m_SQL)
            m_rs = m_db_cursor.fetchall()
            if m_rs is not None:
                for m_row in m_rs:
                    m_Worker = Workers()
                    m_Worker.WorkerHandler_ID = m_row[0]
                    m_Worker.ProcessID = m_row[1]
                    m_Worker.start_time = m_row[2]
                    m_Worker.end_time = m_row[3]
                    m_Worker.exit_code = m_row[4]
                    m_Worker.Finished_Status = m_row[5]
                    m_Worker.Timer_Point = m_row[6]
                    m_Job.setWorker(m_Worker)
            m_db_cursor.close()

            return m_Job

    # 根据JobID返回指定的JOB信息
    def getJobByID(self, p_szJobID):
        # 返回指定的Job信息，如果找不到，返回None
        m_SQL = "SELECT Job_ID,Job_Name,Starter_Interval, " \
                "Starter_Last_Active_Time, Parallel, Loop, " \
                "Started_JOBS, Failed_JOBS,Finished_JOBS,Active_JOBS,Error_Message, " \
                "Script, Script_FullName, Think_Time,Timeout, " \
                "Submit_Time, Start_Time, End_Time, " \
                "Blowout_Threshold_Count, Status, JOB_TAG " \
                "FROM TESTCLI_JOBS WHERE Job_ID = " + str(p_szJobID)
        m_db_cursor = self.MetaConn.cursor()
        m_db_cursor.execute(m_SQL)
        m_rs = m_db_cursor.fetchone()
        if m_rs is None:
            m_db_cursor.close()
            return None
        else:
            m_Job = JOB()
            m_Job.setJobID(m_rs[0])
            m_Job.setJobName(m_rs[1])
            m_Job.setStarterInterval(m_rs[2])
            m_Job.setStarterLastActiveTime(m_rs[3])
            m_Job.setParallel(m_rs[4])
            m_Job.setLoop(m_rs[5])
            m_Job.setStartedJobs(m_rs[6])
            m_Job.setFailedJobs(m_rs[7])
            m_Job.setFinishedJobs(m_rs[8])
            m_Job.setActiveJobs(m_rs[9])
            m_Job.setErrorMessage(m_rs[10])
            m_Job.setScript(m_rs[11])
            m_Job.setScriptFullName(m_rs[12])
            m_Job.setThinkTime(m_rs[13])
            m_Job.setTimeOut(m_rs[14])
            m_Job.setSubmitTime(m_rs[15])
            m_Job.setStartTime(m_rs[16])
            m_Job.setEndTime(m_rs[17])
            m_Job.setBlowoutThresHoldCount(m_rs[18])
            m_Job.setStatus(m_rs[19])
            m_Job.setTag(m_rs[20])
            m_db_cursor.close()

            # 获取Worker信息
            m_SQL = "SELECT WorkerHandler_ID,ProcessID,start_time,end_time,exit_code, Finished_Status,Timer_Point "  \
                    "FROM   TESTCLI_WORKERS WHERE JOB_ID=" + str(m_Job.getJobID())
            m_db_cursor = self.MetaConn.cursor()
            m_db_cursor.execute(m_SQL)
            m_rs = m_db_cursor.fetchall()
            if m_rs is not None:
                for m_row in m_rs:
                    m_Worker = Workers()
                    m_Worker.WorkerHandler_ID = m_row[0]
                    m_Worker.ProcessID = m_row[1]
                    m_Worker.start_time = m_row[2]
                    m_Worker.end_time = m_row[3]
                    m_Worker.exit_code = m_row[4]
                    m_Worker.Finished_Status = m_row[5]
                    m_Worker.Timer_Point = m_row[6]
                    m_Job.setWorker(m_Worker)
            m_db_cursor.close()
            return m_Job

    # 根据JobName返回指定的JOB信息
    def getJobByName(self, jobName):
        # 返回指定的Job信息，如果找不到，返回None
        m_SQL = "SELECT Job_ID,Job_Name,Starter_Interval, " \
                "       Starter_Last_Active_Time, Parallel, Loop, " \
                "       Started_JOBS, Failed_JOBS,Finished_JOBS,Active_JOBS,Error_Message, " \
                "       Script, Script_FullName, Think_Time, Timeout, " \
                "       Submit_Time, Start_Time, End_Time, " \
                "       Blowout_Threshold_Count, Status, JOB_TAG " \
                "FROM TESTCLI_JOBS WHERE JOB_NAME = '" + str(jobName) + "'"
        m_db_cursor = self.MetaConn.cursor()
        m_db_cursor.execute(m_SQL)
        m_rs = m_db_cursor.fetchone()
        if m_rs is None:
            m_db_cursor.close()
            return None
        else:
            m_Job = JOB()
            m_Job.setJobID(m_rs[0])
            m_Job.setJobName(m_rs[1])
            m_Job.setStarterInterval(m_rs[2])
            m_Job.setStarterLastActiveTime(m_rs[3])
            m_Job.setParallel(m_rs[4])
            m_Job.setLoop(m_rs[5])
            m_Job.setStartedJobs(m_rs[6])
            m_Job.setFailedJobs(m_rs[7])
            m_Job.setFinishedJobs(m_rs[8])
            m_Job.setActiveJobs(m_rs[9])
            m_Job.setErrorMessage(m_rs[10])
            m_Job.setScript(m_rs[11])
            m_Job.setScriptFullName(m_rs[12])
            m_Job.setThinkTime(m_rs[13])
            m_Job.setTimeOut(m_rs[14])
            m_Job.setSubmitTime(m_rs[15])
            m_Job.setStartTime(m_rs[16])
            m_Job.setEndTime(m_rs[17])
            m_Job.setBlowoutThresHoldCount(m_rs[18])
            m_Job.setStatus(m_rs[19])
            m_Job.setTag(m_rs[20])
            m_db_cursor.close()

            # 获取Worker信息
            m_SQL = "SELECT WorkerHandler_ID,ProcessID,start_time,end_time,exit_code, Finished_Status, Timer_Point "  \
                    "FROM   TESTCLI_WORKERS WHERE JOB_ID=" + str(m_Job.getJobID())
            m_db_cursor = self.MetaConn.cursor()
            m_db_cursor.execute(m_SQL)
            m_rs = m_db_cursor.fetchall()
            if m_rs is not None:
                for m_row in m_rs:
                    m_Worker = Workers()
                    m_Worker.WorkerHandler_ID = m_row[0]
                    m_Worker.ProcessID = m_row[1]
                    m_Worker.start_time = m_row[2]
                    m_Worker.end_time = m_row[3]
                    m_Worker.exit_code = m_row[4]
                    m_Worker.Finished_Status = m_row[5]
                    m_Worker.Timer_Point = m_row[6]
                    m_Job.setWorker(m_Worker)
            m_db_cursor.close()
            return m_Job

    # 根据JobName返回指定的JOB信息
    def getAllJobs(self):
        # 返回指定的Job信息，如果找不到，返回None
        m_SQL = "SELECT Job_ID FROM TESTCLI_JOBS ORDER BY Job_ID"
        m_db_cursor = self.MetaConn.cursor()
        m_db_cursor.execute(m_SQL)
        m_rs = m_db_cursor.fetchall()
        if m_rs is None:
            m_db_cursor.close()
            return []
        else:
            m_JOBList = []
            for m_row in m_rs:
                m_Job = self.getJobByID(m_row[0])
                m_JOBList.append(m_Job)
            m_db_cursor.close()
            return m_JOBList

    @staticmethod
    def runSQLCli(p_args):
        import sys
        from .testcli import TestCli

        # 运行子进程的时候，不需要启动JOBManager
        sqlcliHandler = TestCli(
            script=p_args["script"],
            logon=p_args["logon"],
            logfilename=p_args["logfilename"],
            commandMap=p_args["commandMap"],
            nologo=p_args["nologo"],
            headlessMode=True,
            workerName=p_args["workername"],
            xlog=p_args["xlog"]
        )
        sys.exit(sqlcliHandler.run_cli())

    # 后台守护线程，跟踪进程信息，启动或强制关闭进程
    def JOBManagerAgent(self):
        try:
            if self.getWorkerStatus() == "NOT-STARTED":
                self.setWorkerStatus("RUNNING")
            while True:
                # 如果程序退出，则关闭该Agent线程
                if self.getWorkerStatus() == "WAITINGFOR_STOP":
                    self.setWorkerStatus("STOPPED")
                    break
                # 循环处理工作JOB
                for m_Job in self.getAllJobs():
                    if m_Job.getStatus() in ("Submitted", "FAILED", "SHUTDOWNED", "FINISHED", "ABORTED"):
                        # 已经结束的Case不再处理， 或者刚提交，但是没有执行的
                        continue
                    if m_Job.getStatus() in ("RUNNING", "WAITINGFOR_SHUTDOWN", "WAITINGFOR_ABORT"):
                        # 依次检查Worker的状态
                        # 即使已经处于WAITINGFOR_SHUTDOWN或者WAITINGFOR_ABORT中，也不排除还有没有完成的作业
                        m_WorkerList = m_Job.getWorkers()
                        currenttime = int(time.mktime(datetime.datetime.now().timetuple()))
                        bAllWorkerFinished = True
                        for m_Worker in m_WorkerList:
                            m_ProcessID = m_Worker.ProcessID
                            if m_ProcessID != 0:
                                m_Process = self.processHandlerInfo[m_ProcessID]
                                if not m_Process.is_alive():
                                    # 进程ID不是0，进程已经不存在，或者是正常完成，或者是异常退出
                                    if m_Process.exitcode != 0:
                                        m_Job.failed_jobs = m_Job.failed_jobs + 1
                                    m_Job.finished_jobs = m_Job.finished_jobs + 1
                                    m_Job.active_jobs = m_Job.active_jobs - 1
                                    m_Job.FinishWorker(self.MetaConn, m_Worker.WorkerHandler_ID,
                                                       m_Process.exitcode, "")
                                    self.SaveJob(m_Job)
                                    # 从当前保存的进程信息中释放该进程
                                    self.processHandlerInfo.pop(m_ProcessID)
                                else:
                                    # 进程还在运行中
                                    if m_Job.getTimeOut() != 0:
                                        # 设置了超时时间，我们需要根据超时时间进行判断
                                        if m_Worker.start_time + m_Job.getTimeOut() < currenttime:
                                            m_Process.terminate()
                                            m_Job.FinishWorker(self.MetaConn, m_Worker.WorkerHandler_ID,
                                                               m_Process.exitcode, "TIMEOUT")
                                            m_Job.failed_jobs = m_Job.failed_jobs + 1
                                            m_Job.finished_jobs = m_Job.finished_jobs + 1
                                            m_Job.active_jobs = m_Job.active_jobs - 1
                                            self.SaveJob(m_Job)
                                            # 从当前保存的进程信息中释放该进程
                                            self.processHandlerInfo.pop(m_ProcessID)
                                        else:
                                            if m_Job.getStatus() == "WAITINGFOR_ABORT":
                                                m_Process.terminate()
                                                m_Job.FinishWorker(self.MetaConn, m_Worker.WorkerHandler_ID,
                                                                   m_Process.exitcode, "ABORTED")
                                                m_Job.failed_jobs = m_Job.failed_jobs + 1
                                                m_Job.finished_jobs = m_Job.finished_jobs + 1
                                                m_Job.active_jobs = m_Job.active_jobs - 1
                                                self.SaveJob(m_Job)
                                                # 从当前保存的进程信息中释放该进程
                                                self.processHandlerInfo.pop(m_ProcessID)
                                            bAllWorkerFinished = False
                                    else:
                                        if m_Job.getStatus() == "WAITINGFOR_ABORT":
                                            m_Process.terminate()
                                            m_Job.FinishWorker(self.MetaConn, m_Worker.WorkerHandler_ID,
                                                               m_Process.exitcode, "ABORTED")
                                            m_Job.failed_jobs = m_Job.failed_jobs + 1
                                            m_Job.finished_jobs = m_Job.finished_jobs + 1
                                            m_Job.active_jobs = m_Job.active_jobs - 1
                                            self.SaveJob(m_Job)
                                            # 从当前保存的进程信息中释放该进程
                                            self.processHandlerInfo.pop(m_ProcessID)
                                        bAllWorkerFinished = False
                                    continue
                        if bAllWorkerFinished and m_Job.getStatus() == "WAITINGFOR_SHUTDOWN":
                            # 检查脚本信息，如果脚本压根不存在，则无法后续的操作
                            m_Job.setStatus("SHUTDOWNED")
                            m_Job.setErrorMessage("JOB has been shutdown successful.")
                            self.SaveJob(m_Job)
                            continue
                        if m_Job.getStatus() == "WAITINGFOR_ABORT":
                            # 检查脚本信息，如果脚本压根不存在，则无法后续的操作
                            m_Job.setStatus("ABORTED")
                            m_Job.setErrorMessage("JOB has been aborted.")
                            self.SaveJob(m_Job)
                            continue
                        if m_Job.getBlowoutThresHoldCount() != 0:
                            if m_Job.getFailedJobs() >= m_Job.getBlowoutThresHoldCount():
                                if bAllWorkerFinished:
                                    # 已经失败的脚本实在太多，不能再继续
                                    m_Job.setStatus("FAILED")
                                    m_Job.setErrorMessage("JOB blowout, terminate.")
                                    self.SaveJob(m_Job)
                                continue
                        if m_Job.getScript() is None:
                            # 检查脚本信息，如果脚本压根不存在，则无法后续的操作
                            m_Job.setStatus("FAILED")
                            m_Job.setErrorMessage("Script parameter is null.")
                            self.SaveJob(m_Job)
                            continue
                        if m_Job.getScriptFullName() is None:
                            # 如果脚本没有补充完全的脚本名称，则此刻进行补充
                            # 命令里头的是全路径名，或者是基于当前目录的相对文件名
                            m_Script_FileName = m_Job.getScript()
                            if os.path.isfile(m_Script_FileName):
                                m_SQL_ScriptBaseName = os.path.basename(m_Script_FileName)
                                m_SQL_ScriptFullName = os.path.abspath(m_Script_FileName)
                            else:
                                if self.getProcessContextInfo("script") is not None:
                                    m_SQL_ScriptHomeDirectory = os.path.dirname(self.getProcessContextInfo("script"))
                                    if os.path.isfile(os.path.join(m_SQL_ScriptHomeDirectory, m_Script_FileName)):
                                        m_SQL_ScriptBaseName = \
                                            os.path.basename(os.path.join(m_SQL_ScriptHomeDirectory, m_Script_FileName))
                                        m_SQL_ScriptFullName = \
                                            os.path.abspath(os.path.join(m_SQL_ScriptHomeDirectory, m_Script_FileName))
                                    else:
                                        m_Job.setStatus("FAILED")
                                        m_Job.setStartTime(None)
                                        m_Job.setEndTime(None)
                                        m_Job.setErrorMessage("Script [" + m_Script_FileName + "] does not exist.")
                                        self.SaveJob(m_Job)
                                        continue
                                else:
                                    m_Job.setStatus("FAILED")
                                    m_Job.setStartTime(None)
                                    m_Job.setEndTime(None)
                                    m_Job.setErrorMessage("Script [" + m_Script_FileName + "] does not exist.")
                                    self.SaveJob(m_Job)
                                    continue
                            m_Job.setScript(m_SQL_ScriptBaseName)
                            m_Job.setScriptFullName(m_SQL_ScriptFullName)
                            self.SaveJob(m_Job)
                        if m_Job.getFinishedJobs() >= (m_Job.getLoop() * m_Job.getParallel()):
                            # 已经完成了全部的作业，标记为完成状态
                            m_Job.setStatus("FINISHED")
                            m_Job.setEndTime(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))
                            # 将任务添加到后台进程信息中
                            self.SaveJob(m_Job)
                            continue
                        # 开始陆续启动需要完成的任务
                        # 获得可以启动的任务进程列表
                        m_WorkerStarterList = m_Job.getWorkerStarter()
                        # 给每一个进程提供唯一的日志文件名
                        m_JOB_Sequence = m_Job.getStartedJobs()
                        # 循环启动所有的进程
                        for m_WorkerStarter in m_WorkerStarterList:
                            m_args = {"logon": self.getProcessContextInfo("logon"),
                                      "nologo": self.getProcessContextInfo("nologo"),
                                      "commandMap": self.getProcessContextInfo("commandMap"),
                                      "script": m_Job.getScriptFullName(),
                                      "workername":
                                          m_Job.getJobName() + "#" + str(m_WorkerStarter) + "-" +
                                          str(m_JOB_Sequence+1)
                                      }
                            xlogPath = self.getProcessContextInfo("xlog")
                            if xlogPath is None:
                                m_args["xlog"] = ""
                            else:
                                # 这里由于Cli已经切换了当前的路径到脚本路径，所以当把带有相对路径的xlog传递给子进程时候，会导致子进程无法使用
                                # 这里要做相对路径的转换
                                xlogFullPatch = os.path.join(
                                    self.getProcessContextInfo("processPwd"),
                                    xlogPath
                                )
                                xlogRelPath = os.path.relpath(
                                    xlogFullPatch,
                                    os.getcwd()
                                )
                                m_args["xlog"] = xlogRelPath
                            if self.getProcessContextInfo("logfilename") is not None:
                                logFileDir = os.path.join(
                                    self.getProcessContextInfo("processPwd"),
                                    os.path.dirname(self.getProcessContextInfo("logfilename")))
                                logFileName = os.path.join(
                                    logFileDir,
                                    m_Job.getScript().split('.')[0] + "_" + str(m_Job.getJobName()) +
                                    str(m_JOB_Sequence+1) + "-" + str(m_WorkerStarter) + ".log")
                            else:
                                logFileName = \
                                    m_Job.getScript().split('.')[0] + "_" + \
                                    str(m_Job.getJobName()) + "-" + \
                                    str(m_JOB_Sequence+1) + "-" + \
                                    str(m_WorkerStarter) + ".log"
                            m_args["logfilename"] = logFileName
                            # jpype无法运行在fork机制下的子进程中，linux默认为fork机制，所以这里要强制为spawn
                            # fork模式下，子进程会继承父进程的一些信息
                            # spawn模式下，子进程为全新进程
                            m_ProcessManagerContext = multiprocessing.get_context("spawn")
                            m_Process = m_ProcessManagerContext.Process(target=self.runSQLCli, args=(m_args,))
                            m_Process.start()

                            # 更新Worker字典信息
                            m_Job.StartWorker(self.MetaConn, m_WorkerStarter, m_Process.pid)

                            # 更新JOB信息
                            m_Job.active_jobs = m_Job.active_jobs + 1
                            m_Job.started_jobs = m_Job.started_jobs + 1
                            m_Job.setStartedJobs(m_JOB_Sequence+1)
                            m_JOB_Sequence = m_JOB_Sequence + 1
                            self.SaveJob(m_Job)
                            self.processHandlerInfo[m_Process.pid] = m_Process
                # 每0.5秒检查一次任务
                time.sleep(3)
        except Exception as e:
            click.secho("JobManager failed with [" + repr(e) + "]. Quit JobManager Agent.", err=True, fg="red")
            self.isAgentStarted = False

    # 启动Agent进程
    def registerAgent(self):
        # 启动后台守护线程，用来处理延时启动，超时等问题
        Agenthread = threading.Thread(target=self.JOBManagerAgent)
        Agenthread.daemon = True  # 主进程退出，守护进程也会退出
        Agenthread.name = "JobManagerAgent"
        Agenthread.start()
        self.isAgentStarted = True

    # 退出Agent进程
    def unregisterAgent(self):
        if self.isAgentStarted:
            if self.getWorkerStatus() == "RUNNING":
                self.setWorkerStatus("WAITINGFOR_STOP")
                while True:
                    if self.getWorkerStatus() == "STOPPED":
                        break
                    else:
                        time.sleep(1)
            self.isAgentStarted = False

    def SaveJob(self, p_objJOB: JOB):
        if self.MetaLockHandler is None:
            self.MetaLockHandler = Lock()
        try:
            self.MetaLockHandler.acquire()
            m_SQL = "SELECT COUNT(1) FROM TESTCLI_JOBS WHERE JOB_ID = " + str(p_objJOB.id)
            m_db_cursor = self.MetaConn.cursor()
            m_db_cursor.execute(m_SQL)
            m_rs = m_db_cursor.fetchone()
            if m_rs[0] == 0:
                m_SQL = "Insert Into TESTCLI_JOBS(JOB_ID,JOB_Name,Starter_Interval, Starter_Last_Active_Time, " \
                        "Parallel, Loop, Started_JOBS, Failed_JOBS,Finished_JOBS,Active_JOBS,Error_Message, " \
                        "Script, Script_FullName, Think_Time,  Timeout, Submit_Time, Start_Time, End_Time, " \
                        "Blowout_Threshold_Count, Status, JOB_Tag) VALUES (" \
                        "?,?,?,?," \
                        "?,?,?,?,?,?,?, " \
                        "?,?,?,?,?,?,?," \
                        "?,?,?" \
                        ")"
                m_Data = [
                    p_objJOB.id,
                    p_objJOB.job_name,
                    p_objJOB.starter_interval,
                    p_objJOB.starter_last_active_time,
                    p_objJOB.parallel,
                    p_objJOB.loop,
                    p_objJOB.started_jobs,
                    p_objJOB.failed_jobs,
                    p_objJOB.finished_jobs,
                    p_objJOB.active_jobs,
                    p_objJOB.error_message,
                    p_objJOB.script,
                    p_objJOB.script_fullname,
                    p_objJOB.think_time,
                    p_objJOB.timeout,
                    p_objJOB.submit_time,
                    p_objJOB.start_time,
                    p_objJOB.end_time,
                    p_objJOB.blowout_threshold_count,
                    p_objJOB.status,
                    p_objJOB.tag
                ]
                m_db_cursor.execute(m_SQL, parameters=m_Data)
            else:
                m_SQL = "Update TESTCLI_JOBS " \
                        "SET    JOB_NAME = ?," \
                        "       Starter_Interval = ?," \
                        "       Starter_Last_Active_Time = ?," \
                        "       Parallel = ?," \
                        "       Loop = ?," \
                        "       Started_JOBS = ?," \
                        "       Failed_JOBS = ?," \
                        "       Finished_JOBS = ?," \
                        "       Active_JOBS = ?," \
                        "       Error_Message = ?," \
                        "       Script = ?," \
                        "       Script_FullName = ?," \
                        "       Think_Time = ?," \
                        "       Timeout = ?," \
                        "       Submit_Time = ?," \
                        "       Start_Time = ?," \
                        "       End_Time = ?," \
                        "       Blowout_Threshold_Count = ?," \
                        "       Status = ?, " \
                        "       JOB_TAG = ? " \
                        "WHERE  JOB_ID = " + str(p_objJOB.id)
                m_Data = [
                    p_objJOB.job_name,
                    p_objJOB.starter_interval,
                    p_objJOB.starter_last_active_time,
                    p_objJOB.parallel,
                    p_objJOB.loop,
                    p_objJOB.started_jobs,
                    p_objJOB.failed_jobs,
                    p_objJOB.finished_jobs,
                    p_objJOB.active_jobs,
                    p_objJOB.error_message,
                    p_objJOB.script,
                    p_objJOB.script_fullname,
                    p_objJOB.think_time,
                    p_objJOB.timeout,
                    p_objJOB.submit_time,
                    p_objJOB.start_time,
                    p_objJOB.end_time,
                    p_objJOB.blowout_threshold_count,
                    p_objJOB.status,
                    p_objJOB.tag
                ]
                m_db_cursor.execute(m_SQL, parameters=m_Data)
            m_db_cursor.close()
            self.MetaConn.commit()
        except Exception:
            print("Internal error:: Save Job write not complete. ")
            import traceback
            if "TESTCLI_DEBUG" not in os.environ:
                print('traceback.print_exc():\n%s' % traceback.print_exc())
                print('traceback.format_exc():\n%s' % traceback.format_exc())
        finally:
            self.MetaLockHandler.release()

    # 提交一个任务
    def createjob(self, p_szname: str):
        # 初始化一个任务
        job = JOB()
        job.setSubmitTime(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))

        # 创建第一个JOB的时候，初始化共享服务器
        if not self.isAgentStarted:
            self.registerAgent()

        # 设置JOBID
        job.setJobID(self.JobID + 1)
        job.setJobName(jobName=p_szname)

        # 当前的JOBID加一
        self.JobID = self.JobID + 1

        # 返回JOB信息
        return job

    # 显示当前所有已经提交的任务信息
    def showjob(self, jobName: str):
        """
            job_name status active_jobs failed_jobs finished_jobs submit_time start_time end_time

            max_transaction_time  avg_transaction_time min_transaction_time,
            parallel, loop, script, script_fullname, think_time, timeout,
            blowout_threshold_count
        """
        # 如果输入的参数为all，则显示全部的JOB信息
        if jobName.lower() == "all":
            m_Header = ["job_name", "tag", "status", "active_jobs", "failed_jobs", "finished_jobs",
                        "submit_time", "start_time", "end_time", "message"]
            m_Result = []
            for m_JOB in self.getAllJobs():
                m_Result.append([m_JOB.getJobName(), m_JOB.getTag(), m_JOB.getStatus(), m_JOB.getActiveJobs(),
                                 m_JOB.getFailedJobs(), m_JOB.getFinishedJobs(),
                                 str(m_JOB.getSubmitTime()), str(m_JOB.getStartTime()),
                                 str(m_JOB.getEndTime()), str(m_JOB.getErrorMessage())])
            return {
                "type": "result",
                "title": None,
                "rows": m_Result,
                "headers": m_Header,
                "columnTypes": None,
                "status": "Total [" + str(len(m_Result)) + "] Jobs."
            }
        else:
            strMessages = ""
            m_Job = self.getJobByName(jobName)
            if m_Job is None:
                return None, None, None, None, "JOB [" + jobName + "] does not exist."
            strMessages = strMessages + 'JOB_Name = [{0:12}]; ID = [{1:4d}]; Tag = [{2:12}], Status = [{3:12}]\n'.\
                format(jobName, m_Job.getJobID(), m_Job.getTag(), m_Job.getStatus())
            strMessages = strMessages + 'ActiveJobs/FailedJobs/FinishedJobs: [{0:15d}/{1:15d}/{2:15d}]\n'.\
                format(m_Job.getActiveJobs(), m_Job.getFailedJobs(), m_Job.getFinishedJobs())
            strMessages = strMessages + 'Submit Time: [{0:70}]\n'.format(str(m_Job.getSubmitTime()))
            strMessages = strMessages + 'Start Time : [{0:30}] ; End Time: [{1:25}]\n'.\
                format(str(m_Job.getStartTime()), str(m_Job.getEndTime()))
            strMessages = strMessages + 'Script              : [{0:61}]\n'.format(str(m_Job.getScript()))
            strMessages = strMessages + 'Script Full FileName: [{0:61}]\n'.format(str(m_Job.getScriptFullName()))
            strMessages = strMessages + 'Parallel: [{0:15d}]; Loop: [{1:15d}]; Starter Interval: [{2:10d}s]\n'.\
                format(m_Job.getParallel(), m_Job.getLoop(),
                       m_Job.getStarterInterval())
            if m_Job.getStartTime() is None:
                m_ElapsedTime = 0
            else:
                m_ElapsedTime = time.time() - time.mktime(time.strptime(m_Job.getStartTime(), "%Y-%m-%d %H:%M:%S"))
            strMessages = strMessages + 'Think time: [{0:15d}]; Timeout: [{1:15d}]; Elapsed: [{2:15s}]\n'.\
                format(m_Job.getThinkTime(), m_Job.getTimeOut(), "%10.2f" % float(m_ElapsedTime))
            strMessages = strMessages + 'Blowout Threshold Count: [{0:58d}]\n'.\
                format(m_Job.getBlowoutThresHoldCount())
            strMessages = strMessages + 'Message : [{0:73s}]\n'.format(str(m_Job.getErrorMessage()))
            strMessages = strMessages + 'Detail Workers>>>:\n'
            strMessages = strMessages + '+{0:10s}+{1:10s}+{2:20s}+{3:20s}+{4:20s}+\n'.format(
                '-'*10, '-'*10, '-'*20, '-'*20, '-'*20)
            strMessages = strMessages + '|{0:10s}|{1:10s}|{2:20s}|{3:20s}|{4:20s}|\n'.format(
                'Worker-ID', 'PID', 'Start_Time', 'End_Time', 'Timer_Point')
            strMessages = strMessages + '+{0:10s}+{1:10s}+{2:20s}+{3:20s}+{4:20s}+\n'.format(
                '-'*10, '-'*10, '-'*20, '-'*20, '-'*20)
            for m_Worker in m_Job.getWorkers():
                if m_Worker.start_time is None:
                    m_StartTime = "____-__-__ __:__:__"
                else:
                    m_StartTime = datetime.datetime.fromtimestamp(m_Worker.start_time).\
                        strftime("%Y-%m-%d %H:%M:%S")
                if m_Worker.end_time is None:
                    m_EndTime = "____-__-__ __:__:__"
                else:
                    m_EndTime = datetime.datetime.fromtimestamp(m_Worker.end_time).\
                        strftime("%Y-%m-%d %H:%M:%S")
                strMessages = strMessages + '|{0:10d}|{1:10d}|{2:20s}|{3:20s}|{4:20s}|\n'.\
                    format(m_Worker.WorkerHandler_ID, m_Worker.ProcessID,
                           m_StartTime, m_EndTime, str(m_Worker.Timer_Point))
                strMessages = strMessages + '+{0:10s}+{1:10s}+{2:20s}+{3:20s}+{4:20s}+\n'.\
                    format('-' * 10, '-' * 10, '-' * 20, '-' * 20, '-' * 20)
            return {
                "type": "result",
                "title": None,
                "rows": None,
                "headers": None,
                "columnTypes": None,
                "status": strMessages
            }

    # 启动JOB
    def startjob(self, p_jobName: str):
        # 将JOB从Submitted变成Runnning
        # 如果输入的参数为all，则启动全部的JOB信息
        nJobStarted = 0
        if p_jobName.lower() == "all":
            m_JobList = self.getAllJobs()
        else:
            m_JobList = [self.getJobByName(p_jobName), ]
        for m_Job in m_JobList:
            if m_Job.getStatus() == "Submitted":
                nJobStarted = nJobStarted + 1
                # 标记Worker已经开始运行
                m_Job.setStatus("RUNNING")
                # 设置Worker运行开始时间
                m_Job.setStartTime(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))
                # 将任务信息更新到后台进程信息中
                self.SaveJob(m_Job)
        return nJobStarted

    # 等待所有的JOB完成
    # 这里不包括光Submit，并没有实质性开始动作的JOB
    def waitjob(self, p_jobName: str, params: dict):
        timeoutLimit = 0
        for paramKey, paramValue in params.items():
            if str(paramKey).upper() == "TIMEOUT":
                if not str(paramValue).isdigit():
                    raise TestCliException("Invalid timeout set [" + str(paramValue) + "], it must be digit.")
                timeoutLimit = int(paramValue)
        start = time.time()
        if p_jobName.lower() == "all":
            while True:
                # 如果JobManager意外退出，也没有继续等待下去的意义
                if not self.isAgentStarted:
                    raise TestCliException("Job agent unexpected lost. Job wait failed.")
                # 等待也是有时间限制的
                if (timeoutLimit > 0) and ((time.time() - start) > timeoutLimit):
                    raise TestCliException("Job wait terminated. Timeout [" + str(timeoutLimit) + "]")
                # 没有正在运行的JOB
                if not self.isAllJobClosed():
                    time.sleep(3)
                    continue
                # 没有已经提交，但是还没有运行的JOB
                bAllProcessFinished = True
                for m_Job in self.getAllJobs():
                    if m_Job.getStatus() not in \
                            ["Submitted", "FINISHED", "SHUTDOWNED", "ABORTED", "FAILED"]:
                        bAllProcessFinished = False
                        time.sleep(3)
                        continue
                if bAllProcessFinished:
                    break
        else:
            while True:
                # 如果JobManager意外退出，也没有继续等待下去的意义
                if not self.isAgentStarted:
                    raise TestCliException("Job agent unexpected lost. Job wait failed.")
                # 等待也是有时间限制的
                if (timeoutLimit > 0) and ((time.time() - start) > timeoutLimit):
                    raise TestCliException("Job wait terminated. Timeout [" + str(timeoutLimit) + "]")
                if self.isJobClosed(p_jobName):
                    break
                else:
                    time.sleep(3)

    # 停止JOB作业
    def shutdownjob(self, p_jobName: str):
        # 将JOB从Runnning变成waitingfor_shutdown
        # 如果输入的参数为all，则停止全部的JOB信息
        nJobShutdowned = 0
        if p_jobName.lower() == "all":
            m_JobList = self.getAllJobs()
        else:
            m_JobList = [self.getJobByName(p_jobName), ]
        for m_Job in m_JobList:
            if m_Job.getStatus() in ("RUNNING", "Submitted"):
                nJobShutdowned = nJobShutdowned + 1
                # 标记Worker已经开始运行
                m_Job.setStatus("WAITINGFOR_SHUTDOWN")
                # 将任务信息更新到后台进程信息中
                self.SaveJob(m_Job)
        return nJobShutdowned

    # 放弃JOB作业
    def abortjob(self, p_jobName: str):
        # 将JOB从Runnning变成waitingfor_abort
        # 如果输入的参数为all，则放弃全部的JOB信息
        nJobAborted = 0
        if p_jobName.lower() == "all":
            m_JobList = self.getAllJobs()
        else:
            m_JobList = [self.getJobByName(p_jobName), ]
        for m_Job in m_JobList:
            if m_Job.getStatus() == "RUNNING":
                nJobAborted = nJobAborted + 1
                # 标记Worker已经开始运行
                m_Job.setStatus("WAITINGFOR_ABORT")
                # 将任务信息更新到后台进程信息中
                self.SaveJob(m_Job)
        return nJobAborted

    # 等待TimerPoint到特定的时间点
    def waitjobtimer(self, p_TimerPoint):
        # 获得当前的Worker_Tag
        m_Job = self.getJobByProcessID(os.getpid())
        if m_Job is None:
            raise TestCliException("TestCli-0000:  This is not a job process at all. What are you waiting for?")

        # 获得进程的Worker信息
        m_Worker = m_Job.getWorkerByProcessID(os.getpid())
        # 获取共有多少个进程需要达到该时间点
        m_JobTag = m_Job.getTag()
        if (m_JobTag is None) or (m_JobTag == ""):
            if self.isManualRegister:
                m_TotalParallel = m_Job.getActiveJobs()
            else:
                m_TotalParallel = m_Job.getParallel()
        else:
            m_SQL = "SELECT     Sum(J.Parallel) " \
                    "FROM       TESTCLI_JOBS J " \
                    "WHERE      J.Job_TAG = '" + m_JobTag + "' " + \
                    "AND        Status Not In ('FAILED', 'SHUTDOWNED', 'FINISHED', 'ABORTED') "
            m_db_cursor = self.MetaConn.cursor()
            m_db_cursor.execute(m_SQL)
            m_rs = m_db_cursor.fetchone()
            m_TotalParallel = m_rs[0]
            m_db_cursor.close()

        # 自己已经到达时间点， 标记Timer_Point为自己等待的时间点
        m_Worker.Timer_Point = p_TimerPoint
        m_Job.setWorker(m_Worker)
        m_db_cursor = self.MetaConn.cursor()
        m_SQL = "UPDATE TESTCLI_WORKERS " \
                "SET    Timer_Point = ? " \
                "WHERE  ProcessID=" + str(os.getpid())
        m_Data = [
            m_Worker.Timer_Point
        ]
        m_db_cursor.execute(m_SQL, parameters=m_Data)
        self.MetaConn.commit()

        # 检查是否为READY状态，如果是，则可以离开
        while True:
            # 检查其他进程是否到达该检查点
            m_TimerPointAllArrived = False
            if (m_JobTag is None) or (m_JobTag == ""):
                m_SQL = "SELECT     COUNT(1) " \
                        "FROM       TESTCLI_WORKERS T " \
                        "WHERE      T.Job_ID = " + str(m_Job.id) + " " + \
                        "AND        T.Timer_Point ='" + p_TimerPoint + "'"
            else:
                m_SQL = "SELECT     COUNT(1) " \
                        "FROM       TESTCLI_WORKERS T " \
                        "WHERE      T.Job_TAG = '" + m_JobTag + "' " + \
                        "AND        T.Timer_Point ='" + p_TimerPoint + "'"
            m_db_cursor = self.MetaConn.cursor()
            m_db_cursor.execute(m_SQL)
            m_rs = m_db_cursor.fetchone()
            if m_rs[0] == m_TotalParallel:
                m_db_cursor.close()
                m_TimerPointAllArrived = True
            m_db_cursor.close()

            # 如果所有进程都已经到达检查点，则标记所有进程为READY符号，否则等待其他进程标记
            if m_TimerPointAllArrived:
                if (m_JobTag is None) or (m_JobTag == ""):
                    m_SQL = "UPDATE     TESTCLI_WORKERS T " \
                            "SET        T.Timer_Point ='__READY__'" \
                            "WHERE      T.Job_ID = " + str(m_Job.id) + \
                            "AND        T.Timer_Point ='" + p_TimerPoint + "'"
                else:
                    m_SQL = "UPDATE     TESTCLI_WORKERS T " \
                            "SET        T.Timer_Point ='__READY__'" \
                            "WHERE      T.Job_Tag = '" + m_JobTag + "'" \
                            "AND        T.Timer_Point ='" + p_TimerPoint + "'"
                m_db_cursor = self.MetaConn.cursor()
                m_db_cursor.execute(m_SQL)
                m_db_cursor.close()
                self.MetaConn.commit()

            # 如果已经被其他进程标记为READY，退出等待
            m_SQL = "SELECT    COUNT(*) " \
                    "FROM      TESTCLI_WORKERS " \
                    "WHERE     ProcessID = " + str(os.getpid()) + " " + \
                    "AND       Timer_Point = '__READY__' "
            m_db_cursor = self.MetaConn.cursor()
            m_db_cursor.execute(m_SQL)
            m_rs = m_db_cursor.fetchone()
            if m_rs[0] != 0:
                m_db_cursor.close()
                break
            self.MetaConn.commit()

            # 2秒钟之后再检查Worker的状态
            time.sleep(2)

        # 离开当前等待，清空READY状态
        m_db_cursor = self.MetaConn.cursor()
        m_SQL = "UPDATE TESTCLI_WORKERS " \
                "SET    Timer_Point = Null " \
                "WHERE  ProcessID =" + str(os.getpid())
        m_db_cursor.execute(m_SQL)
        m_db_cursor.close()
        self.MetaConn.commit()

    # 判断是否所有有效的子进程都已经退出
    def isJobClosed(self, p_JobName: str):
        m_Job = self.getJobByName(p_JobName)
        if m_Job is None:
            raise TestCliException("Invalid JOB name. [" + str(p_JobName) + "]")
        return m_Job.getStatus() == "FINISHED"

    # 将当前Worker注册到指定的JOB上
    def registerjob(self, p_JobName: str):
        if self.MetaConn is None:
            raise TestCliException("You doesn't have job manager connected.")

        m_Job = self.getJobByName(p_JobName)
        if m_Job is None:
            raise TestCliException("Invalid JOB name. [" + str(p_JobName) + "]")
        # 判断TESTCLI_WORKERS中是否已经存在对应记录，如果没有，插入一条新的
        m_SQL = "SELECT    COUNT(*) " \
                "FROM      TESTCLI_WORKERS " \
                "WHERE     ProcessID = " + str(os.getpid())
        m_db_cursor = self.MetaConn.cursor()
        m_db_cursor.execute(m_SQL)
        m_rs = m_db_cursor.fetchone()
        if m_rs[0] != 0:
            m_db_cursor.close()
            raise TestCliException("You have already registerd this worker.")
        # 查找当前最大的WorkerHandler_ID
        m_SQL = "SELECT    Max(WorkerHandler_ID) " \
                "FROM      TESTCLI_WORKERS " \
                "WHERE     JOB_ID = " + str(m_Job.getJobID())
        m_db_cursor = self.MetaConn.cursor()
        m_db_cursor.execute(m_SQL)
        m_rs = m_db_cursor.fetchone()
        if m_rs[0] is None:
            m_WorkerHandler_ID = 1
        else:
            m_WorkerHandler_ID = m_rs[0] + 1
        m_db_cursor.close()

        # 在SQLCLI_WORKER中创建对应记录
        m_CurrentTime = int(time.mktime(datetime.datetime.now().timetuple()))
        m_db_cursor = self.MetaConn.cursor()
        m_SQL = "Insert into TESTCLI_WORKERS(" \
                "JOB_ID,JOB_Name, JOB_Tag, WorkerHandler_ID,ProcessID, Start_Time) " \
                "VALUES(?,?,?,?,?,?)"
        m_Data = [
            m_Job.getJobID(),
            m_Job.getJobName(),
            m_Job.getTag(),
            m_WorkerHandler_ID,
            os.getpid(),
            m_CurrentTime
        ]
        m_db_cursor.execute(m_SQL, parameters=m_Data)
        m_db_cursor.close()

        m_SQL = "UPDATE     TESTCLI_JOBS " \
                "SET        Active_JOBS = Active_JOBS + 1 " \
                "WHERE      JOB_ID = " + str(m_Job.id)
        m_db_cursor = self.MetaConn.cursor()
        m_db_cursor.execute(m_SQL)
        m_db_cursor.close()
        self.MetaConn.commit()

        # 标记当前进程为手动注册的会话
        self.isManualRegister = True

    # 退出当前的Worker作业
    def unregisterjob(self):
        if not self.isManualRegister:
            return

        if self.MetaConn is None:
            raise TestCliException("You doesn't register this worker 1.")

        m_SQL = "SELECT  JOB_ID " \
                "FROM    TESTCLI_WORKERS " \
                "WHERE   ProcessID = " + str(os.getpid())
        m_db_cursor = self.MetaConn.cursor()
        m_db_cursor.execute(m_SQL)
        m_rs = m_db_cursor.fetchone()
        if m_rs is None:
            m_db_cursor.close()
            raise TestCliException("You doesn't register this worker 2.")
        m_JobID = m_rs[0]

        m_SQL = "DELETE    FROM   TESTCLI_WORKERS " \
                "WHERE     ProcessID = " + str(os.getpid())
        m_db_cursor = self.MetaConn.cursor()
        m_db_cursor.execute(m_SQL)
        m_db_cursor.close()

        m_SQL = "UPDATE     TESTCLI_JOBS " \
                "SET        Active_JOBS = Active_JOBS -1 " \
                "WHERE      JOB_ID = " + str(m_JobID)
        m_db_cursor = self.MetaConn.cursor()
        m_db_cursor.execute(m_SQL)
        m_db_cursor.close()
        self.MetaConn.commit()

        # 取消ManualRegister的标志
        self.isManualRegister = False

    # 判断是否所有有效的子进程都已经退出
    def isAllJobClosed(self):
        # 当前有活动进程存在
        return len(self.processHandlerInfo) == 0

    def processRequest(self, cls, requestObject):
        try:
            if requestObject["action"] == "startJobmanager":
                if cls.testOptions.get("JOBMANAGER").upper() == "OFF":
                    cls.MetaHandler.StartAsServer()
                    # 标记JOB队列管理使用的数据库连接
                    if cls.MetaHandler.dbConn is not None:
                        os.environ["TESTCLI_JOBMANAGERURL"] = cls.MetaHandler.MetaURL
                        cls.JobHandler.setMetaConn(cls.MetaHandler.dbConn)
                        cls.testOptions.set("JOBMANAGER", "ON")
                        cls.testOptions.set("JOBMANAGER_METAURL", cls.MetaHandler.MetaURL)
                        yield {
                            "type": "result",
                            "title": None,
                            "rows": None,
                            "headers": None,
                            "columnTypes": None,
                            "status": "Job manager started successful."
                        }
                    else:
                        yield {
                            "type": "error",
                            "message": "Job manager started fail."
                        }
                else:
                    yield {
                        "type": "error",
                        "message": "Job manager already started. You can not start job manager again."
                    }
            if requestObject["action"] == "stopJobmanager":
                if self.MetaConn is None:
                    yield {
                        "type": "error",
                        "message": "JOB Manager is not started.",
                    }
                    return
                if cls.testOptions.get("JOBMANAGER").upper() == "ON":
                    del os.environ["TESTCLI_JOBMANAGERURL"]
                    cls.testOptions.set("JOBMANAGER", "OFF")
                    cls.testOptions.set("JOBMANAGER_METAURL", '')
                    cls.MetaHandler.ShutdownServer()
                    yield {
                        "type": "result",
                        "title": None,
                        "rows": None,
                        "headers": None,
                        "columnTypes": None,
                        "status": "Job manager stopped successful."
                    }
                else:
                    yield {
                        "type": "error",
                        "message": "Job manager already stopped. You can not stop job manager again."
                    }
            if requestObject["action"] == "show":
                if self.MetaConn is None:
                    yield {
                        "type": "error",
                        "message": "JOB Manager is not started. Please use \"_JOB JOGMANAGER ON\" first.",
                    }
                    return
                jobName = requestObject["jobName"]
                yield self.showjob(jobName)
            if requestObject["action"] == "create":
                if self.MetaConn is None:
                    yield {
                        "type": "error",
                        "message": "JOB Manager is not started. Please use \"_JOB JOGMANAGER ON\" first.",
                    }
                    return
                jobName = requestObject["jobName"]
                params = dict(requestObject["param"])
                job = self.createjob(jobName)
                for parameterName, parameterValue in params.items():
                    job.setjob(parameterName, parameterValue)
                self.SaveJob(job)
                yield {
                    "type": "result",
                    "title": None,
                    "rows": None,
                    "headers": None,
                    "columnTypes": None,
                    "status": "Job [" + jobName + "] created successful."
                }
            if requestObject["action"] == "set":
                if self.MetaConn is None:
                    yield {
                        "type": "error",
                        "message": "JOB Manager is not started. Please use \"_JOB JOGMANAGER ON\" first.",
                    }
                    return
                jobName = requestObject["jobName"]
                params = dict(requestObject["param"])
                job = self.getJobByName(jobName)
                for parameterName, parameterValue in params.items():
                    job.setjob(parameterName, parameterValue)
                self.SaveJob(job)
                yield {
                    "type": "result",
                    "title": None,
                    "rows": None,
                    "headers": None,
                    "columnTypes": None,
                    "status": "Job [" + jobName + "] set successful."
                }
            if requestObject["action"] == "start":
                if self.MetaConn is None:
                    yield {
                        "type": "error",
                        "message": "JOB Manager is not started. Please use \"_JOB JOGMANAGER ON\" first.",
                    }
                    return
                jobName = requestObject["jobName"]
                nJobStarted = self.startjob(jobName)
                yield {
                    "type": "result",
                    "title": None,
                    "rows": None,
                    "headers": None,
                    "columnTypes": None,
                    "status": "Total [" + str(nJobStarted) + "] jobs started."
                }
            if requestObject["action"] == "wait":
                if self.MetaConn is None:
                    yield {
                        "type": "error",
                        "message": "JOB Manager is not started. Please use \"_JOB JOGMANAGER ON\" first.",
                    }
                    return
                jobName = str(requestObject["jobName"])
                params = dict(requestObject["param"])
                self.waitjob(jobName, params)
                if jobName.strip().upper() == "ALL":
                    yield {
                        "type": "result",
                        "title": None,
                        "rows": None,
                        "headers": None,
                        "columnTypes": None,
                        "status": "All jobs finished."
                    }
                else:
                    yield {
                        "type": "result",
                        "title": None,
                        "rows": None,
                        "headers": None,
                        "columnTypes": None,
                        "status": "Job [" + jobName + "] finished."
                    }
            if requestObject["action"] == "shutdown":
                if self.MetaConn is None:
                    yield {
                        "type": "error",
                        "message": "JOB Manager is not started. Please use \"_JOB JOGMANAGER ON\" first.",
                    }
                    return
                jobName = requestObject["jobName"]
                nJobShutdowned = self.shutdownjob(jobName)
                yield {
                    "type": "result",
                    "title": None,
                    "rows": None,
                    "headers": None,
                    "columnTypes": None,
                    "status": "Total [" + str(nJobShutdowned) + "] jobs shutdown complete."
                }
            if requestObject["action"] == "abort":
                if self.MetaConn is None:
                    yield {
                        "type": "error",
                        "message": "JOB Manager is not started. Please use \"_JOB JOGMANAGER ON\" first.",
                    }
                    return
                jobName = requestObject["jobName"]
                nJobAbortted = self.abortjob(jobName)
                yield {
                    "type": "result",
                    "title": None,
                    "rows": None,
                    "headers": None,
                    "columnTypes": None,
                    "status": "Total [" + str(nJobAbortted) + "] jobs abort complete."
                }
            if requestObject["action"] == "timer":
                if self.MetaConn is None:
                    yield {
                        "type": "error",
                        "message": "JOB Manager is not started. Please use \"_JOB JOGMANAGER ON\" first.",
                    }
                    return
                timerPoint = requestObject["timerPoint"]
                self.waitjobtimer(timerPoint)
                yield {
                    "type": "result",
                    "title": None,
                    "rows": None,
                    "headers": None,
                    "columnTypes": None,
                    "status": "TimerPoint [" + timerPoint + "] has arrived."
                }
            if requestObject["action"] == "register":
                if self.MetaConn is None:
                    yield {
                        "type": "error",
                        "message": "JOB Manager is not started. Please use \"_JOB JOGMANAGER ON\" first.",
                    }
                    return
                jobName = requestObject["jobName"]
                self.registerjob(jobName)
                yield {
                    "type": "result",
                    "title": None,
                    "rows": None,
                    "headers": None,
                    "columnTypes": None,
                    "status": "Register worker to Job [" + str(jobName) + "] successful."
                }
            if requestObject["action"] == "deregister":
                if self.MetaConn is None:
                    yield {
                        "type": "error",
                        "message": "JOB Manager is not started. Please use \"_JOB JOGMANAGER ON\" first.",
                    }
                    return
                self.unregisterjob()
                yield {
                    "type": "result",
                    "title": None,
                    "rows": None,
                    "headers": None,
                    "columnTypes": None,
                    "status": "Worker has deregistered successful."
                }
            return
        except TestCliException as te:
            yield {
                "type": "error",
                "message": str(te)
            }
            return

    # 设置进程的启动相关上下文信息
    def setProcessContextInfo(self, p_ContextName, p_ContextValue):
        self.ProcessContextInfo[p_ContextName] = p_ContextValue

    # 获得进程的启动相关上下文信息
    def getProcessContextInfo(self, p_ContextName):
        return self.ProcessContextInfo[p_ContextName]
