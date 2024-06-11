# -*- coding: utf-8 -*-
import copy
import multiprocessing
import os
import logging
import platform
import random
import shutil
import sys
import re
import time
import datetime
import json
import threading
import configparser

import mysql.connector
import psutil
import robot.errors
from robot.api import TestSuiteBuilder
from robot import rebot_cli

from .runrobotexecutor import runRobotExecutor
from .runrobotexecutor import generateRobotExecutorReport
from .htmltestreport.HtmlTestReport import HTMLTestRunner
from .htmltestreport.HtmlTestReport import TestResult
from .htmltestreport.HtmlTestReport import TestSuite
from .htmltestreport.HtmlTestReport import TestCase
from .htmltestreport.HtmlTestReport import TestScenario
from .htmltestreport.HtmlTestReport import TestCaseStatus
from .htmltestreport.HtmlTestReport import TestScenarioStatus
from .runrobotexecutor import RobotXMLSoupParser
from .junitreport.JunitTestReport import TestSuite as JunitTestSuite
from .junitreport.JunitTestReport import TestCase as JunitTestCase
from .mysqlutil import MYSQLUtil
from .regressexception import RegressException


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
            testRunId=0,
            testResultDb=None
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
        self.testResultDb = testResultDb
        self.appOptions = None

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

        # 应用程序的配置选项
        if "TESTCLI_HOME" in os.environ:
            # 其次尝试读取TESTCLI_HOME/conf/testcli.ini中的信息，如果有，以TESTCLI_HOME/conf/testcli.ini信息为准
            confFilename = os.path.join(str(os.environ["TESTCLI_HOME"]).strip(), "conf", "testcli.ini")
            if os.path.exists(confFilename):
                self.appOptions = configparser.ConfigParser()
                self.appOptions.read(confFilename)
        if self.appOptions is None:
            # 之前的读取都没有找到，以系统默认目录为准
            confFilename = os.path.join(os.path.dirname(__file__), "..", "..", "conf", "testcli.ini")
            if os.path.exists(confFilename):
                self.appOptions = configparser.ConfigParser()
                self.appOptions.read(confFilename)
            else:
                raise RegressException("Config file [" + confFilename + "] missed. " +
                                       "Please mare sure you have a successful install.")

    # 整理并生成最后的测试报告
    def generateTestReport(self):
        # 建立测试报告的目录
        try:
            reportFileDir = os.path.join(self.workDirectory, "report")
            if not os.path.exists(reportFileDir):
                os.makedirs(reportFileDir, exist_ok=True)

            # 整理报告内容
            htmlTestResult = TestResult()
            htmlTestResult.setTitle("Test Report")
            htmlTestResult.setMaxProcess(self.maxProcess)
            htmlTestResult.robotOptions = self.robotOptions

            # 为Junit单独准备一个目录，来放置Junit结果
            jUnitReportDir = os.path.join(self.workDirectory, "report", "junitreport")
            if not os.path.exists(jUnitReportDir):
                os.makedirs(jUnitReportDir)
            JunitReportFile = os.path.join(jUnitReportDir, "junit.xml")

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

            # Junit测试结果
            jUnitTestSuites = []

            # 按照目录来统计报告
            # 如果存在目录下的汇总(jobSummary.json)，则直接利用
            for robotTask in self.taskList:
                self.logger.info(
                    "  Processing robot result file under [" + str(robotTask["workingDirectory"]) + "] ...")

                htmlTestSuite = TestSuite()
                # 记录源文件名，相对路径
                htmlTestSuite.setSuiteSource(str(os.path.relpath(robotTask["robotFile"], self.testRoot)))

                # 如果指定目录下不存在jobSummary文件，则说明测试被异常终止，需要重新生成汇总文件
                jobSummaryFile = os.path.join(self.workDirectory, str(robotTask["workingDirectory"]),
                                              "jobSummary.json")
                if not os.path.exists(jobSummaryFile):
                    generateRobotExecutorReport(
                        logger=self.logger,
                        testRoot=self.testRoot,
                        workingDirectory=self.workDirectory,
                        subDirectory=str(robotTask["workingDirectory"]),
                        robotFile=str(robotTask["robotFile"]),
                        robotOptions=self.robotOptions,
                        startTime=None,
                        endTime=None
                    )
                if not os.path.exists(jobSummaryFile):
                    raise RegressException(
                        "Failed to generate robot executor report at [" + robotTask["workingDirectory"] + "].")

                # 加载任务的汇总数据到json结构中
                with open(file=jobSummaryFile, mode="r", encoding="utf-8") as fp:
                    jobSummary = json.load(fp=fp)
                htmlTestSuite.setSuiteName(jobSummary["suiteName"])
                htmlTestSuite.setSuiteMeta(jobSummary["metadata"])

                # 首先加载全部数据，全部按照ERROR处理，随后根据结果信息二次更新
                testOwnerMap = {}
                for testCase in jobSummary["caseList"]:
                    htmlTestCase = TestCase()
                    isFilteredCase = testCase["isSkiped"]
                    if isFilteredCase:
                        continue
                    htmlTestCase.setCaseName(testCase["caseName"])
                    htmlTestCase.setCaseStatus(TestCaseStatus.ERROR)
                    testOwner = None
                    for resultTestCaseTag in testCase["caseTags"]:
                        if str(resultTestCaseTag).lower().startswith('owner:'):
                            if testOwner is None:
                                testOwner = resultTestCaseTag[6:].strip()
                                testOwnerMap.update(
                                    {
                                        testCase["caseName"]: testOwner
                                    }
                                )
                    htmlTestCase.setCaseOwner(testOwner)
                    htmlTestCase.setCaseStartTime("____-__-__ __:__:__")
                    htmlTestCase.setCaseElapsedTime(0)
                    htmlTestCase.setErrorStackTrace("Not started.")
                    htmlTestCase.setDownloadURLLink("javascript:void(0)")
                    htmlTestCase.setDetailReportLink("javascript:void(0)")
                    htmlTestSuite.addTestCase(htmlTestCase)

                # 用正确的结果来更新测试报告
                for testCaseResult in jobSummary["caseResultList"]:
                    htmlTestCase = TestCase()
                    htmlTestCase.setCaseName(testCaseResult["caseName"])

                    # 更新HTML测试结果
                    if testCaseResult["caseName"] in testOwnerMap.keys():
                        testOwner = testOwnerMap[testCaseResult["caseName"]]
                    else:
                        testOwner = "UNKNOWN"
                    htmlTestCase.setCaseOwner(testOwner)
                    if testCaseResult["caseStatus"] == "FAIL":
                        htmlTestCase.setCaseStatus(TestCaseStatus.FAILURE)
                    elif testCaseResult["caseStatus"] == "PASS":
                        htmlTestCase.setCaseStatus(TestCaseStatus.SUCCESS)
                    else:
                        htmlTestCase.setCaseStatus(TestCaseStatus.ERROR)
                    try:
                        caseStartTime = (
                            datetime.datetime.strptime(testCaseResult["startTime"], "%Y-%m-%d %H:%M:%S"))
                    except ValueError:
                        caseStartTime = None
                    try:
                        caseEndTime = datetime.datetime.strptime(testCaseResult["endTime"], "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        caseEndTime = None
                    htmlTestCase.setCaseStartTime(testCaseResult["startTime"])
                    if caseStartTime is None or caseEndTime is None:
                        caseElapsed = 0
                    else:
                        caseElapsed = (caseEndTime - caseStartTime).seconds
                    htmlTestCase.setCaseElapsedTime(caseElapsed)
                    htmlTestCase.setDetailReportLink(
                        robotTask["workingDirectory"] + ".html#" + testCaseResult["id"])
                    htmlTestCase.setDownloadURLLink(robotTask["workingDirectory"] + ".tar")

                    # 更新测试场景数据
                    for scenarioResult in jobSummary["scenarioResultList"]:
                        if scenarioResult["caseName"] == testCaseResult["caseName"]:
                            testScenario = TestScenario()
                            testScenario.setScenarioName(scenarioResult["scenarioName"])
                            if scenarioResult["scenarioStatus"] == "PASS":
                                testScenario.setScenarioStatus(TestScenarioStatus.SUCCESS)
                            elif scenarioResult["scenarioStatus"] == "FAIL":
                                testScenario.setScenarioStatus(TestScenarioStatus.FAILURE)
                            else:
                                testScenario.setScenarioStatus(TestScenarioStatus.ERROR)
                            testScenario.setScenarioDescription("")
                            htmlTestCase.addScenario(copy.deepcopy(testScenario))
                    htmlTestSuite.addTestCase(htmlTestCase)

                # 更新Html运行结果
                htmlTestSuite.SummaryTestCase()
                htmlTestResult.addSuite(htmlTestSuite)

                # 合并Junit的测试报告
                self.logger.info("Combing all test reports to junit report ...")
                for testCase in jobSummary["caseList"]:
                    junitSuiteName = testCase["caseName"]
                    jUnitTestCases = []
                    for scenarioResult in jobSummary["scenarioResultList"]:
                        if scenarioResult["caseName"] != junitSuiteName:
                            continue
                        if scenarioResult["scenarioStatus"] in ["PASS"]:
                            scenarioStatus = "passed"
                        else:
                            scenarioStatus = "failed"
                        jUnitTestCase = JunitTestCase(
                            name=scenarioResult["scenarioName"] + "-" + scenarioResult["scenarioId"],
                            status=scenarioStatus,
                            classname=scenarioResult["scenarioName"] + "-" + scenarioResult["scenarioId"],
                            elapsed_sec=scenarioResult["elapsed"]
                        )
                        jUnitTestCases.append(jUnitTestCase)
                    # 更新Junit测试结果
                    jUnitTestSuite = JunitTestSuite(jobSummary["suiteName"], jUnitTestCases)
                    jUnitTestSuites.append(jUnitTestSuite)

            # 写入Junit的测试结果文件
            with open(file=JunitReportFile, mode="w", encoding="UTF-8") as fp:
                fp.write(JunitTestSuite.toXmlString(jUnitTestSuites, prettyFormat=True))

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
                formattedArgs = []
                for arg in rebotArgs:
                    if arg.startswith("--"):
                        formattedArgs.append(arg)
                    else:
                        formattedArgs[-1] = formattedArgs[-1] + " " + arg
                for arg in formattedArgs:
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

        # 生成测试汇总报告
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
        testReport = []
        for task in self.taskList:
            try:
                robotSuite = TestSuiteBuilder().build(task["robotFile"])
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
                            "caseTags": [str(s) for s in testCase.tags if s.strip() != "|"],
                            "isSkiped": isFilteredCase
                        }
                    )
                caseList.append(
                    {
                        "job": str(os.path.relpath(task["robotFile"], self.testRoot)),
                        "suiteName": robotSuite.name,
                        "cases": cases
                    }
                )
                if os.path.exists(os.path.join(self.workDirectory, task["workingDirectory"], "jobSummary.json")):
                    with open(
                            file=os.path.join(self.workDirectory, task["workingDirectory"], "jobSummary.json"),
                            mode="r", encoding="utf-8") as fp:
                        jobSummary = json.load(fp=fp)
                    testReport.append(
                        {
                            "job": str(os.path.relpath(task["robotFile"], self.testRoot)),
                            "suiteName": robotSuite.name,
                            "workingDirectory": task["workingDirectory"],
                            "cases": jobSummary["caseResultList"],
                            "scenarios": jobSummary["scenarioResultList"]
                        }
                    )
            except robot.errors.DataError as ex:
                caseList.append(
                    {
                        "job": str(os.path.relpath(task["robotFile"], self.testRoot)),
                        "suiteName": "Unknown",
                        "errorMsg": ex.message,
                        "cases": []
                    }
                )

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
                "robotOptions": self.robotOptions,
                "filteredTags": filteredTags,
                "jobList": self.jobList,
                "caseList": caseList,
                "testReport": testReport
            }
        )
        # 将任务汇总结果写入文件记录
        with open(file=os.path.join(reportFileDir, "taskSummary.json"), mode="w", encoding="utf-8") as fp:
            json.dump(taskSummary, fp=fp, indent=4, ensure_ascii=False)

        # 如果需要将测试结果插入数据库，则插入数据库
        saveTestResultToDb = False
        resultDbHost = None
        resultDbPort = None
        resultDbUser = None
        resultDbPasswd = None
        resultDbService = None
        if self.testResultDb is None:
            try:
                resultDbHost = self.appOptions.get("resultdb", "host")
                resultDbPort = self.appOptions.get("resultdb", "port")
                resultDbUser = self.appOptions.get("resultdb", "user")
                resultDbPasswd = self.appOptions.get("resultdb", "passwd")
                resultDbService = self.appOptions.get("resultdb", "service")
                saveTestResultToDb = True
            except (configparser.NoSectionError, configparser.NoSectionError):
                pass
        else:
            # user/pass@ip:port/service
            matchObj = re.match(pattern=r"^(.*?)/(.*?)@(.*?):(\d+)/(.*?)$", string=self.testResultDb)
            if matchObj is not None:
                resultDbUser = str(matchObj.group(1))
                resultDbPasswd = str(matchObj.group(2))
                resultDbHost = str(matchObj.group(3))
                resultDbPort = int(matchObj.group(4))
                resultDbService = str(matchObj.group(5))
                saveTestResultToDb = True
            else:
                self.logger.warning("Invalid resultdb parameter. skip presist test result.")
        if saveTestResultToDb:
            self.logger.info("Log test result into rdb ...")
            sql = ""
            try:
                testResultDbHandler = MYSQLUtil()
                testResultDbHandler.connect(
                    host=resultDbHost,
                    port=resultDbPort,
                    user=resultDbUser,
                    passwd=resultDbPasswd,
                    database=resultDbService
                )
                # TESTCLI_RESULTDB_JOBS
                sql = """
                    CREATE TABLE IF NOT EXISTS TESTCLI_RESULTDB_JOBS
                    (
                        testRunId          VARCHAR(200),
                        platform           VARCHAR(200),
                        hostName           VARCHAR(200),
                        pid                Int,
                        maxProcess         Int,
                        scriptTimeout      Int,
                        workerTimeout      Int,
                        startTime          DateTime,
                        endTime            DateTime,
                        robotOptions       VARCHAR(500),
                        filteredTags       VARCHAR(500),
                        jobList            VARCHAR(5000)
                    )
                """
                testResultDbHandler.execute(sql=sql)
                dbValues = {
                    "testRunId": taskSummary["testRunId"],
                    "platform": taskSummary["platform"],
                    "hostName": taskSummary["hostName"],
                    "pid": taskSummary["pid"],
                    "maxProcess": taskSummary["maxProcess"],
                    "scriptTimeout": taskSummary["scriptTimeout"],
                    "workerTimeout": taskSummary["workerTimeout"],
                    "startTime": datetime.datetime.strptime(taskSummary["startTime"], "%Y-%m-%d %H:%M:%S"),
                    "endTime": datetime.datetime.strptime(taskSummary["endTime"], "%Y-%m-%d %H:%M:%S"),
                    "robotOptions": str(taskSummary["robotOptions"]),
                    "filteredTags": str(taskSummary["filteredTags"]),
                    "jobList": str(taskSummary["jobList"])
                }
                sql = ("INSERT INTO TESTCLI_RESULTDB_JOBS({keys}) VALUES ({values})"
                       .format(keys=",".join(dbValues.keys()), values=",".join(['%s'] * len(dbValues))))
                testResultDbHandler.execute(sql, data=tuple(dbValues.values()))
                # TESTCLI_RESULTDB_CASES
                sql = """
                    CREATE TABLE IF NOT EXISTS TESTCLI_RESULTDB_CASES
                    (
                        testRunId          VARCHAR(200),
                        job                VARCHAR(200),
                        suiteName          VARCHAR(200),
                        caseName           VARCHAR(200),
                        caseTags           VARCHAR(200),
                        isSkiped           tinyint
                    )
                """
                testResultDbHandler.execute(sql=sql)
                dbValues = []
                for caseLists in taskSummary["caseList"]:
                    for cases in caseLists["cases"]:
                        dbValues.append(
                            {
                                "testRunId": taskSummary["testRunId"],
                                "job": caseLists["job"],
                                "suiteName": caseLists["suiteName"],
                                "caseName": cases["caseName"],
                                "caseTags": str(cases["caseTags"]),
                                "isSkiped": cases["isSkiped"]
                            }
                        )
                if len(dbValues) != 0:
                    sql = ("INSERT INTO TESTCLI_RESULTDB_CASES({keys}) VALUES ({values})"
                           .format(keys=",".join(dbValues[0].keys()), values=",".join(['%s'] * len(dbValues[0]))))
                    testResultDbHandler.executemany(sql, data=[s.values() for s in dbValues])
                # TESTCLI_RESULTDB_REPORT_CASES
                sql = """
                    CREATE TABLE IF NOT EXISTS TESTCLI_RESULTDB_REPORT_CASES
                    (
                        testRunId          VARCHAR(200),
                        job                VARCHAR(200),
                        suiteName          VARCHAR(200),
                        workingDirectory   VARCHAR(200),
                        caseId             VARCHAR(200),
                        caseName           VARCHAR(200),                        
                        caseTags           VARCHAR(200),
                        caseStatus         VARCHAR(200),
                        caseMessage        VARCHAR(5000),
                        startTime          DateTime,
                        endTime            DateTime
                    )
                """
                testResultDbHandler.execute(sql=sql)
                dbValues = []
                for testReport in taskSummary["testReport"]:
                    for case in testReport["cases"]:
                        dbValues.append(
                            {
                                "testRunId": taskSummary["testRunId"],
                                "job": testReport["job"],
                                "suiteName": testReport["suiteName"],
                                "workingDirectory": testReport["workingDirectory"],
                                "caseId": case["id"],
                                "caseName": case["caseName"],
                                "caseTags": str(case["caseTags"]),
                                "caseStatus": str(case["caseStatus"]),
                                "caseMessage": str(case["message"]),
                                "startTime":
                                    datetime.datetime.strptime(case["startTime"], "%Y-%m-%d %H:%M:%S"),
                                "endTime":
                                    datetime.datetime.strptime(case["endTime"], "%Y-%m-%d %H:%M:%S")
                            }
                        )
                if len(dbValues) != 0:
                    sql = ("INSERT INTO TESTCLI_RESULTDB_REPORT_CASES({keys}) VALUES ({values})"
                           .format(keys=",".join(dbValues[0].keys()), values=",".join(['%s'] * len(dbValues[0]))))
                    testResultDbHandler.executemany(sql, data=[s.values() for s in dbValues])
                # TESTCLI_RESULTDB_REPORT_SCENARIOS
                sql = """
                    CREATE TABLE IF NOT EXISTS TESTCLI_RESULTDB_REPORT_SCENARIOS
                    (
                        testRunId          VARCHAR(200),
                        job                VARCHAR(200),
                        suiteName          VARCHAR(200),
                        workingDirectory   VARCHAR(200),
                        scenarioId         VARCHAR(200),
                        scenarioName       VARCHAR(200),
                        caseName           VARCHAR(200),                        
                        scenarioStatus     VARCHAR(200),
                        scenarioMessage    VARCHAR(5000),
                        elapsed            float
                    )
                """
                testResultDbHandler.execute(sql=sql)
                dbValues = []
                for testReport in taskSummary["testReport"]:
                    for scenario in testReport["scenarios"]:
                        dbValues.append(
                            {
                                "testRunId": taskSummary["testRunId"],
                                "job": testReport["job"],
                                "suiteName": testReport["suiteName"],
                                "workingDirectory": testReport["workingDirectory"],
                                "scenarioId": scenario["scenarioId"],
                                "scenarioName": scenario["scenarioName"],
                                "caseName": scenario["caseName"],
                                "scenarioStatus": str(scenario["scenarioStatus"]),
                                "scenarioMessage": str(scenario["scenarioMessage"]),
                                "elapsed": scenario["elapsed"],
                            }
                        )
                if len(dbValues) != 0:
                    sql = ("INSERT INTO TESTCLI_RESULTDB_REPORT_SCENARIOS({keys}) VALUES ({values})"
                           .format(keys=",".join(dbValues[0].keys()), values=",".join(['%s'] * len(dbValues[0]))))
                    testResultDbHandler.executemany(sql, data=[s.values() for s in dbValues])
                testResultDbHandler.commit()
                testResultDbHandler.disConnect()
            except mysql.connector.Error as me:
                self.logger.warning("Log test result into rdb failed. " + str(me.msg))
                self.logger.warning("Log test result into rdb. sql = [" + str(sql) + "]")

        # 生成报告
        htmlTestRunner = HTMLTestRunner(title="Test Report")
        htmlTestRunner.generateReport(
            result=htmlTestResult,
            output=os.path.join(reportFileDir, "report.html")
        )
        self.logger.info("Combined all test reports. Files saved at [" +
                         os.path.join(reportFileDir, "report.html") + "]")

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
                self.logger.info("Result file [" + str(inputxmlfile) + "] is corrupted. Will try to fix it ...")
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
                            self.logger.info(
                                "End the test [" + str(runningJobs[executor["executorName"]]["script"] + "]"))
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
