# -*- coding: utf-8 -*-
import os
import datetime
import robot.errors
from robot.running.builder import RobotParser
from robot.api import ExecutionResult
from robot import rebot_cli

from .htmltestreport.HtmlTestReport import TestSuite
from .htmltestreport.HtmlTestReport import TestCase
from .htmltestreport.HtmlTestReport import TestCaseStatus
from .runrobotexecutor import RobotXMLSoupParser


# 整理Robot运行测试报告
def generateRobotReport(cls, reportDir: str):
    cls.logger.info("处理目录【" + str(reportDir) + "】下的Robot结果文件...")

    # 总是先插入一个错误的记录, 如果随后找到正确的结果，则测试结果将被覆盖
    robotPath = None
    for robotTask in cls.taskList:
        if robotTask["workingDirectory"] == reportDir:
            robotPath = robotTask["robotfile"]
            break
    if robotPath is None:
        cls.logger.error(
            "内部错误。【" + reportDir + "】不是有效的工作任务目录。忽略...")
        return

    # 解析Robot文件，将所有Robot的测试用例标记为失败
    # 下一步即使测试程序退出，这里的结果将作为最终的失败结果参考
    htmlTestSuite = TestSuite()
    robotParser = RobotParser()
    suiteParser = robotParser.parse_suite_file(source=robotPath)
    resultTestCaseList = cls.TestCasesFinder()
    suiteParser.remove_empty_suites(True)
    suiteParser.filter(excluded_tags=["sqlId:None", "FILTERED"])
    suiteParser.visit(resultTestCaseList)
    htmlTestSuite.setSuiteName(suiteParser.name)
    for testCase in resultTestCaseList.tests:
        htmlTestCase = TestCase()
        htmlTestCase.setCaseName(testCase.name)
        htmlTestCase.setCaseStatus(TestCaseStatus.ERROR)
        testOwner = None
        testSqlId = None
        for resultTestCaseTag in testCase.tags:
            resultTestCaseTag = str(resultTestCaseTag.strip()).lower()
            if resultTestCaseTag.startswith('owner:'):
                if testOwner is None:
                    testOwner = resultTestCaseTag[6:].strip()
            if resultTestCaseTag.startswith('sqlid:'):
                if testSqlId is None:
                    testSqlId = resultTestCaseTag[6:].strip()
        htmlTestCase.setCaseOwner(testOwner)
        htmlTestCase.setCaseStartTime("____-__-__ __:__:__")
        htmlTestCase.setCaseElapsedTime(0)
        if testSqlId is None:
            htmlTestCase.setErrorStackTrace(
                "SQL_ID missed in catalog and robot. Not started.")
            htmlTestCase.setDownloadURLLink("javascript:void(0)")
        else:
            if testSqlId.lower() == "none":
                htmlTestCase.setErrorStackTrace(
                    "SQL_ID missed in catalog. Not started.")
                htmlTestCase.setDownloadURLLink("javascript:void(0)")
            else:
                htmlTestCase.setErrorStackTrace(
                    "Case fatal error. Not started.")
                htmlTestCase.setDownloadURLLink(reportDir + ".tar")
        htmlTestCase.setDetailReportLink("javascript:void(0)")
        htmlTestSuite.addTestCase(htmlTestCase)

    # 分析运行结果，一个目录下目前只有一个suite
    cls.logger.info("分析测试结果 ....")
    xmlResultFile = os.path.join(
        os.environ['T_WORK'], reportDir, reportDir + ".xml")
    if os.path.exists(xmlResultFile):
        cls.logger.info("分析测试结果， 读取XML结果文件 ....")
        # 有xml结果文件
        try:
            robotResults = ExecutionResult(xmlResultFile)
        except robot.errors.DataError:
            # 文件不完整，修正XML后重新运行
            cls.logger.info(
                "Result file [" + str(xmlResultFile) + "] is incomplete xml file, fix it.")
            with open(xmlResultFile, encoding="UTF-8", mode="r") as infile:
                fixed = str(RobotXMLSoupParser(
                    infile, features='xml'))
            with open(xmlResultFile, encoding="UTF-8", mode='w') as outfile:
                outfile.write(fixed)
            try:
                robotResults = ExecutionResult(xmlResultFile)
            except robot.errors.DataError:
                # 文件存在问题，还是无法解析
                cls.logger.error(
                    "Result file [" + str(xmlResultFile) + "] is not a valid xml file, ignore it.")
                return

        cls.logger.info("分析测试结果， 分析XML结果文件 ....")
        robotSuiteResultList = []
        if len(robotResults.suite.suites) == 0:
            robotSuiteResultList.append(robotResults.suite)
        else:
            for resultTestSuite in robotResults.suite.suites:
                robotSuiteResultList.append(resultTestSuite)
        for robotSuiteResult in robotSuiteResultList:
            for robotCaseResult in robotSuiteResult.tests:
                cls.logger.info(
                    "分析测试结果， 加载测试结果 【" + str(robotSuiteResult.source) + ":" +
                    str(robotCaseResult.name) + "】 ....")
                robotCaseFinished = True
                htmlTestCase = TestCase()
                htmlTestCase.setCaseName(robotCaseResult.name)
                robotCaseTagList = []
                # 从robot文件中去查找tag， 随后获得owner
                robotParser = RobotParser()
                suiteParser = robotParser.parse_suite_file(
                    source=robotSuiteResult.source)
                resultTestCaseList = cls.TestCasesFinder()
                suiteParser.visit(resultTestCaseList)
                for testCase in resultTestCaseList.tests:
                    if testCase.name == robotCaseResult.name:
                        robotCaseTagList = testCase.tags
                        break
                testOwner = None
                for resultTestTag in robotCaseTagList:
                    resultTestTag = str(resultTestTag.strip()).lower()
                    if resultTestTag.startswith('owner:'):
                        if testOwner is None:
                            testOwner = resultTestTag[6:].strip()
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
                    startTime = datetime.datetime.strptime(
                        robotCaseResult.starttime[:17], "%Y%m%d %H:%M:%S")
                else:
                    # 不确定的test开始时间, 可能是由于Case没有运行完成，robot文件损坏
                    # 这时将Robot的开始时间作为test的开始时间,并且标记测试为失败
                    startTime = datetime.datetime.fromtimestamp(
                        os.path.getctime(xmlResultFile))
                    htmlTestCase.setCaseStatus(
                        TestCaseStatus.ERROR)
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
                    endTime = datetime.datetime.fromtimestamp(
                        os.path.getmtime(xmlResultFile))
                    htmlTestCase.setCaseStatus(
                        TestCaseStatus.ERROR)
                    robotCaseFinished = False
                htmlTestCase.setCaseElapsedTime(
                    (endTime - startTime).seconds)
                if not robotCaseFinished:
                    htmlTestCase.setErrorStackTrace(
                        "测试致命错误， 由于超时被停止！")
                else:
                    htmlTestCase.setErrorStackTrace(
                        robotSuiteResult.message)
                subHtmlReportFile = os.path.join(
                    os.environ['T_WORK'], reportDir, reportDir + ".html")

                cls.logger.info("分析测试结果， 生成测试报告 【" + str(robotSuiteResult.source) + ":" + str(
                    robotCaseResult.name) + "】 ....")

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
                    ["--outputdir", os.environ['T_WORK']])
                resultRebotArgs.extend(
                    ["--logtitle", "测试报告-" + robotSuiteResult.name])
                resultRebotArgs.extend(
                    ["--reporttitle", "测试报告-" + robotSuiteResult.name])
                resultRebotArgs.extend(
                    ["--name", "测试报告-" + robotSuiteResult.name])
                resultRebotArgs.extend(["--log", subHtmlReportFile])
                resultRebotArgs.extend(["--report", "NONE"])
                resultRebotArgs.extend(["--output", "NONE"])
                resultRebotArgs.append("--nostatusrc")

                # 生成测试报告信息
                resultXmlList = [
                    os.path.abspath(os.path.join(os.environ['T_WORK'], reportDir, reportDir + ".xml"))]
                resultRebotArgs.extend(resultXmlList)
                rebot_cli(resultRebotArgs, exit=False)
                htmlTestCase.setDetailReportLink(reportDir + ".html#" + robotCaseResult.id)
                htmlTestCase.setDownloadURLLink(reportDir + ".tar")
                htmlTestSuite.addTestCase(htmlTestCase)

    # 汇总运行结果
    cls.logger.info("汇总测试结果 ....")
    htmlTestSuite.SummaryTestCase()
    return htmlTestSuite


