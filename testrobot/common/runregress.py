# -*- coding: utf-8 -*-
import multiprocessing
import os
import random
import shutil
import sys
import time
import logging
import coloredlogs
from robot.running.builder import RobotParser
from robot.model import SuiteVisitor
from robot import rebot_cli

from .runrobotexecutor import runRobotExecutor
from .generatereport import generateRobotReport
from .generatereport import generateIgnoredRobotReport
from .runrobotexecutor import RobotXMLSoupParser
from .htmltestreport.HtmlTestReport import HTMLTestRunner
from .htmltestreport.HtmlTestReport import TestResult

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
    ):
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

        # 最后一次检查脚本放弃的时间
        self.lastCheckAbortStatusPoint = time.time()

        if logger is None:
            # 设置程序的日志级别
            os.environ["COLOREDLOGS_LEVEL_STYLES"] = \
                "spam=22;debug=28;verbose=34;notice=220;warning=202;success=118,bold;" \
                "error=background=red,bold;critical=background=red"

            LOG_FORMAT = "%(asctime)s -  %(name)15s-[%(process)8d] - %(levelname)9s - %(message)s"
            fFormat = logging.Formatter(LOG_FORMAT)
            consoleLogHandler = logging.StreamHandler()
            consoleLogHandler.setFormatter(fFormat)
            # 默认日志输出级别是INFO级别
            if "LOG_LEVEL" not in os.environ:
                logLevel = "INFO"
            else:
                logLevel = os.environ["LOG_LEVEL"].upper().strip()
            if logLevel == "INFO":
                consoleLogHandler.setLevel(logging.INFO)
            elif logLevel == "DEBUG":
                consoleLogHandler.setLevel(logging.DEBUG)
            elif logLevel == "WARNING":
                consoleLogHandler.setLevel(logging.WARNING)
            elif logLevel == "ERROR":
                consoleLogHandler.setLevel(logging.ERROR)
            elif logLevel == "CRITICAL":
                consoleLogHandler.setLevel(logging.CRITICAL)
            else:
                logging.error(
                    "UNKNOWN log level [" + logLevel + "]. must in [INFO|DEBUG|WARING|ERROR|CRITICAL].")
                return
            self.logger = logging.getLogger("runRegress")
            # self.logger.addHandler(consoleLogHandler)
            coloredlogs.install(
                level=consoleLogHandler.level,
                fmt=LOG_FORMAT,
                logger=self.logger,
                isatty=True
            )
            self.logger.info("当前日志级别：【" + logLevel + "】")
        else:
            self.logger = logger

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

    def run(self):
        self.logger.info("自动化回归测试开始 .....")

        # 设置超时时间
        if self.scriptTimeout != -1:
            self.logger.info("全局超时时间设置 :【" + str(self.scriptTimeout) + "】秒.")
        else:
            self.logger.info("全局超时时间设置 :【不限制】")
        if self.workerTimeout != -1:
            self.logger.info("脚本超时时间设置 :【" + str(self.workerTimeout) + "】秒.")
        else:
            self.logger.info("脚本超时时间设置 :【不限制】")
        self.logger.info("最大进程并发设置 :【" + str(self.maxProcess) + "】路.")

        # 系统最大并发进程数
        if self.maxProcess is None:
            self.maxProcess = DEFAULT_Max_Process
        self.logger.info("系统并发进程数: 【" + str(self.maxProcess) + "】")

        # 检索需要处理的测试文件
        # 第一次检索记录所有可能的文件
        robotFileList = []
        if self.jobList is not None:
            self.logger.info("任务列表: ")
            for job in str(self.jobList).split(","):
                self.logger.info(">>  " + job)
            # Job_List分隔符可以是换行符，也可以是逗号
            self.jobList = self.jobList.replace('\n', ',')
            for jobdir in str(self.jobList).split(","):
                jobdir = jobdir.strip()
                if len(jobdir) == 0:
                    continue
                if os.path.isfile(str(jobdir)):
                    self.logger.info("检查文件有效性 : 【" + str(jobdir) + "】")
                    if str(jobdir).endswith(".robot"):
                        robotFileList.append(str(os.path.abspath(jobdir)))
                elif os.path.isdir(str(jobdir)):
                    self.logger.info("检查目录（包含子目录）有效性: 【" + str(jobdir) + "】")
                    for root, dirs, files in os.walk(str(jobdir)):
                        for f in files:
                            if f.endswith(".robot"):
                                robotFileList.append(os.path.abspath(
                                    os.path.join(root, str(f))))
                elif os.path.isfile(os.path.join(os.environ["WORKSPACE"], str(jobdir))):
                    self.logger.info("检查文件有效性 : 【" + os.path.join(os.environ["WORKSPACE"], str(jobdir)) + "】")
                    if str(jobdir).endswith(".robot"):
                        robotFileList.append(str(os.path.abspath(os.path.join(os.environ["WORKSPACE"], str(jobdir)))))
                elif os.path.isdir(os.path.join(os.environ["WORKSPACE"], str(jobdir))):
                    self.logger.info("检查目录（包含子目录）有效性: 【" +
                                     os.path.join(os.environ["WORKSPACE"], str(jobdir)) + "】")
                    for root, dirs, files in os.walk(os.path.join(os.environ["WORKSPACE"], str(jobdir))):
                        for f in files:
                            if f.endswith(".robot"):
                                robotFileList.append(os.path.abspath(
                                    os.path.join(root, str(f))))
                else:
                    self.logger.error(os.path.join(os.environ["WORKSPACE"], str(jobdir)))
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
            self.logger.info("测试脚本 【" + str(robotFile) + "】 " +
                             "中包含了【" + str(len(testCaseList.tests)) + "】个有效测试用例.")

        # 清理工作目录
        workDirectory = os.environ["T_WORK"]
        self.logger.info("将清理工作目录 【" + workDirectory + "】， 该目录下所有文件都将会被清空...")
        if os.path.exists(workDirectory):
            files = os.listdir(workDirectory)
            for file in files:
                filePath = os.path.join(workDirectory, file)
                if os.path.isdir(filePath):
                    shutil.rmtree(path=filePath, ignore_errors=True)
                else:
                    # 删除具体某一个文件， 不会删除.gitignore文件
                    if os.path.basename(file) == ".gitignore":
                        continue
                    os.remove(filePath)

        # 在执行的过程中不断打印出执行的统计情况
        def print_statistics(p_TestStatistics):
            if len(p_TestStatistics) == 0:
                self.logger.info("统计信息:: 当前已经完成测试 ----. 任务成功率 ----")
            else:
                successfulCaseCount = 0
                totalCaseCount = 0
                for testResults in testStatistics:
                    for testResult in testResults:
                        totalCaseCount = totalCaseCount + 1
                        if testResult["Case_Status"] == "SUCCESS":
                            successfulCaseCount = successfulCaseCount + 1
                if totalCaseCount != 0:
                    self.logger.info("统计信息:: 共完成"
                                     " 测试用例:【" + str(totalCaseCount) + "】 测试任务:【" + str(len(testStatistics)) + "】" +
                                     "任务成功率:【" +
                                     "%6.2f" % (successfulCaseCount * 100 / totalCaseCount) + "%】.")

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
                            # timeoutExecutor["Process"].close()
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
                            # timeoutExecutor["Process"].close()
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
        self.logger.info("共有 【" + str(len(self.taskList)) + "】 个未完成任务在任务清单中 ...")
        testStatistics = multiprocessing.Manager().list()
        lastPrintStatisticsTime = time.time()
        printStatisticsInterval = 120
        self.logger.info("runLevels = [" + str(runLevels) + "]")
        runLevels.sort()
        if len(runLevels) != 1:
            self.logger.info("系统定义了多个【" + str(len(runLevels)) + "】运行级别. 将按照运行级别运行测试用例.")
        taskPos = 1
        for runLevel in runLevels:
            self.logger.info("处理运行级别为【" + str(runLevel) + "】的测试...")
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
                            # close函数只有Python3.8才开始支持
                            # executor["Process"].close()
                            self.executorList.remove(executor)
                    # 如果超过了最大进程数限制，则等待
                    if len(self.executorList) >= self.maxProcess:
                        if time.time() - lastPrintStatisticsTime > printStatisticsInterval:
                            print_statistics(testStatistics)
                            lastPrintStatisticsTime = time.time()
                        time.sleep(3)
                    else:
                        break

                self.logger.info("开始执行Robot测试 【" + str(taskPos) + "/" + str(len(self.taskList)) + "】 "
                                 + self.taskList[nPos]["robotfile"] + " ...")
                taskPos = taskPos + 1
                processManagerContext = multiprocessing.get_context("spawn")
                args = {
                    "testrobot": str(self.taskList[nPos]["robotfile"]),
                    "statistics": testStatistics,
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
                        "args": args
                    })

            # 完成所有的测试
            while True:
                # 移除已经结束的进程列表
                for executor in self.executorList:
                    if not executor["Process"].is_alive():
                        # 进程已经结束，记录进程运行结果
                        self.executorList.remove(executor)
                if len(self.executorList) == 0:
                    break
                else:
                    if time.time() - lastPrintStatisticsTime > printStatisticsInterval:
                        print_statistics(testStatistics)
                        lastPrintStatisticsTime = time.time()
                    time.sleep(3)
                    # 检查是否有超时的进程，如果有，则处理
                    check_timeout()
            self.logger.info("当前运行级别的所有测试均已经完成...")
            print_statistics(testStatistics)

        self.logger.info("所有测试任务已经完成.")
        print_statistics(testStatistics)

        # 建立报告的保存目录
        reportFileDir = os.path.join(os.environ["T_WORK"], "report")
        if not os.path.exists(reportFileDir):
            os.makedirs(reportFileDir, exist_ok=True)

        # 整理报告内容
        reportFileDir = os.path.join(os.environ["T_WORK"], "report")
        if not os.path.exists(reportFileDir):
            os.makedirs(reportFileDir, exist_ok=True)

        # 重定向报告生成过程中的日志
        stdoutFile = open(os.path.join(
            reportFileDir, "TestReport.stdout"), 'w')
        stderrFile = open(os.path.join(
            reportFileDir, "TestReport.stderr"), 'w')
        saved__Stdout = sys.__stdout__
        saved__Stderr = sys.__stderr__
        savedStdout = sys.stdout
        savedStderr = sys.stderr
        sys.__stdout__ = stdoutFile
        sys.__stderr__ = stderrFile
        sys.stdout = stdoutFile
        sys.stderr = stderrFile

        try:
            htmlTestResult = TestResult()
            htmlTestResult.setTitle("测试报告")
            htmlTestResult.setDescription("最大进程数  : " + str(self.maxProcess) + '<br>')
            htmlTestResult.targetLabel = self.targetLabel
            htmlTestResult.robotOptions = self.robotOptions
            htmlTestResult.testOptions = self.testOptions
            htmlTestResult.testBranch = self.testBranch

            self.logger.info("处理测试报告.")
            # 首先处理每个子目录
            # 测试报告是每个子目录一个报告，同时一个累计的报告
            for subdir in os.listdir(os.environ['T_WORK']):
                # 遍历所有的sub目录
                if subdir.startswith("sub_"):
                    if os.path.exists(os.path.join(os.environ['T_WORK'], subdir, subdir + ".xml")):
                        # Robot运行结果
                        self.logger.info("生成Robot测试报告中...")
                        htmlTestResult.addSuite(generateRobotReport(cls=self, reportDir=subdir))
            # 补充所有ignore的测试报告
            self.logger.info("合并那些被忽略的测试项目到测试报告中...")
            for robotTask in self.ignoredTaskList:
                htmlTestResult.addSuite(generateIgnoredRobotReport(cls=self, ignoredRobotTask=robotTask))

            # 汇总所有的子目录到一个统一的报表上
            # 生成该测试的测试报告
            self.logger.info("合并所有的测试内容到一个完整的报告上....")
            rebotArgs = []
            rebotArgs.extend(["--tagstatexclude", "owner*"])
            rebotArgs.extend(["--tagstatexclude", "feature*"])
            rebotArgs.extend(["--tagstatexclude", "priority*"])
            rebotArgs.extend(["--suitestatlevel", "2"])
            rebotArgs.extend(["--outputdir", os.environ['T_WORK']])
            rebotArgs.extend(["--logtitle", "测试报告-汇总"])
            rebotArgs.extend(["--reporttitle", "测试报告-汇总"])
            rebotArgs.extend(["--name", "测试报告-汇总"])
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

            # 生成报告
            htmlTestRunner = HTMLTestRunner(title="测试报告")
            htmlTestRunner.generateReport(
                result=htmlTestResult,
                output=os.path.join(reportFileDir, "report.html")
            )
            self.logger.info("为本次测试生成汇总的测试报告. 报告文件放置在【" +
                             os.path.join(reportFileDir, "report.html") + "】")

            # 备份测试结果文件到report目录下
            self.logger.info("备份测试结果文件到报告目录....")
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
            self.logger.info("程序顺利运行结束.")
        except Exception as e:
            self.logger.error("测试报告生成错误：", e)

        # 还原重定向的日志
        sys.__stdout__ = saved__Stdout
        sys.__stderr__ = saved__Stderr
        sys.stdout = savedStdout
        sys.stderr = savedStderr
        stdoutFile.close()
        stderrFile.close()
