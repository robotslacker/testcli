# -*- coding: utf-8 -*-
import copy
import multiprocessing
import os
import random
import shutil
import sys
import time
from robot.running.builder import RobotParser
from robot.model import SuiteVisitor
from robot import rebot_cli

from .runrobotexecutor import runRobotExecutor
from .generatereport import generateRobotReport
from .generatereport import generateIgnoredRobotReport
from .runrobotexecutor import RobotXMLSoupParser
from .htmltestreport.HtmlTestReport import HTMLTestRunner
from .htmltestreport.HtmlTestReport import TestResult
from .regressexception import RegressException

# 默认的系统最大并发作业数
DEFAULT_Max_Process = 3


class Regress(object):
    def __init__(
            self,
            maxProcess=None,
            testOptions=None,
            testBranch=None,
            logger=None,
            workerTimeout=-1,
            scriptTimeout=-1,
            targetLabel=None,
            jobList=None,
            executorMonitor=None
    ):
        if executorMonitor is None:
            executorMonitor = {}
        self.maxProcess = maxProcess
        self.taskList = []
        self.ignoredTaskList = []
        self.executorList = []
        self.testOptions = testOptions
        self.testBranch = testBranch
        self.startTime = time.time()
        self.jobName = None
        self.buildNumber = None
        self.targetLabel = targetLabel
        self.robotOptions = None
        self.jobList = jobList

        # 进程日志
        self.logger = logger

        # 进程的监控信息
        self.executorMonitor = executorMonitor

        if workerTimeout is None:
            if "TIMEOUT_WORKER" in os.environ:
                self.workerTimeout = int(os.environ["TIMEOUT_WORKER"])
            else:
                self.workerTimeout = -1
        else:
            self.workerTimeout = workerTimeout
        if scriptTimeout is None:
            if "TIMEOUT_SCRIPT" in os.environ:
                self.scriptTimeout = int(os.environ["TIMEOUT_SCRIPT"])
            else:
                self.scriptTimeout = -1
        else:
            self.scriptTimeout = scriptTimeout

    class TestCasesFinder(SuiteVisitor):
        def __init__(self):
            self.tests = []

        def visit_test(self, test):
            self.tests.append(test)

    # 整理并生成最后的测试报告
    def generateTestReport(self):
        # 备份之前的输入输出和环境信息
        stdoutFile = None
        stderrFile = None
        saved__Stdout = sys.__stdout__
        saved__Stderr = sys.__stderr__
        savedStdout = sys.stdout
        savedStderr = sys.stderr

        try:
            # 建立报告的保存目录
            reportFileDir = os.path.join(os.environ["T_WORK"], "report")
            if not os.path.exists(reportFileDir):
                os.makedirs(reportFileDir, exist_ok=True)

            # 整理报告内容
            reportFileDir = os.path.join(os.environ["T_WORK"], "report")
            if not os.path.exists(reportFileDir):
                os.makedirs(reportFileDir, exist_ok=True)

            # 切换标准输入输出到指定的文件中
            stdoutFile = open(os.path.join(
                reportFileDir, "TestReport.stdout"), 'w')
            stderrFile = open(os.path.join(
                reportFileDir, "TestReport.stderr"), 'w')
            sys.__stdout__ = stdoutFile
            sys.__stderr__ = stderrFile
            sys.stdout = stdoutFile
            sys.stderr = stderrFile

            htmlTestResult = TestResult()
            htmlTestResult.setTitle("Test Report")
            htmlTestResult.setDescription("Max Processes : " + str(self.maxProcess) + '<br>')
            htmlTestResult.targetLabel = self.targetLabel
            htmlTestResult.robotOptions = self.robotOptions
            htmlTestResult.testOptions = self.testOptions
            htmlTestResult.testBranch = self.testBranch

            self.logger.info("Processing test result ...")
            # 首先处理每个子目录
            # 测试报告是每个子目录一个报告，同时一个累计的报告
            for subdir in os.listdir(os.environ['T_WORK']):
                # 遍历所有的sub目录
                if subdir.startswith("sub_"):
                    if os.path.exists(os.path.join(os.environ['T_WORK'], subdir, subdir + ".xml")):
                        # Robot运行结果
                        self.logger.info("Generate RobotFrameWork report style ...")
                        htmlTestResult.addSuite(generateRobotReport(cls=self, reportDir=subdir))

            # 补充所有ignore的测试报告
            self.logger.info("Combing those ignored test to final report ...")
            for robotTask in self.ignoredTaskList:
                htmlTestResult.addSuite(generateIgnoredRobotReport(cls=self, ignoredRobotTask=robotTask))

            # 汇总所有的子目录到一个统一的报表上
            # 生成该测试的测试报告
            self.logger.info("Combing all test reports to one summary report ...")
            rebotArgs = []
            rebotArgs.extend(["--tagstatexclude", "owner*"])
            rebotArgs.extend(["--tagstatexclude", "feature*"])
            rebotArgs.extend(["--tagstatexclude", "priority*"])
            rebotArgs.extend(["--suitestatlevel", "2"])
            rebotArgs.extend(["--outputdir", os.environ['T_WORK']])
            rebotArgs.extend(["--logtitle", "TestReport Summary"])
            rebotArgs.extend(["--reporttitle", "TestReport Summary"])
            rebotArgs.extend(["--name", "TestReport Summary"])
            rebotArgs.extend(
                ["--log", os.path.join(reportFileDir, "summary_log.html")])
            rebotArgs.extend(
                ["--report", os.path.join(reportFileDir, "summary_report.html")])
            rebotArgs.extend(
                ["--output", os.path.join(reportFileDir, "summary_output.xml")])
            rebotArgs.append("--splitlog")
            rebotArgs.append("--nostatusrc")

            # 遍历目录，查找所有的sub开头的目录
            m_TestSubXmlList = []
            for root, dirs, files in os.walk(os.environ["T_WORK"]):
                for f in files:
                    if f.endswith(".xml") and f.startswith("sub_"):
                        m_TestSubXmlList.append(
                            os.path.abspath(os.path.join(root, str(f))))
            if len(m_TestSubXmlList) == 0:
                self.logger.error(
                    "No valid test in [" + os.environ["T_WORK"] + "].")
            else:
                rebotArgs.extend(m_TestSubXmlList)
                rebot_cli(rebotArgs, exit=False)

            # 更新测试结果到共享区域
            testReport = []
            for testSuite in htmlTestResult.TestSuites:
                testCaseReports = []
                for testcase in testSuite.getTestCases():
                    testCaseReport = {
                        "caseName": testcase.getCaseName(),
                        "caseStatus": str(testcase.getCaseStatus())
                    }
                    testCaseReports.append(testCaseReport)
                testSuiteReport = {
                    "suiteName": testSuite.getSuiteName(),
                    "passedCount": testSuite.getPassedCaseCount(),
                    "errorCount": testSuite.getErrorCaseCount(),
                    "failedCount": testSuite.getFailedCaseCount(),
                    "elapsed": testSuite.getSuiteElapsedTime(),
                    "cases": testCaseReports
                }
                testReport.append(testSuiteReport)
            self.executorMonitor["testReport"] = testReport

            # 生成报告
            htmlTestRunner = HTMLTestRunner(title="Test Report")
            htmlTestRunner.generateReport(
                result=htmlTestResult,
                output=os.path.join(reportFileDir, "report.html")
            )
            self.logger.info("Combined all test reports. Files saved at [" +
                             os.path.join(reportFileDir, "report.html") + "]")

            # 备份测试结果文件到report目录下
            self.logger.info("Backup test result to report directory ....")
            for subdir in os.listdir(os.environ['T_WORK']):
                if os.path.isdir(os.path.join(os.environ['T_WORK'], subdir)) and subdir.startswith("sub_"):
                    m_SourceReportFile = os.path.join(
                        os.environ['T_WORK'], subdir, subdir + ".html")
                    m_TargetReportFile = os.path.join(
                        os.environ['T_WORK'], reportFileDir, subdir + ".html")
                    if os.path.exists(m_SourceReportFile):
                        shutil.copyfile(m_SourceReportFile, m_TargetReportFile)
                    shutil.make_archive(
                        base_name=os.path.join(
                            os.environ['T_WORK'], reportFileDir, subdir),
                        format="tar",
                        root_dir=os.path.join(os.environ['T_WORK']),
                        base_dir=subdir
                    )
        except Exception as e:
            raise RegressException(message="Regress failed.", inner_exception=e)
        finally:
            # 还原重定向的日志
            if savedStdout:
                sys.__stdout__ = saved__Stdout
            if saved__Stderr:
                sys.__stderr__ = saved__Stderr
            if savedStdout:
                sys.stdout = savedStdout
            if savedStderr:
                sys.stderr = savedStderr
            if stdoutFile:
                stdoutFile.close()
            if stderrFile:
                stderrFile.close()

    # 运行回归测试
    def run(self):
        # 进程监控信息
        self.executorMonitor.update(
            {
                "pid": os.getpid(),
                "maxProcess": self.maxProcess,
                "scriptTimeout": self.scriptTimeout,
                "workerTimeout": self.workerTimeout,
                "jobList": self.jobList,
                "started": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "end": "",
                "running": True
            }
        )

        # 设置超时时间
        if self.scriptTimeout != -1:
            self.logger.info("Global timeout :[" + str(self.scriptTimeout) + "] seconds.")
        else:
            self.logger.info("Global timeout : [no limit].")
        if self.workerTimeout != -1:
            self.logger.info("Task timeout :[" + str(self.workerTimeout) + "] seconds.")
        else:
            self.logger.info("Task timeout : [no limit].")

        # 系统最大并发进程数
        if self.maxProcess is None:
            self.maxProcess = DEFAULT_Max_Process
            self.executorMonitor.update({"maxProcess": self.maxProcess})
        self.logger.info("Test parallelism :[" + str(self.maxProcess) + "].")

        # 构造一个字典，用来标记每个子进程的名称，方便监控作业
        executorNameList = []
        for nPos in range(self.maxProcess):
            executorNameList.append("Executor-" + format(nPos, '04d'))
        self.executorMonitor.update(
            {
                "runningJobs": {}
            }
        )
        executorNameList.sort()

        # 检索需要处理的测试文件
        # 第一次检索记录所有可能的文件
        robotFileList = []
        if self.jobList is not None:
            self.logger.info("Task list: ")
            for job in str(self.jobList).split(","):
                self.logger.info(">>  " + job)
            # Job_List分隔符可以是换行符，也可以是逗号
            self.jobList = self.jobList.replace('\n', ',')
            for jobdir in str(self.jobList).split(","):
                jobdir = jobdir.strip()
                if len(jobdir) == 0:
                    continue
                if os.path.isfile(str(jobdir)):
                    self.logger.info("Checking file: [" + str(jobdir) + "].")
                    if str(jobdir).endswith(".robot"):
                        robotFileList.append(str(os.path.abspath(jobdir)))
                elif os.path.isdir(str(jobdir)):
                    self.logger.info("Checking directory: [" + str(jobdir) + "].")
                    for root, dirs, files in os.walk(str(jobdir)):
                        for f in files:
                            if f.endswith(".robot"):
                                robotFileList.append(os.path.abspath(
                                    os.path.join(root, str(f))))
                else:
                    self.logger.warning("[" + jobdir + "] is not valid file or directory. Ignore it.")

        # 记录所有的不重复的优先级信息, 并添加任务清单
        runLevels = [100, ]   # 默认的优先级为100
        for robotFile in robotFileList:
            parser = RobotParser()
            suite = parser.parse_suite_file(source=robotFile)
            testCaseList = self.TestCasesFinder()
            suite.remove_empty_suites(True)
            suite.visit(testCaseList)
            if len(testCaseList.tests) <= 0:
                # filter again with no excluded tags
                parser = RobotParser()
                suite = parser.parse_suite_file(source=robotFile)
                testCaseList = self.TestCasesFinder()
                suite.remove_empty_suites(True)
                suite.visit(testCaseList)
                self.ignoredTaskList.append(
                    {
                        "robotfile": robotFile,
                        "validcase": 0,
                        "Suite_Name": suite.name,
                        "runLevel": 0,
                        "workingDirectory": ""
                    })
                self.logger.info(
                    "Ignore test file [" + str(robotFile) + ":" + str(len(testCaseList.tests)) +
                    "]. no valid test cases.")
                continue

            # 检查Tag信息
            # 只要找到一个runLevel，就认为整个Robot都是这个runLevel
            runLevel = None
            for robotTest in testCaseList.tests:
                for tag in robotTest.tags:
                    tag = str(tag).strip().upper()
                    if tag.startswith("RUNLEVEL:"):
                        try:
                            if runLevel is None:
                                runLevel = int(tag[9:].strip())
                        except ValueError:
                            self.logger.warning("测试脚本中未定义有效的runLevel信息："
                                                "【" + str(robotFile) + ":" + str(robotTest.name) +
                                                "-" + str(tag) + "】")

            # 没有指定的优先级默认是100
            if runLevel is None:
                runLevel = 100
            if runLevel not in runLevels:
                runLevels.append(runLevel)
            m_RobotRelFile = robotFile.replace("\\", "/")
            testName = os.path.basename(robotFile)[:-len(".robot")]
            workingFolderName = "sub_" + testName + \
                "_" + str(random.randint(100000, 999999))
            self.taskList.append({
                "robotfile": robotFile,
                "robotrelfile": m_RobotRelFile,
                "validcase": len(testCaseList.tests),
                "Suite_Name": suite.name,
                "runLevel": runLevel,
                "workingDirectory": workingFolderName
            })
            self.logger.info("Task [" + str(robotFile) + "] " +
                             "include [" + str(len(testCaseList.tests)) + "] valid test cases.")

        # 处理没有完成的JOB
        def AnalyzeBrokenTest(test_robot_id: int, workingDirectory: str):
            # 如果测试目录都没有建立起来，这里建立一个空目录
            if not os.path.exists(os.path.join(os.getenv("T_WORK"), workingDirectory)):
                os.makedirs(os.path.join(os.getenv("T_WORK"),
                            workingDirectory), exist_ok=True)

            # 处理掉损坏的XML文件，由于Robot运行(超时退出)不完整导致的
            inputxmlfile = os.path.join(
                os.getenv("T_WORK"),  workingDirectory, workingDirectory + ".xml")
            if not os.path.exists(inputxmlfile):
                self.logger.error("Robot [" + str(test_robot_id) + "] has failed with fatal error. " +
                                  "No result files found.")
            else:
                self.logger.info("结果文件 【" + str(inputxmlfile) + "】 不完整，会尝试修正.")
                outputxmlfile = inputxmlfile
                with open(inputxmlfile, encoding="UTF-8", mode="r") as robotBrokenXMLFile:
                    fixedRobotBrokenXMLFile = str(
                        RobotXMLSoupParser(robotBrokenXMLFile, features='xml'))
                with open(outputxmlfile, encoding="UTF-8", mode='w') as robotBrokenXMLFile:
                    robotBrokenXMLFile.write(fixedRobotBrokenXMLFile)

        # 在执行的过程中检查进程的超时情况
        def check_timeout():
            """ check_timeout """
            currentDateTime = time.time()
            if self.scriptTimeout != -1:
                if (currentDateTime - self.startTime) > self.scriptTimeout:
                    # 运行已经超过了系统的最大限制
                    for timeoutExecutor in self.executorList:
                        if not timeoutExecutor["Process"].is_alive():
                            # Python3.6不支持close
                            if sys.version_info[0] == 3 and sys.version_info[1] >= 8:
                                timeoutExecutor["Process"].close()
                            runningJobsTimeout = self.executorMonitor["runningJobs"]
                            del runningJobsTimeout[timeoutExecutor["executorName"]]
                            self.executorMonitor["runningJobs"] = copy.copy(runningJobsTimeout)
                            self.executorMonitor.update(
                                {"taskLeft": self.executorMonitor["taskLeft"] - 1}
                            )
                            self.executorList.remove(timeoutExecutor)
                        else:
                            # 强行终止进程
                            self.logger.error("Executor(" + str(timeoutExecutor["Process"].pid).rjust(8, ' ') +
                                              ") has run over script limit [" + str(
                                                  self.scriptTimeout) + "] seconds, "
                                              + "terminate the [" + str(timeoutExecutor["testrobot"]) + "] " +
                                              str(timeoutExecutor["args"]["robotId"]))
                            timeoutExecutor["Process"].terminate()
                            AnalyzeBrokenTest(
                                test_robot_id=timeoutExecutor["args"]["robotId"],
                                workingDirectory=timeoutExecutor["args"]["workingDirectory"])
            if self.workerTimeout != -1:
                for timeoutExecutor in self.executorList:
                    if (currentDateTime - timeoutExecutor["Start_Time"]) > self.workerTimeout:
                        if not timeoutExecutor["Process"].is_alive():
                            # Python3.6不支持close
                            if sys.version_info[0] == 3 and sys.version_info[1] >= 8:
                                timeoutExecutor["Process"].close()
                            # 进程已经结束，记录进程运行结果
                            runningJobsTimeout = self.executorMonitor["runningJobs"]
                            del runningJobsTimeout[timeoutExecutor["executorName"]]
                            self.executorMonitor["runningJobs"] = copy.copy(runningJobsTimeout)
                            self.executorMonitor.update(
                                {"taskLeft": self.executorMonitor["taskLeft"] - 1}
                            )
                            self.executorList.remove(timeoutExecutor)
                        else:
                            # 强行终止进程
                            self.logger.error("Executor(" + str(timeoutExecutor["Process"].pid).rjust(8, ' ') +
                                              ") has run over worker limit [" + str(
                                                  self.workerTimeout) + "] seconds, "
                                              + "terminate the [" + str(timeoutExecutor["testrobot"]) + "]")
                            timeoutExecutor["Process"].terminate()
                            AnalyzeBrokenTest(
                                test_robot_id=timeoutExecutor["args"]["robotId"],
                                workingDirectory=timeoutExecutor["args"]["workingDirectory"])
            """ check_timeout """

        # 循环处理任务
        self.executorMonitor.update({"taskCount": len(self.taskList)})
        self.executorMonitor.update({"taskLeft": len(self.taskList)})
        self.executorMonitor.update({"runLevelCount": len(runLevels)})
        self.executorMonitor.update({"runLevelLeft": len(runLevels)})

        self.logger.info("Totally [" + str(self.executorMonitor["taskCount"]) + "] in task TODO list ...")

        # 按照运行级别来分别开始运行
        runLevels.sort()
        if len(runLevels) != 1:
            self.logger.info("You have defined multi runLevel [" + str(runLevels) + "], will run order by runlevel.")
        taskPos = 1
        for runLevel in runLevels:
            self.logger.info("Process tasks in runlevel [" + str(runLevel) + "] ...")
            for nPos in range(0, len(self.taskList)):
                if self.taskList[nPos]["runLevel"] != runLevel:
                    continue
                # 循环等待，一直到有空闲的进程可以来工作
                while True:
                    # 检查是否有超时的进程，如果有，则处理
                    check_timeout()
                    # 移除已经结束的进程列表
                    for executor in self.executorList:
                        if not executor["Process"].is_alive():
                            if sys.version_info[0] == 3 and sys.version_info[1] >= 8:
                                # close函数只有Python3.8才开始支持
                                executor["Process"].close()
                            runningJobs = self.executorMonitor["runningJobs"]
                            del runningJobs[executor["executorName"]]
                            self.executorMonitor["runningJobs"] = copy.copy(runningJobs)
                            self.executorMonitor.update(
                                {"taskLeft": self.executorMonitor["taskLeft"] - 1}
                            )
                            self.executorList.remove(executor)
                    if len(self.executorList) >= self.maxProcess:
                        # 如果超过了最大进程数限制，则等待
                        time.sleep(3)
                    else:
                        executorsActive = []
                        for executor in self.executorList:
                            executorsActive.append(executor["executorName"])
                        executorsActive.sort()
                        executorName = list(set(executorNameList) - set(executorsActive))[0]
                        break

                self.logger.info("Begin to execute robot test [" + str(taskPos) + "/" + str(len(self.taskList)) + "] "
                                 + self.taskList[nPos]["robotfile"] + " ...")
                taskPos = taskPos + 1
                processManagerContext = multiprocessing.get_context("spawn")
                args = {
                    "testrobot": str(self.taskList[nPos]["robotfile"]),
                    "robotOptions": self.robotOptions,
                    "workingDirectory": self.taskList[nPos]["workingDirectory"]
                }
                process = processManagerContext.Process(
                    target=runRobotExecutor,
                    args=(args,)
                )
                process.start()
                self.executorList.append(
                    {
                        "Process": process,
                        "testrobot":  str(self.taskList[nPos]["robotfile"]),
                        "Start_Time": time.time(),
                        "workingDirectory": self.taskList[nPos]["workingDirectory"],
                        "executorName": executorName,
                        "args": args
                    })
                runningJobs = self.executorMonitor["runningJobs"]
                runningJobs.update(
                    {
                        executorName:
                            {
                                "script": str(self.taskList[nPos]["robotfile"]),
                                "workingDirectory": self.taskList[nPos]["workingDirectory"],
                                "pid": process.pid,
                                "started": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                            }
                    }
                )
                self.executorMonitor["runningJobs"] = copy.copy(runningJobs)
            self.executorMonitor.update({"runLevelLeft": self.executorMonitor["runLevelLeft"] - 1})
            self.logger.info("All tasks in run level [" + str(runLevel) + "] have completed.")

            while True:
                # 移除已经结束的进程列表
                for executor in self.executorList:
                    if not executor["Process"].is_alive():
                        # 进程已经结束，记录进程运行结果
                        runningJobs = self.executorMonitor["runningJobs"]
                        del runningJobs[executor["executorName"]]
                        self.executorMonitor["runningJobs"] = copy.copy(runningJobs)
                        self.executorMonitor.update(
                            {"taskLeft": self.executorMonitor["taskLeft"] - 1}
                        )
                        self.executorList.remove(executor)
                if len(self.executorList) == 0:
                    break
                else:
                    # 休息3秒钟
                    time.sleep(3)
                    # 检查是否有超时的进程，如果有，则处理
                    check_timeout()
