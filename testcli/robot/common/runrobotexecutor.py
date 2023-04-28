# -*- coding: utf-8 -*-
import os
import sys
import logging
from robot.running.builder import RobotParser
from robot.model import SuiteVisitor
from robot.run import run_cli as run_robot
from robot.api import ExecutionResult
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
    class TestCasesFinder(SuiteVisitor):
        def __init__(self):
            self.tests = []

        def visit_test(self, test):
            self.tests.append(test)

    # 禁止掉一些不必要显示的log信息
    logging.getLogger('hdfs.client').setLevel(level=logging.ERROR)
    logging.getLogger('urllib3.connectionpool').setLevel(level=logging.ERROR)
    logging.getLogger("paramiko").setLevel(level=logging.ERROR)

    # 保存之前的输入输出和环境信息
    saved__Stdout = sys.__stdout__
    saved__Stderr = sys.__stderr__
    savedStdout = sys.stdout
    savedStderr = sys.stderr
    stdoutFile = None
    stderrFile = None
    oldDirectory = os.getcwd()
    upperWorkingDirectory = os.getenv("T_WORK")

    try:
        # 建立工作目录
        workingDirectory = os.path.join(
            os.getenv("T_WORK"), args["workingDirectory"])
        os.makedirs(workingDirectory, exist_ok=True)

        # 初始化进程日志
        LOG_FORMAT = "%(asctime)s - %(levelname)9s - %(message)s"
        logFormat = logging.Formatter(LOG_FORMAT)
        fileLogHandler = logging.FileHandler(
            filename=os.path.join(workingDirectory, "runRobotExecutor.log"),
            mode="a",
            encoding="UTF-8")
        fileLogHandler.setFormatter(logFormat)
        logger = logging.getLogger("runRobotExecutor")
        logger.setLevel(logging.INFO)
        logger.addHandler(fileLogHandler)

        # 需要运行的Robot文件
        robotFile = args["testrobot"]

        # JobId,workingDirectory
        workingDirectory = args["workingDirectory"]

        robotOptions = args["robotOptions"]
        logger.info("Begin to execute [" + robotFile + "] ...")

        # 准备一个新的工作目录，用来存放Case的结果，目录用case的名称加上6位随机数字
        # 6位随机数字的原因是有的Case可能会同名
        testName = os.path.basename(robotFile)[:-len(".robot")]

        # 建立随后robot运行的工作目录
        os.makedirs(os.path.join(os.getenv("T_WORK"),
                                 workingDirectory), exist_ok=True)

        # 检查文件路径是否存在
        if not os.path.exists(robotFile):
            raise RegressException("File [" + robotFile + "] does not exist! task failed.")

        # 切换标准输入输出
        stdoutFile = open(os.path.join(
            os.getenv("T_WORK"), workingDirectory, testName + ".stdout"), 'w')
        stderrFile = open(os.path.join(
            os.getenv("T_WORK"), workingDirectory, testName + ".stderr"), 'w')
        sys.__stdout__ = stdoutFile
        sys.__stderr__ = stderrFile
        sys.stdout = stdoutFile
        sys.stderr = stderrFile

        # 记录当前的文件目录位置，切换工作目录到robot文件所在的目录
        os.chdir(os.path.dirname(robotFile))

        # 重置T_WORK到子目录下
        os.environ['T_WORK'] = os.path.join(os.getenv("T_WORK"), workingDirectory)

        # 生成测试运行结果，根据Robot的解析情况，一律标记为NOT_STARTED
        # 随后会被正式的测试结果更新
        testSuiteResults = {}
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
            "--loglevel", "INFO",
            "--log", "NONE",
            "--report", "NONE",
            "--exclude", "sqlId:None",
            "--exclude", "FILTERED",
            "--output", workingDirectory + ".xml",
            "--outputdir", os.environ['T_WORK'],
            robotFile, ])
        logger.info("Runtime args:")
        for robotOption in robotOptions:
            logger.info("    " + str(robotOption))
        rc = run_robot(robotOptions, exit=False)
        logger.info("Finished test [" + robotFile + "]. ret=[" + str(rc) + "]")

        # 根据XML文件生成一个测试数据的汇总JSON信息
        xmlResultFile = os.path.abspath(os.path.join(os.environ['T_WORK'], workingDirectory + ".xml"))
        try:
            ExecutionResult(xmlResultFile).suite
        except DataError:
            # 文件不完整，修正XML后重新运行
            logger.info("Result file [" + str(xmlResultFile) + "] is incomplete. Try to fix it.")
            with open(xmlResultFile, encoding="UTF-8", mode="r") as infile:
                fixed = str(RobotXMLSoupParser(infile, features='xml'))
            with open(xmlResultFile, encoding="UTF-8", mode='w') as outfile:
                outfile.write(fixed)
    except RegressException as ex:
        raise ex
    finally:
        # 切换回原工作目录
        os.chdir(oldDirectory)
        os.environ['T_WORK'] = upperWorkingDirectory

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