# 整理被忽略的测试用例，这些用例也要反映到报告中
def generateIgnoredRobotReport(cls, ignoredRobotTask):
    # 被忽略的任务也要放入到报告中
    htmlTestSuite = TestSuite()

    robotPath = ignoredRobotTask["robotfile"]
    # 解析Robot文件，将所有Robot的测试用例标记为失败
    # 下一步即使测试程序退出，这里的结果将作为最终的失败结果参考
    robotParser = RobotParser()
    suiteParser = robotParser.parse_suite_file(source=robotPath)
    resultTestCaseList = cls.TestCasesFinder()
    suiteParser.remove_empty_suites(True)
    suiteParser.filter(excluded_tags=["FILTERED"])
    suiteParser.visit(resultTestCaseList)
    htmlTestSuite.setSuiteName(suiteParser.name)
    if len(resultTestCaseList.tests) == 0:
        return None
    for testCase in resultTestCaseList.tests:
        htmlTestCase = TestCase()
        htmlTestCase.setCaseName(testCase.name)
        htmlTestCase.setCaseStatus(TestCaseStatus.ERROR)
        testOwner = None
        for resultTestCaseTag in testCase.tags:
            resultTestCaseTag = str(resultTestCaseTag.strip()).lower()
            if resultTestCaseTag.startswith('owner:'):
                if testOwner is None:
                    testOwner = resultTestCaseTag[6:].strip()
        htmlTestCase.setCaseOwner(testOwner)
        htmlTestCase.setCaseStartTime("____-__-__ __:__:__")
        htmlTestCase.setCaseElapsedTime(0)
        htmlTestCase.setErrorStackTrace(
            "SQL_ID missed in catalog. Not started.")
        htmlTestCase.setDownloadURLLink("javascript:void(0)")
        htmlTestCase.setDetailReportLink("javascript:void(0)")
        htmlTestSuite.addTestCase(htmlTestCase)

    htmlTestSuite.SummaryTestCase()
    return htmlTestSuite
