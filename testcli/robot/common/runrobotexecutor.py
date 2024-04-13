# -*- coding: utf-8 -*-
import os
import sys
import time
import json
import sqlite3
import logging
import datetime
import robot.errors
from robot.api import TestSuiteBuilder
from robot.api import ExecutionResult
from robot.run import run_cli as run_robot
from robot.errors import DataError
from robot import rebot_cli
from bs4 import BeautifulSoup
from .regressexception import RegressException


class RobotXMLSoupParser(BeautifulSoup):
    def insert_after(self, *args):
        pass

    def insert_before(self, *args):
        pass

    NESTABLE_TAGS = {'suite': ['testrobot', 'suite', 'statistics'],
                     'doc': ['suite', 'test', 'kw'],
                     'metadata': ['suite'],
                     'item': ['metadata'],
                     'status': ['suite', 'test', 'kw'],
                     'test': ['suite'],
                     'tags': ['test'],
                     'tag': ['tags'],
                     'kw': ['suite', 'test', 'kw'],
                     'msg': ['kw', 'errors'],
                     'arguments': ['kw'],
                     'arg': ['arguments'],
                     'statistics': ['testrobot'],
                     'errors': ['testrobot']}
    __close_on_open = None

    def unknown_starttag(self, name, attrs, selfClosing=0):
        if name == 'testrobot':
            attrs = [(key, value if key != 'generator' else 'robotfixml.py')
                     for key, value in attrs]
        if name == 'kw' and ('type', 'teardown') in attrs:
            while self.tagStack[-1].name not in ['test', 'suite']:
                self._popToTag(self.tagStack[-1].name)
        if self.__close_on_open:
            self._popToTag(self.__close_on_open)
            self.__close_on_open = None
        BeautifulSoup.unknown_starttag(self, name, attrs, selfClosing)

    def unknown_endtag(self, name):
        BeautifulSoup.unknown_endtag(self, name)
        if name == 'status':
            self.__close_on_open = self.tagStack[-1].name
        else:
            self.__close_on_open = None


