# -*- coding: utf-8 -*-
import copy
import multiprocessing
import os
import logging
import platform
import random
import shutil
import sys
import time
import datetime
import json
import threading

import psutil
import robot.errors
from robot.api import TestSuiteBuilder
from robot.api import ExecutionResult
from robot import rebot_cli

from .runrobotexecutor import runRobotExecutor
from .htmltestreport.HtmlTestReport import HTMLTestRunner
from .htmltestreport.HtmlTestReport import TestResult
from .regressexception import RegressException
from .htmltestreport.HtmlTestReport import TestSuite
from .htmltestreport.HtmlTestReport import TestCase
from .htmltestreport.HtmlTestReport import TestCaseStatus
from .runrobotexecutor import RobotXMLSoupParser
from .junitreport.JunitTestReport import TestSuite as JunitTestSuite
from .junitreport.JunitTestReport import TestCase as JunitTestCase

# 默认的系统最大并发作业数
DEFAULT_MAX_PROCESS = 3
# 默认的系统最大报告汇总进程数量
DEFAULT_MAX_REPORTER = int(psutil.cpu_count() / 2)


class Regress(object):
    def __init__(
            self,
            jobList,
            workDirectory: str,
            testRoot=None,
            maxProcess=None,
            robotOptions=None,
            logger=None,
            workerTimeout=-1,
            scriptTimeout=-1,
            executorMonitor=None,
            reportType="HTML,JUNIT",
            reportLevel="Case",
            testRunId=0
    ):
        if executorMonitor is None:
            executorMonitor = {}
        self.maxProcess = maxProcess
        self.taskList = []
        self.ignoredTaskList = []
        self.executorList = []
        self.startTime = time.time()
        self.jobName = None
        self.robotOptions = robotOptions
        if isinstance(jobList, list):
            self.jobList = jobList
        else:
            self.jobList = str(jobList).split(",")
        self.workDirectory = workDirectory
        self.testRoot = testRoot
        self.testRunId = testRunId

        # 进程日志
        if logger is not None:
            self.logger = logger
        else:
            # 没有提供日志句柄，则直接打印到控制台
            self.logger = logging.getLogger("runRegress")

        # 进程的监控信息
        self.executorMonitor = executorMonitor

        # 生成报告的时候考虑并发，来提高生成效率。但是要控制线程冲突
        self.semGenerateReport = threading.Semaphore(DEFAULT_MAX_REPORTER)
        self.lockGenerateReport = threading.Lock()

        # 设置进程的超时时间
        if workerTimeout is None:
            if "TIMEOUT_WORKER" in os.environ:
                self.workerTimeout = int(os.environ["TIMEOUT_WORKER"])
            else:
                self.workerTimeout = -1
        else:
            self.workerTimeout = int(workerTimeout)
        if scriptTimeout is None:
            if "TIMEOUT_SCRIPT" in os.environ:
                self.scriptTimeout = int(os.environ["TIMEOUT_SCRIPT"])
            else:
                self.scriptTimeout = -1
        else:
            self.scriptTimeout = int(scriptTimeout)

        # 设置报告的展示类型
        if reportType is None:
            self.reportTypes = []
        else:
            s = str(reportType).split(',')
            self.reportTypes = [i.upper().strip() for i in s if (i is not None) and (str(i).strip() != '')]
        for s in self.reportTypes:
            if s not in ["JUNIT", "HTML"]:
                raise RegressException("Invalid reportType.  Only support JUNIT and HTML.")

        # 设置报告的展示级别（仅对Junit报告有意义）
        self.reportLevel = None
        if reportLevel is not None:
            self.reportLevel = reportLevel.strip().upper()
        if self.reportLevel not in ["CASE", "SCENARIO"]:
            raise RegressException("Invalid reportLevel.  Case or Scenario only.")

    def generateRobotReport(
            self,
            robotTask,
            htmlTestResult
    ):
        with self.semGenerateReport:
            # 不能有太多的并发来处理这个报告，避免CPU的过度消耗
            self.logger.info("  Processing robot result file under [" + str(robotTask["workingDirectory"]) + "] ...")

            htmlTestSuite = TestSuite()
            # 记录源文件名，相对路径
            htmlTestSuite.setSuiteSource(str(os.path.relpath(robotTask["robotFile"], self.testRoot)))

            # 对于测试运行中过滤掉的Case，也不会显示在html报告中
            filteredTags = []
            if self.robotOptions is not None:
                robotOptionList = str(self.robotOptions).split()
                for pos in range(0, len(robotOptionList)):
                    if robotOptionList[pos] == "--exclude" and pos < (len(robotOptionList) - 1):
                        filteredTags.append(robotOptionList[pos+1])

            # 解析Robot文件，假设悲观原则，即所有测试都失败。失败了也要给测试报告
            robotSourceSuite = TestSuiteBuilder().build(robotTask["robotFile"])
            htmlTestSuite.setSuiteName(robotSourceSuite.name)
            metaData = {}
            for metaKey, metaValue in robotSourceSuite.metadata.items():
                metaData.update(
                    {
                        metaKey: metaValue
                    }
                )
            htmlTestSuite.setSuiteMeta(metaData)

            testOwnerMap = {}
            for testCase in robotSourceSuite.tests:
                htmlTestCase = TestCase()
                htmlTestCase.setCaseName(testCase.name)
                htmlTestCase.setCaseStatus(TestCaseStatus.ERROR)
                testOwner = None
                isFilteredCase = False
                for resultTestCaseTag in testCase.tags:
                    if resultTestCaseTag in filteredTags:
                        isFilteredCase = True
                    if str(resultTestCaseTag).lower().startswith('owner:'):
                        if testOwner is None:
                            testOwner = resultTestCaseTag[6:].strip()
                            testOwnerMap.update(
                                {
                                    testCase.name: testOwner
                                }
                            )
                if not isFilteredCase:
                    htmlTestCase.setCaseOwner(testOwner)
                    htmlTestCase.setCaseStartTime("____-__-__ __:__:__")
                    htmlTestCase.setCaseElapsedTime(0)
                    htmlTestCase.setErrorStackTrace("Not started.")
                    htmlTestCase.setDownloadURLLink("javascript:void(0)")
                    htmlTestCase.setDetailReportLink("javascript:void(0)")
                    htmlTestSuite.addTestCase(htmlTestCase)

            # 用正确的结果来更新测试报告
            xmlResultFile = \
                os.path.join(self.workDirectory,
                             robotTask["workingDirectory"],
                             os.path.basename(robotTask["workingDirectory"]) + ".xml")
            if os.path.exists(xmlResultFile):
                try:
                    self.logger.info("  Analyze report file [" + xmlResultFile + "] ....")
                    robotResults = ExecutionResult(xmlResultFile)
                except robot.errors.DataError:
                    # 文件不完整，修正XML后重新运行
                    self.logger.error("Result file [" + str(xmlResultFile) + "] is incomplete xml file, fix it.")
                    with open(xmlResultFile, encoding="UTF-8", mode="r") as infile:
                        fixed = str(RobotXMLSoupParser(infile, features='xml'))
                    with open(xmlResultFile, encoding="UTF-8", mode='w') as outfile:
                        outfile.write(fixed)
                    try:
                        robotResults = ExecutionResult(xmlResultFile)
                    except robot.errors.DataError:
                        # 文件存在问题，还是无法解析
                        self.logger.error("Result file [" + str(xmlResultFile) + "] is not valid xml file, ignore it.")
                        return

                robotSuiteResultList = []
                if len(robotResults.suite.suites) == 0:
                    robotSuiteResultList.append(robotResults.suite)
                else:
                    for resultTestSuite in robotResults.suite.suites:
                        robotSuiteResultList.append(resultTestSuite)
                for robotSuiteResult in robotSuiteResultList:
                    for robotCaseResult in robotSuiteResult.tests:
                        robotCaseFinished = True
                        htmlTestCase = TestCase()
                        htmlTestCase.setCaseName(robotCaseResult.name)

                        # 获得测试的Owner
                        if robotCaseResult.name in testOwnerMap.keys():
                            testOwner = testOwnerMap[robotCaseResult.name]
                        else:
                            testOwner = "UNKNOWN"
                        htmlTestCase.setCaseOwner(testOwner)

                        if robotCaseResult.status == "FAIL":
                            htmlTestCase.setCaseStatus(
                                TestCaseStatus.FAILURE)
                        elif robotCaseResult.status == "PASS":
                            htmlTestCase.setCaseStatus(
                                TestCaseStatus.SUCCESS)
                        else:
                            htmlTestCase.setCaseStatus(
                                TestCaseStatus.ERROR)
                        if robotCaseResult.starttime is not None:
                            startTime = datetime.datetime.strptime(robotCaseResult.starttime[:17], "%Y%m%d %H:%M:%S")
                        else:
                            # 不确定的test开始时间, 可能是由于Case没有运行完成，robot文件损坏
                            # 这时将Robot的开始时间作为test的开始时间,并且标记测试为失败
                            startTime = datetime.datetime.fromtimestamp(os.path.getctime(xmlResultFile))
                            htmlTestCase.setCaseStatus(TestCaseStatus.ERROR)
                            robotCaseFinished = False
                        htmlTestCase.setCaseStartTime(
                            startTime.strftime("%Y-%m-%d %H:%M:%S"))
                        if robotCaseResult.endtime is not None:
                            endTime = \
                                datetime.datetime.strptime(
                                    robotCaseResult.endtime[:17], "%Y%m%d %H:%M:%S")
                        else:
                            # 如果无法得到test的结束时间，可能是由于Case没有运行完成，robot文件损坏
                            # 这时将xml文件的最后修改时间，作为test的结束时间,并且标记测试为失败
                            endTime = datetime.datetime.fromtimestamp(os.path.getmtime(xmlResultFile))
                            htmlTestCase.setCaseStatus(TestCaseStatus.ERROR)
                            robotCaseFinished = False
                        htmlTestCase.setCaseElapsedTime(
                            (endTime - startTime).seconds)
                        if not robotCaseFinished:
                            htmlTestCase.setErrorStackTrace("Fatal error， Test has been TIMEOUT terminated.")
                        else:
                            htmlTestCase.setErrorStackTrace(
                                robotSuiteResult.message)
                        subHtmlReportFile = \
                            os.path.join(
                                robotTask["workingDirectory"],
                                os.path.basename(robotTask["workingDirectory"]) + ".html"
                            )

                        # 生成该测试的测试报告
                        resultRebotArgs = []
                        resultRebotArgs.extend(
                            ["--tagstatexclude", "owner*"])
                        resultRebotArgs.extend(
                            ["--tagstatexclude", "feature*"])
                        resultRebotArgs.extend(
                            ["--tagstatexclude", "runLevel*"])
                        resultRebotArgs.extend(
                            ["--tagstatexclude", "priority*"])
                        resultRebotArgs.extend(["--suitestatlevel", "2"])
                        resultRebotArgs.extend(
                            ["--outputdir", self.workDirectory])
                        resultRebotArgs.extend(
                            ["--logtitle", "Test Report-" + robotSuiteResult.name])
                        resultRebotArgs.extend(
                            ["--reporttitle", "Test Report-" + robotSuiteResult.name])
                        resultRebotArgs.extend(
                            ["--name", "Test Report-" + robotSuiteResult.name])
                        resultRebotArgs.extend(["--log", subHtmlReportFile])
                        resultRebotArgs.extend(["--report", "NONE"])
                        resultRebotArgs.extend(["--output", "NONE"])
                        resultRebotArgs.append("--nostatusrc")

                        # 生成测试报告参数
                        resultXmlList = [os.path.abspath(xmlResultFile)]
                        resultRebotArgs.extend(resultXmlList)

                        # 生成测试报告
                        print("Execute Rebot_Cli: ")
                        for arg in resultRebotArgs:
                            print("    " + str(arg))
                        rebot_cli(resultRebotArgs, exit=False)

                        htmlTestCase.setDetailReportLink(robotTask["workingDirectory"] + ".html#" + robotCaseResult.id)
                        htmlTestCase.setDownloadURLLink(robotTask["workingDirectory"] + ".tar")
                        htmlTestSuite.addTestCase(htmlTestCase)

            # 汇总运行结果
            htmlTestSuite.SummaryTestCase()

            # 更新引用中的信息
            with self.lockGenerateReport:
                # 合并报告的时候无法采用并发
                htmlTestResult.addSuite(htmlTestSuite)

    # 测试报告预处理，生成扩展信息文件
    def generateJunitReport(self):
        # 为Junit单独准备一个目录，来放置Junit结果
        jUnitReportDir = os.path.join(self.workDirectory, "report", "junitreport")
        if not os.path.exists(jUnitReportDir):
            os.makedirs(jUnitReportDir)
        JunitReportFile = os.path.join(jUnitReportDir, "junit.xml")

        if self.reportLevel == "CASE":
            # 直接用Robot的xml作为Junit报告的基础
            # 遍历目录来获取Junit测试结果
            jUnitTestSuites = []
            subDirs = os.listdir(self.workDirectory)
            for subDir in subDirs:
                if not os.path.isdir(os.path.join(self.workDirectory, subDir)):
                    continue
                if not subDir.startswith("sub_"):
                    continue
                xmlResultFile = os.path.join(self.workDirectory, subDir, subDir + ".xml")
                if not os.path.exists(xmlResultFile):
                    continue
                try:
                    robotResults = ExecutionResult(xmlResultFile)
                except robot.errors.DataError as rd:
                    # 文件不完整，修正XML后重新运行
                    self.logger.error("Result file [" + str(xmlResultFile) + "] is incomplete xml file, fix it.")
                    with open(xmlResultFile, encoding="UTF-8", mode="r") as infile:
                        fixed = str(RobotXMLSoupParser(infile, features='xml'))
                    with open(xmlResultFile, encoding="UTF-8", mode='w') as outfile:
                        outfile.write(fixed)
                    try:
                        robotResults = ExecutionResult(xmlResultFile)
                    except robot.errors.DataError:
                        # 文件存在问题，还是无法解析
                        self.logger.error("Result file [" + str(xmlResultFile) + "] is not valid xml file, ignore it.")
                        continue

                robotSuiteResultList = []
                if len(robotResults.suite.suites) == 0:
                    robotSuiteResultList.append(robotResults.suite)
                else:
                    for resultTestSuite in robotResults.suite.suites:
                        robotSuiteResultList.append(resultTestSuite)
                jUnitTestCases = []
                for robotSuiteResult in robotSuiteResultList:
                    testSuiteName = robotSuiteResult.name
                    for robotCaseResult in robotSuiteResult.tests:
                        caseStatus = ""
                        if robotCaseResult.status == "PASS":
                            caseStatus = "passed"
                        if robotCaseResult.status == "FAIL":
                            caseStatus = "failed"
                        if robotCaseResult.status == "ERROR":
                            caseStatus = "error"
                        if robotCaseResult.starttime is not None:
                            startTime = datetime.datetime.strptime(
                                robotCaseResult.starttime[:17],
                                "%Y%m%d %H:%M:%S"
                            )
                        else:
                            startTime = None
                        if robotCaseResult.endtime is not None:
                            endTime = datetime.datetime.strptime(
                                robotCaseResult.endtime[:17],
                                "%Y%m%d %H:%M:%S")
                        else:
                            endTime = 0
                        if startTime is not None and endTime is not None:
                            caseElapsed = (endTime - startTime).seconds
                        else:
                            caseElapsed = 0
                        jUnitTestCase = JunitTestCase(
                            name=robotCaseResult.name,
                            classname=robotCaseResult.name,
                            elapsed_sec=caseElapsed
                        )
                        if caseStatus in ["failed", "error"]:
                            if robotCaseResult.message is None or len(str(robotCaseResult.message).strip()) == 0:
                                failureMessage = "Test failed."
                            else:
                                failureMessage = robotCaseResult.message
                            jUnitTestCase.add_failure_info(message=failureMessage)
                        jUnitTestCases.append(jUnitTestCase)
                    jUnitTestSuite = JunitTestSuite(testSuiteName, jUnitTestCases)
                    jUnitTestSuites.append(jUnitTestSuite)
            with open(file=JunitReportFile, mode="w", encoding="UTF-8") as fp:
                fp.write(JunitTestSuite.to_xml_string(jUnitTestSuites))
        elif self.reportLevel == "SCENARIO":
            # 遍历目录来获取Junit测试结果
            jUnitTestSuites = []
            subDirs = os.listdir(self.workDirectory)
            for subDir in subDirs:
                if not os.path.isdir(os.path.join(self.workDirectory, subDir)):
                    continue
                if not subDir.startswith("sub_"):
                    continue

                # 开始处理subDir下的内容
                # 需要处理的文件有 xdb文件， 即Execute TestCli形成的结果
                # 需要处理的文件有 xlog文件，即Compare形成的结果
                # 如果xlog文件中有和xdb不一样的结果，以xlog文件中的信息为最终结果，忽略之前xdb的结果
                for root, dirs, files in os.walk(os.path.join(self.workDirectory, subDir)):
                    for f in files:
                        if f.endswith(".xlog"):
                            # 读取xlog扩展文件
                            with open(file=os.path.join(root, f), mode="r", encoding="utf-8") as fp:
                                xlogContent = json.load(fp)
                            jUnitTestCases = []

                            # xlog信息中不一定包含时间信息
                            # - passed: 表示测试用例通过, 状态为passed。
                            # - failed: 表示测试用例失败, 状态为failed。
                            # - skipped: 表示测试用例被跳过, 状态为skipped。可能是测试用例当前不可执行。
                            # - error: 表示测试用例执行时报错, 状态为error。
                            for scenarioName, scenarioResult in dict(xlogContent["ScenarioResults"]).items():
                                caseStatus = ""
                                if scenarioResult["Status"] in ["FAILURE"]:
                                    caseStatus = "failed"
                                if scenarioResult["Status"] in ["Successful"]:
                                    caseStatus = "passed"
                                caseElapsed = 0
                                if "Elapsed" in dict(scenarioResult).keys():
                                    caseElapsed = scenarioResult["Elapsed"]
                                jUnitTestCase = JunitTestCase(
                                    name=scenarioName,
                                    classname=f.replace(".xlog", ""),
                                    elapsed_sec=caseElapsed
                                )
                                if caseStatus == "failed":
                                    jUnitTestCase.add_failure_info(
                                        message=scenarioResult["message"]
                                    )
                                jUnitTestCases.append(jUnitTestCase)
                            # 每一个xlog作为一个TestSuite，每一个Scenario作为一个TestCase
                            testSuiteName = ("_".join(subDir.split('_')[1:-1]) +
                                             "_" + f.replace(".xlog", ""))
                            jUnitTestSuite = JunitTestSuite(testSuiteName, jUnitTestCases)
                            jUnitTestSuites.append(jUnitTestSuite)
            with open(file=JunitReportFile, mode="w", encoding="UTF-8") as fp:
                fp.write(JunitTestSuite.to_xml_string(jUnitTestSuites))

    # 整理并生成最后的测试报告
    def generateTestReport(self):
        # 建立测试报告的目录
        reportFileDir = os.path.join(self.workDirectory, "report")
        if not os.path.exists(reportFileDir):
            os.makedirs(reportFileDir, exist_ok=True)

        # 如果有需要，生成JUNIT格式的测试报告
        if "JUNIT" in self.reportTypes:
            self.generateJunitReport()

        # 如果有需要，生成HTML格式的测试报告
        if "HTML" in self.reportTypes:
            try:
                # 整理报告内容
                htmlTestResult = TestResult()
                htmlTestResult.setTitle("Test Report")
                htmlTestResult.robotOptions = self.robotOptions

                self.logger.info("Processing test result under [" + str(self.workDirectory) + "] ...")

                # 备份之前的输入输出和环境信息
                saved__Stdout = sys.__stdout__
                saved__Stderr = sys.__stderr__
                savedStdout = sys.stdout
                savedStderr = sys.stderr

                # 切换标准输入输出到指定的文件中
                stdoutFile = open(os.path.join(self.workDirectory, "report", "TestReport.stdout"), 'a+')
                stderrFile = open(os.path.join(self.workDirectory, "report", "TestReport.stderr"), 'a+')
                sys.stdout = stdoutFile
                sys.stderr = stderrFile
                sys.__stdout__ = stdoutFile
                sys.__stderr__ = stderrFile

                # 分线程来统计报告
                threads = []
                for task in self.taskList:
                    t = threading.Thread(
                        target=self.generateRobotReport,
                        args=(task, htmlTestResult)
                    )
                    t.start()
                    threads.append(t)
                for t in threads:
                    t.join()

                # 汇总所有的子目录到一个统一的报表上，便于展现
                self.logger.info("Combing all test reports to one summary report ...")
                rebotArgs = []
                rebotArgs.extend(["--tagstatexclude", "owner*"])
                rebotArgs.extend(["--tagstatexclude", "feature*"])
                rebotArgs.extend(["--tagstatexclude", "priority*"])
                rebotArgs.extend(["--suitestatlevel", "2"])
                rebotArgs.extend(["--outputdir", self.workDirectory])
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
                # 遍历目录，将所有的Robot的XML文件合并到程序的参数中
                testSubXmlList = []
                for root, dirs, files in os.walk(self.workDirectory):
                    for f in files:
                        if f.endswith(".xml") and f.startswith("sub_"):
                            testSubXmlList.append(
                                os.path.abspath(os.path.join(root, str(f))))
                if len(testSubXmlList) == 0:
                    self.logger.error(
                        "No valid test in [" + self.workDirectory + "].")
                else:
                    rebotArgs.extend(testSubXmlList)
                    # 调用Rebot_Cli来合并报表
                    print("Execute Rebot_Cli: ")
                    for arg in rebotArgs:
                        print("    " + str(arg))
                    rebot_cli(rebotArgs, exit=False)

                # 还原重定向的日志
                sys.__stdout__ = saved__Stdout
                sys.stdout = savedStdout
                sys.__stderr__ = saved__Stderr
                sys.stderr = savedStderr
                stdoutFile.close()
                stderrFile.close()

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
                        "job": testSuite.getSuiteSource(),
                        "metadata": testSuite.getSuiteMeta(),
                        "suiteName": testSuite.getSuiteName(),
                        "passedCount": testSuite.getPassedCaseCount(),
                        "errorCount": testSuite.getErrorCaseCount(),
                        "failedCount": testSuite.getFailedCaseCount(),
                        "elapsed": testSuite.getSuiteElapsedTime(),
                        "cases": testCaseReports
                    }
                    testReport.append(testSuiteReport)
                self.executorMonitor["testReport"] = testReport

                # 更新描述信息
                htmlTestResult.setDescription(
                    "Max Processes   : " + str(self.maxProcess) + '<br>'
                )

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
                for subdir in os.listdir(self.workDirectory):
                    if os.path.isdir(os.path.join(self.workDirectory, subdir)) and subdir.startswith("sub_"):
                        for backupFile in os.listdir(os.path.join(self.workDirectory, subdir)):
                            if backupFile.split(".")[-1] in ["html"]:
                                sourceReportFile = os.path.join(
                                    self.workDirectory, subdir, backupFile)
                                targetReportFile = os.path.join(
                                    self.workDirectory, reportFileDir, backupFile)
                                if os.path.exists(sourceReportFile):
                                    shutil.copyfile(sourceReportFile, targetReportFile)
                        shutil.make_archive(
                            base_name=os.path.join(
                                self.workDirectory, reportFileDir, subdir),
                            format="tar",
                            root_dir=os.path.join(self.workDirectory),
                            base_dir=subdir
                        )
            except Exception as e:
                raise RegressException(message="Regress failed.", inner_exception=e)

        self.logger.info("Processing test summary ...")

        # 记录所有被过滤掉的Tag标记
        filteredTags = []
        if self.robotOptions is not None:
            robotOptionList = str(self.robotOptions).split()
            for pos in range(0, len(robotOptionList)):
                if robotOptionList[pos] == "--exclude" and pos < (len(robotOptionList) - 1):
                    filteredTags.append(robotOptionList[pos+1])

        # 记录所有需要运行的testcase
        caseList = []
        for job in self.jobList:
            try:
                robotSuite = TestSuiteBuilder().build(job)
                cases = []
                for testCase in robotSuite.tests:
                    isFilteredCase = False
                    for resultTestCaseTag in testCase.tags:
                        if resultTestCaseTag in filteredTags:
                            isFilteredCase = True
                            break
                    cases.append(
                        {
                            "caseName": testCase.name,
                            "caseTags": [str(s) for s in testCase.tags],
                            "isSkiped": isFilteredCase
                        }
                    )
                caseList.append(
                    {
                        "job": str(os.path.relpath(job, self.testRoot)),
                        "suiteName": robotSuite.name,
                        "cases": cases
                    }
                )
            except robot.errors.DataError as re:
                caseList.append(
                    {
                        "job": str(os.path.relpath(job, self.testRoot)),
                        "suiteName": "Unknown",
                        "errorMsg": re.message,
                        "cases": []
                    }
                )

        # 记录测试结果
        if "testReport" in self.executorMonitor.keys():
            testReport = self.executorMonitor["testReport"]
        else:
            testReport = []

        # 汇总测试数据，生成summary文件
        taskSummary = {}
        taskSummary.update(
            {
                "platform": platform.platform(),
                "processor": platform.processor(),
                "hostName": platform.node(),
                "python": platform.python_version(),
                "pid": os.getpid(),
                "testRunId": self.testRunId,
                "maxProcess": self.maxProcess,
                "scriptTimeout": self.scriptTimeout,
                "workerTimeout": self.workerTimeout,
                "startTime": self.executorMonitor["started"],
                "endTime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "filteredTags": filteredTags,
                "jobList": self.jobList,
                "caseList": caseList,
                "testReport": testReport
            }
        )
        # 将结果写入文件记录
        with open(file=os.path.join(reportFileDir, "taskSummary.json"), mode="w", encoding="utf-8") as fp:
            json.dump(taskSummary, fp=fp, indent=4, ensure_ascii=False)

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
            self.maxProcess = DEFAULT_MAX_PROCESS
            self.executorMonitor.update({"maxProcess": self.maxProcess})
        self.logger.info("Test parallelism :[" + str(self.maxProcess) + "].")

        # 系统Robot运行选项
        self.logger.info("robotOptions :[" + str(self.robotOptions) + "].")

        # 构造字典，用来标记每个子进程的名称，方便监控作业
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
        # 在这个过程中，要过滤掉所有StandAlone为N的文件，即不能独立运行，或者不包含任何有效测试用例的文件
        # 要补充runLevel进入任务清单，如果文件没有提供runLevel，则默认runLevel为100
        runLevels = [100, ]

        def appendJobFile(jobfile: str):
            self.logger.info("Checking file: [" + str(jobfile) + "] ...")
            if str(jobfile).endswith(".robot"):
                try:
                    isStandAlone = True
                    robotSuite = TestSuiteBuilder().build(os.path.abspath(jobfile))
                    for metaKey, metaValue in robotSuite.metadata.items():
                        if str(metaKey).strip().upper() == "StandAlone".upper():
                            if str(metaValue).upper() in ["N", "NO", "NOT"]:
                                isStandAlone = False
                                break
                    if isStandAlone:
                        robotRunLevel = 100
                        for metaKey, metaValue in robotSuite.metadata.items():
                            if str(metaKey).strip().upper() == "runLevel".upper():
                                robotRunLevel = int(str(metaValue))
                                if robotRunLevel not in runLevels:
                                    runLevels.append(robotRunLevel)
                                break
                        self.logger.info("  Robot file : [" + str(jobfile) + "] has added to task list. ")
                        testName = os.path.basename(jobfile)[:-len(".robot")]
                        workingFolderName = "sub_" + testName + "_" + str(random.randint(100000, 999999))
                        self.taskList.append(
                            {
                                "robotFile": str(os.path.abspath(jobfile)).replace("\\", "/"),
                                "runLevel": robotRunLevel,
                                "suiteName": robotSuite.name,
                                "workingDirectory": workingFolderName
                            }
                        )
                    else:
                        self.logger.warning("  Robot file : [" + str(jobfile) + "] is not standalone suite. " +
                                            "Will ignore this ...")
                except robot.errors.DataError:
                    self.logger.warning("  Parse robot file : [" + str(jobfile) + "] error. Will ignore this ...")
            else:
                self.logger.warning("  Ignore job file [" + str(jobfile) + "] . Unknown file format.")
            # end of appendJobFile

        if self.jobList is not None:
            self.logger.info("Task list: ")
            for job in self.jobList:
                self.logger.info(">>  " + job)
            # Job_List分隔符可以是换行符，也可以是逗号
            for job in self.jobList:
                job = job.strip()
                if len(job) == 0:
                    continue
                if os.path.isfile(str(job)):
                    appendJobFile(jobfile=str(job))
                elif os.path.isdir(str(job)):
                    self.logger.info("Checking directory: [" + str(job) + "] ...")
                    for root, dirs, files in os.walk(str(job)):
                        for f in files:
                            if f.endswith(".robot"):
                                job = os.path.join(root, str(f))
                                appendJobFile(jobfile=job)
                else:
                    self.logger.warning("Current pwd directory : [" + str(os.getcwd()) + "]")
                    self.logger.warning("[" + job + "] is not valid file or directory. Ignore it.")

        # 处理没有完成的JOB
        def AnalyzeBrokenTest(testRobotFile: str, workingDirectory: str):
            # 处理掉损坏的XML文件，由于Robot运行(超时退出)不完整导致的
            inputxmlfile = os.path.join(workingDirectory, os.path.basename(workingDirectory) + ".xml")
            if not os.path.exists(inputxmlfile):
                self.logger.error("Robot [" + str(testRobotFile) + "] has failed with fatal error. " +
                                  "No result files found. " + str(inputxmlfile))
            else:
                self.logger.info("Result file [" + str(inputxmlfile) + "] is incompleted. Will try to fix it ...")
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
                            self.executorMonitor.update({"taskLeft": self.executorMonitor["taskLeft"] - 1})
                            self.executorList.remove(timeoutExecutor)
                        else:
                            # 强行终止进程
                            self.logger.error("Executor(" + str(timeoutExecutor["Process"].pid).rjust(8, ' ') +
                                              ") has run over script limit [" + str(
                                                  self.scriptTimeout) + "] seconds, "
                                              + "terminate the [" + str(timeoutExecutor["robotFile"]) + "]")
                            timeoutExecutor["Process"].terminate()
                            AnalyzeBrokenTest(
                                testRobotFile=timeoutExecutor["args"]["robotFile"],
                                workingDirectory=timeoutExecutor["args"]["workingDirectory"])
            if self.workerTimeout != -1:
                for timeoutExecutor in self.executorList:
                    if (currentDateTime - timeoutExecutor["startTime"]) > self.workerTimeout:
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
                                              + "terminate the [" + str(timeoutExecutor["robotFile"]) + "]")
                            timeoutExecutor["Process"].terminate()
                            AnalyzeBrokenTest(
                                testRobotFile=timeoutExecutor["args"]["robotFile"],
                                workingDirectory=timeoutExecutor["args"]["workingDirectory"])
            """ check_timeout """

        # 循环处理任务
        self.executorMonitor.update({"taskCount": len(self.taskList)})
        self.executorMonitor.update({"taskLeft": len(self.taskList)})
        self.executorMonitor.update({"runLevelCount": len(runLevels)})
        self.executorMonitor.update({"runLevelLeft": len(runLevels)})

        self.logger.info("Totally [" + str(self.executorMonitor["taskCount"]) + "] in task TODO list ...")

        self.logger.info("Start runner at [" + str(self.workDirectory) + "]...")

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
                            self.logger.info("End the test [" +
                                             runningJobs[executor["executorName"]]["workingDirectory"] + ":" +
                                             str(runningJobs[executor["executorName"]]["script"] + "]"))
                            del runningJobs[executor["executorName"]]
                            self.executorMonitor["runningJobs"] = copy.copy(runningJobs)
                            self.executorMonitor.update({"taskLeft": self.executorMonitor["taskLeft"] - 1})
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

                # 运行具体的Robot文件
                processManagerContext = multiprocessing.get_context("spawn")
                self.logger.info(
                    "Begin to execute robot test [" + str(taskPos) + "/" + str(len(self.taskList)) + "] "
                    + self.taskList[nPos]["robotFile"] + " ...")
                args = {
                    "robotFile": str(self.taskList[nPos]["robotFile"]),
                    "robotOptions": self.robotOptions,
                    "testRoot": self.testRoot,
                    "testRunId": self.testRunId,
                    "workingDirectory": os.path.join(self.workDirectory, self.taskList[nPos]["workingDirectory"]),
                }
                taskPos = taskPos + 1
                process = processManagerContext.Process(
                    target=runRobotExecutor,
                    name="TestCliRobot: " + str(args["workingDirectory"]),
                    args=(args,)
                )
                process.start()
                self.executorList.append(
                    {
                        "Process": process,
                        "robotFile":  str(self.taskList[nPos]["robotFile"]),
                        "startTime": time.time(),
                        "workingDirectory": args["workingDirectory"],
                        "executorName": executorName,
                        "args": args
                    })
                runningJobs = self.executorMonitor["runningJobs"]
                runningJobs.update(
                    {
                        executorName:
                            {
                                "script": str(self.taskList[nPos]["robotFile"]),
                                "workingDirectory": args["workingDirectory"],
                                "pid": process.pid,
                                "started": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                            }
                    }
                )
                self.executorMonitor["runningJobs"] = copy.copy(runningJobs)
            self.executorMonitor.update({"runLevelLeft": self.executorMonitor["runLevelLeft"] - 1})

            while True:
                # 移除已经结束的进程列表
                for executor in self.executorList:
                    if not executor["Process"].is_alive():
                        # 进程已经结束，记录进程运行结果
                        runningJobs = self.executorMonitor["runningJobs"]
                        self.logger.info("End the test [" +
                                         runningJobs[executor["executorName"]]["workingDirectory"] + ":" +
                                         str(runningJobs[executor["executorName"]]["script"] + "]"))
                        del runningJobs[executor["executorName"]]
                        self.executorMonitor["runningJobs"] = copy.copy(runningJobs)
                        self.executorMonitor.update({"taskLeft": self.executorMonitor["taskLeft"] - 1})
                        self.executorList.remove(executor)
                if len(self.executorList) == 0:
                    break
                else:
                    # 休息3秒钟
                    time.sleep(3)
                    # 检查是否有超时的进程，如果有，则处理
                    check_timeout()

            self.logger.info("All tasks in run level [" + str(runLevel) + "] have completed.")
