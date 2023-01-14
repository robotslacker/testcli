# -*- coding: utf-8 -*-
import os
import sys
import logging
import traceback

import coloredlogs
from robot.running.builder import RobotParser
from robot.model import SuiteVisitor
from robot.run import run_cli as run_robot
from robot.api import ExecutionResult
from robot.errors import DataError
from bs4 import BeautifulSoup


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


# Added by wenliang for filter out braces
def remove_braces(error_msg, begin_brace, end_brace):

    index_list = []
    start_index = error_msg.find(begin_brace)
    if start_index > 0:
        brace_count = 1
        index_list.append(start_index)
        end_index = len(error_msg)
        for i in range(start_index + 1, end_index):
            if error_msg[i: i+1] == begin_brace:
                if brace_count == 0:
                    index_list.append(i)
                brace_count = brace_count + 1

            if error_msg[i: i+1] == end_brace:
                brace_count = brace_count - 1

            if brace_count == 0 and (len(index_list) + 1) % 2 == 0:
                index_list.append(i)

    if len(index_list) > 0:
        end_index = 0
        j = 0
        return_msg = ""
        while j < len(index_list):
            start_index = index_list[j]
            filter_msg = error_msg[end_index: start_index]
            return_msg = return_msg + filter_msg
            if j + 1 < len(index_list):
                end_index = index_list[j + 1] + 1
            j = j + 2

        if end_index < len(error_msg):
            return_msg = return_msg + error_msg[end_index:]
        return return_msg

    return error_msg