def generateRobotExecutorReport(
        logger,
        testRoot: str,
        workingDirectory: str,
        subDirectory: str,
        robotFile: str,
        robotOptions: [],
        startTime,
        endTime
):
    # 约定文件名称
    subHtmlReportFile = os.path.join(workingDirectory, subDirectory, os.path.basename(subDirectory) + ".html")
    subXmlReportFile = os.path.join(workingDirectory, subDirectory, os.path.basename(subDirectory) + ".xml")

    # 记录所有被过滤掉的Tag标记
    filteredTags = []
    for pos in range(0, len(robotOptions)):
        if robotOptions[pos] == "--exclude" and pos < (len(robotOptions) - 1):
            filteredTags.append(robotOptions[pos + 1])

    # 获取Robot源文件的基础信息
    metaData = {}
    caseList = []
    try:
        robotSuite = TestSuiteBuilder().build(robotFile)
        for metaKey, metaValue in robotSuite.metadata.items():
            metaData.update(
                {
                    metaKey: metaValue
                }
            )
        for testCase in robotSuite.tests:
            isFilteredCase = False
            for resultTestCaseTag in testCase.tags:
                if resultTestCaseTag in filteredTags:
                    isFilteredCase = True
                    break
            caseList.append(
                {
                    "caseName": testCase.name,
                    "caseTags": [str(s) for s in testCase.tags if str(s).strip() not in ["|"]],
                    "isSkiped": isFilteredCase
                }
            )
    except robot.errors.DataError as re:
        raise RegressException("Failed to execute [" + str(robotFile) + "], " + str(re.message))

    # 利用RobotFramework的内置功能生成该测试的HTML测试报告
    resultRebotArgs = []
    resultRebotArgs.extend(["--tagstatexclude", "owner*"])
    resultRebotArgs.extend(["--tagstatexclude", "feature*"])
    resultRebotArgs.extend(["--tagstatexclude", "runLevel*"])
    resultRebotArgs.extend(["--tagstatexclude", "priority*"])
    resultRebotArgs.extend(["--suitestatlevel", "2"])
    resultRebotArgs.extend(["--outputdir", workingDirectory])
    resultRebotArgs.extend(["--logtitle", "Test Report-" + robotSuite.name])
    resultRebotArgs.extend(["--reporttitle", "Test Report-" + robotSuite.name])
    resultRebotArgs.extend(["--name", "Test Report-" + robotSuite.name])
    resultRebotArgs.extend(["--log", subHtmlReportFile])
    resultRebotArgs.extend(["--report", "NONE"])
    resultRebotArgs.extend(["--output", "NONE"])
    resultRebotArgs.append("--nostatusrc")
    resultRebotArgs.extend([subXmlReportFile])

    # 生成测试报告
    logger.info("Execute Rebot_Cli: ")
    formattedArgs = []
    for arg in resultRebotArgs:
        if arg.startswith("--"):
            formattedArgs.append(arg)
        else:
            formattedArgs[-1] = formattedArgs[-1] + " " + arg
    for arg in formattedArgs:
        logger.info("    " + str(arg))
    rc = rebot_cli(resultRebotArgs, exit=False)
    logger.info("Finished rebot [" + robotFile + "]. ret=[" + str(rc) + "]")

    robotResults = None
    # 如果Robot运行结果文件不存在，表示这个Case彻底失败
    if not os.path.exists(subXmlReportFile):
        logger.warning("Result file [" + str(subXmlReportFile) + "] is missed. Case blowout.")
    else:
        # 分析Robot的运行结果文件，并汇总结果到JSON中
        try:
            robotResults = ExecutionResult(subXmlReportFile).suite
        except DataError:
            # 文件不完整，修正XML后重新运行
            # 大概率是因为Robot没有运行结束，导致丢失了部分数据
            logger.warning("Result file [" + str(subXmlReportFile) + "] is incomplete. Try to fix it.")
            with open(subXmlReportFile, encoding="UTF-8", mode="r") as infile:
                fixed = str(RobotXMLSoupParser(infile, features='xml'))
            with open(subXmlReportFile, encoding="UTF-8", mode='w') as outfile:
                outfile.write(fixed)
            # 修复后尝试重新读取内容
            try:
                robotResults = ExecutionResult(subXmlReportFile).suite
            except DataError as de:
                logger.error("Failed to analyze test result, "
                             "result file is broken. [" + subXmlReportFile + "]. " + str(de))

    # 可能是单Suite文件，也可能是多Suite文件，需要分开处理
    robotSuiteResultList = []
    if robotResults is not None:
        if len(robotResults.suites) == 0:
            robotSuiteResultList.append(robotResults)
        else:
            for resultTestSuite in robotResults.suites:
                robotSuiteResultList.append(resultTestSuite)

    # 记录测试用例的情况
    caseResultList = []
    for robotSuiteResult in robotSuiteResultList:
        for robotCaseResult in robotSuiteResult.tests:
            caseStartTime = robotCaseResult.starttime
            caseEndTime = robotCaseResult.endtime
            if len(str(caseStartTime).strip()) >= 17:
                caseStartTime = (
                    datetime.datetime.strptime(
                        caseStartTime[:17], "%Y%m%d %H:%M:%S"
                    ).strftime("%Y-%m-%d %H:%M:%S"))
            else:
                caseStartTime = ""
            if len(str(caseEndTime).strip()) >= 17:
                caseEndTime = (
                    datetime.datetime.strptime(
                        caseEndTime[:17], "%Y%m%d %H:%M:%S"
                    ).strftime("%Y-%m-%d %H:%M:%S"))
            else:
                caseEndTime = ""
            caseTags = [str(tag).strip() for tag in robotCaseResult.tags if str(tag).strip() != "|"]
            caseResultList.append(
                {
                    "id": str(robotCaseResult.id),
                    "caseName": str(robotCaseResult.name),
                    "caseTags": caseTags,
                    "caseStatus": str(robotCaseResult.status),
                    "message": str(robotCaseResult.message),
                    "startTime": caseStartTime,
                    "endTime": caseEndTime
                }
            )

    # 记录Scenario情况
    scenarioResultDict = {}
    # 分别从2个维度去看测试场景情况，分别是xdb文件, xlog文件
    # 首先从xdb文件分析，如果能找到，则优先处理xdb。 如果存在xlog文件，则xlog覆盖xdb的结果
    # 如果存在xdb，则处理xdb文件
    for root, dirs, files in os.walk(os.path.join(workingDirectory, subDirectory)):
        for f in files:
            if f.endswith(".xdb"):
                logger.info("  Process xdb file [" + str(f) + "]....")
                xdbtestlog = os.path.abspath(os.path.join(root, str(f)))

                xdbFileHandle = sqlite3.connect(xdbtestlog)
                cursor = xdbFileHandle.cursor()
                cursor.execute("SELECT * FROM TestCli_Xlog Order by Id")
                rs = cursor.fetchall()
                field_names = [i[0] for i in cursor.description]
                cursor.close()
                data = []
                for row in rs:
                    rowMap = {}
                    for i in range(0, len(row)):
                        rowMap[field_names[i]] = row[i]
                    data.append(rowMap)
                for row in data:
                    scenarioId = row["ScenarioId"]
                    scenarioName = row["ScenarioName"]

                    # 统计测试场景的运行时间
                    if row["CommandType"] in ["ASSERT", "SCRIPT", "PYTHONSCRIPT"] and row["ErrorCode"] != "0":
                        scenarioStatus = "FAIL"
                    else:
                        scenarioStatus = "PASS"
                    # 第一次插入一个记录，随后累计执行时间
                    if scenarioId not in scenarioResultDict.keys():
                        elapsed = row["Elapsed"]
                        scenarioResultDict[scenarioId] = {
                            "elapsed": round(elapsed, 2),
                            "caseName": row["CaseName"],
                            "scenarioName": scenarioName,
                            "scenarioStatus": scenarioStatus,
                            "scenarioMessage": "",
                        }
                    else:
                        scenarioResultDict[scenarioId].update(
                            {
                                "elapsed":
                                    round(float(scenarioResultDict[scenarioId]["elapsed"]) + float(row["Elapsed"]), 2),
                                "caseName": row["CaseName"],
                                "scenarioName": scenarioName,
                                "scenarioStatus": scenarioStatus,
                                "scenarioMessage": "",
                            }
                        )
                xdbFileHandle.close()

    # 如果存在xlog文件，则处理xlog文件
    for root, dirs, files in os.walk(os.path.join(workingDirectory, subDirectory)):
        for f in files:
            if f.endswith(".xlog"):
                logger.info("  Process xlog file [" + str(f) + "]....")
                xlogFile = open(os.path.join(root, str(f)), mode='r', encoding='UTF-8')
                xLogResult = json.load(xlogFile)
                for scenarioId, scenarioResult in xLogResult["ScenarioResults"].items():
                    if scenarioResult["Status"] in ["Successful", "PASS"]:
                        scenarioStatus = "PASS"
                    else:
                        scenarioStatus = "FAIL"
                    if scenarioId not in scenarioResultDict.keys():
                        scenarioResultDict[scenarioId] = \
                            {
                                "elapsed": 0.00,
                                "caseName": xLogResult["CaseName"],
                                "scenarioName": scenarioResult["Name"],
                                "scenarioStatus": scenarioStatus,
                                "scenarioMessage": scenarioResult["message"],
                            }
                    else:
                        # 如果一个测试场景反复出现，用最后一个的信息为准
                        scenarioResultDict[scenarioId].update(
                            {
                                "elapsed": round(scenarioResultDict[scenarioId]["elapsed"], 2),
                                "caseName": xLogResult["CaseName"],
                                "scenarioName": scenarioResultDict[scenarioId]["scenarioName"],
                                "scenarioStatus": scenarioStatus,
                                "scenarioMessage": scenarioResult["message"],
                            }
                        )
                xlogFile.close()

    # 将scenarioResult转换为一个列表信息
    scenarioResultList = []
    for key, value in scenarioResultDict.items():
        if key != "0" and str(key).strip() != "":
            scenarioResultList.append(
                {
                    "scenarioId": key,
                    "scenarioName": value["scenarioName"],
                    "caseName": value["caseName"],
                    "scenarioStatus": value["scenarioStatus"],
                    "scenarioMessage": value["scenarioMessage"],
                    "elapsed": value["elapsed"]
                }
            )

    # 汇总测试数据，生成summary文件
    jobSummary = {}
    if startTime is None:
        startTime = datetime.datetime.fromtimestamp(os.path.getctime(subXmlReportFile)).strftime("%Y-%m-%d %H:%M:%S")
    if endTime is None:
        endTime = startTime
    if isinstance(robotOptions, list):
        robotOptions = " ".join(robotOptions)
    jobSummary.update(
        {
            "robotFile": str(os.path.relpath(robotFile, testRoot)),
            "suiteName": str(robotSuite.name),
            "metadata": metaData,
            "startTime": startTime,
            "endTime": endTime,
            "robotOptions": robotOptions,
            "filteredTags": filteredTags,
            "caseList": caseList,
            "caseResultList": caseResultList,
            "scenarioResultList": scenarioResultList
        }
    )
    # 将结果写入文件记录
    with open(file=os.path.join(workingDirectory, subDirectory, "jobSummary.json"), mode="w", encoding="utf-8") as fp:
        json.dump(jobSummary, fp=fp, indent=4, ensure_ascii=False)


