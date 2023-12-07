# -*- coding: utf-8 -*-
import os
import sys
import time
import json
import logging
import robot.errors
from robot.api import TestSuiteBuilder
from robot.api import ExecutionResult
from robot.run import run_cli as run_robot
from robot.errors import DataError
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

        # JobId,workingDirectory
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
                # 如果参数没有提供，以TEST_ROOT环境变量为准, 否则以当前目录的上一级目录为准
                os.environ['TEST_ROOT'] = os.path.dirname(os.path.dirname(__file__))
        logger.info("TEST_ROOT [" + os.environ['TEST_ROOT'] + "]")

        # 拼接测试选项
        if robotOptions is None:
            robotOptions = []
        else:
            robotOptions = robotOptions.split()
        robotOptions.extend([
            "--loglevel", "INFO",
            "--log", "NONE",
            "--report", "NONE",
            "--output", os.path.basename(workingDirectory) + ".xml",
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
                        "caseTags": [str(s) for s in testCase.tags],
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
        logger.info("Finished test [" + robotFile + "]. ret=[" + str(rc) + "]")

        # 分析Robot的运行结果文件，并汇总结果到JSON中
        robotResults = None
        xmlResultFile = os.path.abspath(os.path.join(workingDirectory, os.path.basename(workingDirectory) + ".xml"),)
        if not os.path.exists(xmlResultFile):
            logger.warning("Result file [" + str(xmlResultFile) + "] is missed. " +
                           "Probably robot run with no invalid test case.")
        else:
            try:
                robotResults = ExecutionResult(xmlResultFile).suite
            except DataError:
                # 文件不完整，修正XML后重新运行
                # 大概率是因为Robot没有运行结束，导致丢失了部分数据
                logger.info("Result file [" + str(xmlResultFile) + "] is incomplete. Try to fix it.")
                with open(xmlResultFile, encoding="UTF-8", mode="r") as infile:
                    fixed = str(RobotXMLSoupParser(infile, features='xml'))
                with open(xmlResultFile, encoding="UTF-8", mode='w') as outfile:
                    outfile.write(fixed)
                # 修复后尝试重新读取内容
                try:
                    robotResults = ExecutionResult(xmlResultFile).suite
                except DataError as de:
                    raise RegressException("Failed to analyze test result, "
                                           "result file is broken. [" + xmlResultFile + "]. " + str(de))
        if robotResults is None:
            raise RegressException("Failed to analyze test result, "
                                   "result file is broken. [" + xmlResultFile + "].  None result.")
        # 可能是单Suite文件，也可能是多Suite文件，需要分开处理
        robotSuiteResultList = []
        if len(robotResults.suites) == 0:
            robotSuiteResultList.append(robotResults)
        else:
            for resultTestSuite in robotResults.suites:
                robotSuiteResultList.append(resultTestSuite)
        # 记录测试用例的情况
        caseResultList = []
        for robotSuiteResult in robotSuiteResultList:
            for robotCaseResult in robotSuiteResult.tests:
                caseResultList.append(
                    {
                        "caseName": str(robotCaseResult.name),
                        "caseStatus": str(robotCaseResult.status),
                        "startTime": str(robotCaseResult.starttime),
                        "endTime": str(robotCaseResult.endtime)
                    }
                )

        # 汇总测试数据，生成summary文件
        jobSummary = {}
        jobSummary.update(
            {
                "robotFile": str(os.path.relpath(robotFile, os.environ['TEST_ROOT'])),
                "suiteName": str(robotSuite.name),
                "metadata": metaData,
                "startTime": startTime,
                "endTime": endTime,
                "filteredTags": filteredTags,
                "caseList": caseList,
                "caseResultList": caseResultList
            }
        )
        # 将结果写入文件记录
        with open(file=os.path.join(workingDirectory, "jobSummary.json"), mode="w", encoding="utf-8") as fp:
            json.dump(jobSummary, fp=fp, indent=4, ensure_ascii=False)

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