def runRobotExecutor(args):
    class TestCasesFinder(SuiteVisitor):
        def __init__(self):
            self.tests = []

        def visit_test(self, test):
            self.tests.append(test)

    # 设置程序的日志级别
    LOG_FORMAT = "%(asctime)s -  %(name)15s-[%(process)8d] - %(levelname)9s - %(message)s"
    LOG_FORMAT2 = "%(asctime)s - %(levelname)9s - %(message)s"
    logFormat = logging.Formatter(LOG_FORMAT)
    logFormat2 = logging.Formatter(LOG_FORMAT2)
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormat)

    # 开启PR模式
    os.environ["PR_COMPARE"] = "1"

    # 建立工作目录
    workingDirectory = os.path.join(
        os.getenv("T_WORK"), args["workingDirectory"])
    os.makedirs(workingDirectory, exist_ok=True)

    # 将把日志内容输出到
    fileLogHandler = logging.FileHandler(
        filename=os.path.join(
            workingDirectory, "farmregress-executor.log"),
        mode="a",
        encoding="UTF-8")
    fileLogHandler.setFormatter(logFormat2)
    if "LOG_LEVEL" in os.environ:
        logLevel = os.environ["LOG_LEVEL"].upper().strip()
    else:
        logLevel = "INFO"
    if logLevel == "INFO":
        consoleHandler.setLevel(logging.INFO)
        fileLogHandler.setLevel(logging.INFO)
    elif logLevel == "DEBUG":
        consoleHandler.setLevel(logging.DEBUG)
        fileLogHandler.setLevel(logging.DEBUG)
    elif logLevel == "WARNING":
        consoleHandler.setLevel(logging.WARNING)
        fileLogHandler.setLevel(logging.WARNING)
    elif logLevel == "ERROR":
        consoleHandler.setLevel(logging.ERROR)
        fileLogHandler.setLevel(logging.ERROR)
    elif logLevel == "CRITICAL":
        consoleHandler.setLevel(logging.CRITICAL)
        fileLogHandler.setLevel(logging.CRITICAL)
    else:
        logLevel = "INFO"
        consoleHandler.setLevel(logging.INFO)
        fileLogHandler.setLevel(logging.INFO)

    logger = logging.getLogger("runRobotExecutor.py")

    logger.addHandler(fileLogHandler)
    coloredlogs.install(
        level=consoleHandler.level,
        fmt=LOG_FORMAT,
        logger=logger,
        isatty=True
    )

    # 禁止掉一些不必要显示的log信息
    logging.getLogger('hdfs.client').setLevel(level=logging.ERROR)
    logging.getLogger('urllib3.connectionpool').setLevel(
        level=logging.ERROR)
    logging.getLogger("paramiko").setLevel(level=logging.ERROR)

    try:
        # 需要运行的Robot文件
        robotFile = args["testrobot"]

        # Robot文件统计信息
        testStatistics = args["statistics"]

        # JobId,workingDirectory
        workingDirectory = args["workingDirectory"]

        robotOptions = args["robotOptions"]
        logger.info("开始执行测试 【" + robotFile + "】...")

        # 准备一个新的工作目录，用来存放Case的结果，目录用case的名称加上6位随机数字
        # 6位随机数字的原因是有的Case可能会同名
        testName = os.path.basename(robotFile)[:-len(".robot")]
        upperWorkingDirectory = os.getenv("T_WORK")

        # 建立随后robot运行的工作目录
        os.makedirs(os.path.join(os.getenv("T_WORK"),
                                 workingDirectory), exist_ok=True)

        # 检查文件路径是否存在
        if not os.path.exists(robotFile):
            logger.error(
                "File [" + robotFile + "] does not exist! task failed.")
            return 1

        # 切换标准输入输出
        stdoutFile = open(os.path.join(
            os.getenv("T_WORK"), workingDirectory, testName + ".stdout"), 'w')
        stderrFile = open(os.path.join(
            os.getenv("T_WORK"), workingDirectory, testName + ".stderr"), 'w')
        saved__Stdout = sys.__stdout__
        saved__Stderr = sys.__stderr__
        m_SavedStdout = sys.stdout
        m_SavedStderr = sys.stderr
        sys.__stdout__ = stdoutFile
        sys.__stderr__ = stderrFile
        sys.stdout = stdoutFile
        sys.stderr = stderrFile

        # 记录当前的文件目录位置，切换工作目录到robot文件所在的目录
        oldDirectory = os.getcwd()
        os.chdir(os.path.dirname(robotFile))
        os.environ['T_WORK'] = os.path.join(
            os.getenv("T_WORK"), workingDirectory)

        # 生成测试运行结果，根据Robot的解析情况，一律标记为NOT_STARTED
        # 随后会被正式的测试结果更新
        testSuiteResults = {}
        testCaseResults = {}
        robotParser = RobotParser().parse_suite_file(source=robotFile)
        # will not filter sqlid:none
        robotParser.remove_empty_suites(True)
        testCaseParserList = TestCasesFinder()
        robotParser.visit(testCaseParserList)
        testSuiteResult = {
            "Suite_Name": str(robotParser.name),
            "Start_Time": "-------- --:--:--.---",
            "End_Time": "-------- --:--:--.---",
            "Status": "NOT_STARTED",
            "RobotPath": robotFile,
            "ValidCase": robotParser.test_count
        }
        testSuiteResults[str(robotParser)] = testSuiteResult
        for robotTest in testCaseParserList.tests:
            tagList = []
            for tag in robotTest.tags:
                tag = str(tag.strip()).lower()
                if tag.startswith('runlevel:'):
                    pass
                else:
                    tagList.append(tag)

        # 拼接测试选项
        if robotOptions is None:
            robotOptions = []
        else:
            robotOptions = robotOptions.split()
        robotOptions.extend([
            "--loglevel", logLevel,
            "--log", "NONE",
            "--report", "NONE",
            "--exclude", "sqlId:None",
            "--exclude", "FILTERED",
            "--output", workingDirectory + ".xml",
            "--outputdir", os.environ['T_WORK'],
            robotFile, ])
        logger.info("程序运行选项： ")
        for robotOption in robotOptions:
            logger.info("    " + str(robotOption))
        rc = run_robot(robotOptions, exit=False)
        logger.info("结束执行测试 [" + robotFile + "]. 返回代码 =[" + str(rc) + "]")

        # 根据XML文件生成一个测试数据的汇总JSON信息
        xmlResultFile = os.path.abspath(os.path.join(
            os.environ['T_WORK'], workingDirectory + ".xml"))
        try:
            ExecutionResult(xmlResultFile).suite
        except DataError:
            # 文件不完整，修正XML后重新运行
            logger.info("结果文件 【" + str(xmlResultFile) + "】 不完整，会尝试修正.")
            with open(xmlResultFile, encoding="UTF-8", mode="r") as infile:
                fixed = str(RobotXMLSoupParser(infile, features='xml'))
            with open(xmlResultFile, encoding="UTF-8", mode='w') as outfile:
                outfile.write(fixed)

        # 关闭打开的文件，并切换
        sys.__stdout__ = saved__Stdout
        sys.__stderr__ = saved__Stderr
        sys.stdout = m_SavedStdout
        sys.stderr = m_SavedStderr
        stdoutFile.close()
        stderrFile.close()

        # 切换回原工作目录
        os.chdir(oldDirectory)
        os.environ['T_WORK'] = upperWorkingDirectory

        # 将测试结果记录到共享的统计信息中, 便于主程序前台打印
        testStatistics.append(list(testCaseResults.values()))
    except Exception:
        print('traceback.print_exc():\n%s' % traceback.print_exc())
        print('traceback.format_exc():\n%s' % traceback.format_exc())