def runRobotExecutor(args):
    # 禁止掉一些不必要显示的log信息
    logging.getLogger('hdfs.client').setLevel(level=logging.ERROR)
    logging.getLogger('urllib3.connectionpool').setLevel(level=logging.ERROR)
    logging.getLogger("paramiko").setLevel(level=logging.ERROR)
    logger = logging.getLogger("runRobotExecutor")

    # 保存之前的输入输出和环境信息
    saved__Stdout = sys.__stdout__
    saved__Stderr = sys.__stderr__
    savedStdout = sys.stdout
    savedStderr = sys.stderr
    stdoutFile = None
    stderrFile = None
    oldDirectory = os.getcwd()

    try:
        # 设置进程的名称，来标记当前运行的脚本
        import setproctitle
        setproctitle.setproctitle('TestCliRobot: ' + str(args["workingDirectory"]))

        # 建立工作目录
        workingDirectory = args["workingDirectory"]
        os.makedirs(workingDirectory, exist_ok=True)

        # 重置T_WORK到子目录下
        os.environ['T_WORK'] = workingDirectory
        # 记录测试唯一ID
        os.environ['T_RUNID'] = str(args["testRunId"])

        # 初始化进程日志
        LOG_FORMAT = "%(asctime)s - %(levelname)9s - %(message)s"
        logFormat = logging.Formatter(LOG_FORMAT)
        fileLogHandler = logging.FileHandler(
            filename=os.path.join(workingDirectory, "runRobotExecutor.log"),
            mode="a",
            encoding="UTF-8")
        fileLogHandler.setFormatter(logFormat)
        logger.setLevel(logging.INFO)
        logger.addHandler(fileLogHandler)

        # 需要运行的Robot文件
        robotFile = args["robotFile"]
        testName = os.path.basename(robotFile)[:-len(".robot")]
        robotOptions = args["robotOptions"]
        logger.info("Begin to execute [" + robotFile + "] ...")

        # 检查文件路径是否存在
        if not os.path.exists(robotFile):
            raise RegressException("Robot File [" + robotFile + "] does not exist! task failed.")

        # 切换标准输入输出
        stdoutFile = open(os.path.join(workingDirectory, testName + ".stdout"), 'w')
        stderrFile = open(os.path.join(workingDirectory, testName + ".stderr"), 'w')
        sys.__stdout__ = stdoutFile
        sys.__stderr__ = stderrFile
        sys.stdout = stdoutFile
        sys.stderr = stderrFile

        # 记录当前的文件目录位置，切换工作目录到robot文件所在的目录
        os.chdir(os.path.dirname(robotFile))

        # 重置T_WORK到子目录下
        # 如果运行的外部环境已经强行设置了这两个变量，则不会考虑去覆盖
        # 如果参数已经传递了，则直接使用参数中的变量
        # 如果参数没有传递，则默认为当前目录
        if "TEST_ROOT" not in os.environ:
            if args["testRoot"] is not None:
                # 如果参数提供了testRoot，以参数为准
                os.environ['TEST_ROOT'] = args["testRoot"]
            else:
                # 如果参数没有提供，以TEST_ROOT环境变量为准, 否则以当前目录上一级目录为准
                os.environ['TEST_ROOT'] = os.path.dirname(os.path.dirname(__file__))
        logger.info("TEST_ROOT [" + os.environ['TEST_ROOT'] + "]")

        # 将生成的xml结果文件，以及html报告文件
        subXmlReportFile = os.path.join(workingDirectory, os.path.basename(workingDirectory) + ".xml")

        # 拼接测试选项
        if robotOptions is None:
            robotOptions = []
        else:
            robotOptions = robotOptions.split()
        robotOptions.extend([
            "--loglevel", "INFO",
            "--log", "NONE",
            "--report", "NONE",
            "--output", os.path.basename(subXmlReportFile),
            "--outputdir", workingDirectory,
            robotFile, ])
        logger.info("Runtime args:")
        for robotOption in robotOptions:
            logger.info("    " + str(robotOption))

        # 记录所有被过滤掉的Tag标记
        filteredTags = []
        if robotOptions is not None:
            robotOptionList = str(robotOptions).split()
            for pos in range(0, len(robotOptionList)):
                if robotOptionList[pos] == "--exclude" and pos < (len(robotOptionList) - 1):
                    filteredTags.append(robotOptionList[pos+1])

        # 记录所有需要运行的testcase
        metaData = {}
        caseList = []
        try:
            robotSuite = TestSuiteBuilder().build(robotFile)
            for metaKey, metaValue in robotSuite.metadata.items():
                metaData.update(
                    {
                        metaKey: metaValue
                    }
                )
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
                        "caseTags": [str(s) for s in testCase.tags if str(s).strip() not in ["|"]],
                        "isSkiped": isFilteredCase
                    }
                )
            caseList.append(
                {
                    "cases": cases
                }
            )
        except robot.errors.DataError as re:
            raise RegressException("Failed to execute [" + str(robotFile) + "], " + str(re.message))

        # 开始运行测试
        startTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        rc = run_robot(robotOptions, exit=False)
        endTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        logger.info("Finished robot [" + robotFile + "]. ret=[" + str(rc) + "]")

        # 生成测试报告
        logger.info("Generate robot report [" + robotFile + "] ...")
        generateRobotExecutorReport(
            logger=logger,
            testRoot=os.environ['TEST_ROOT'],
            workingDirectory=os.path.abspath(os.path.dirname(workingDirectory)),
            subDirectory=os.path.basename(workingDirectory),
            robotFile=robotFile,
            robotOptions=robotOptions,
            startTime=startTime,
            endTime=endTime
        )

        # 结束运行测试
        logger.info("End execute [" + robotFile + "].")
    except RegressException as ex:
        raise ex
    finally:
        # 切换回原工作目录
        os.chdir(oldDirectory)

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

        # 移除所有的logHandler
        for handler in logger.handlers:
            logger.removeHandler(handler)
