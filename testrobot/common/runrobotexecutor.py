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

    # ???????????????????????????
    LOG_FORMAT = "%(asctime)s -  %(name)15s-[%(process)8d] - %(levelname)9s - %(message)s"
    LOG_FORMAT2 = "%(asctime)s - %(levelname)9s - %(message)s"
    logFormat = logging.Formatter(LOG_FORMAT)
    logFormat2 = logging.Formatter(LOG_FORMAT2)
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormat)

    # ??????PR??????
    os.environ["PR_COMPARE"] = "1"

    # ??????????????????
    workingDirectory = os.path.join(
        os.getenv("T_WORK"), args["workingDirectory"])
    os.makedirs(workingDirectory, exist_ok=True)

    # ???????????????????????????
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

    # ?????????????????????????????????log??????
    logging.getLogger('hdfs.client').setLevel(level=logging.ERROR)
    logging.getLogger('urllib3.connectionpool').setLevel(
        level=logging.ERROR)
    logging.getLogger("paramiko").setLevel(level=logging.ERROR)

    try:
        # ???????????????Robot??????
        robotFile = args["testrobot"]

        # Robot??????????????????
        testStatistics = args["statistics"]

        # JobId,workingDirectory
        workingDirectory = args["workingDirectory"]

        robotOptions = args["robotOptions"]
        logger.info("?????????????????? ???" + robotFile + "???...")

        # ?????????????????????????????????????????????Case?????????????????????case???????????????6???????????????
        # 6?????????????????????????????????Case???????????????
        testName = os.path.basename(robotFile)[:-len(".robot")]
        upperWorkingDirectory = os.getenv("T_WORK")

        # ????????????robot?????????????????????
        os.makedirs(os.path.join(os.getenv("T_WORK"),
                                 workingDirectory), exist_ok=True)

        # ??????????????????????????????
        if not os.path.exists(robotFile):
            logger.error(
                "File [" + robotFile + "] does not exist! task failed.")
            return 1

        # ????????????????????????
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

        # ?????????????????????????????????????????????????????????robot?????????????????????
        oldDirectory = os.getcwd()
        os.chdir(os.path.dirname(robotFile))
        os.environ['T_WORK'] = os.path.join(
            os.getenv("T_WORK"), workingDirectory)

        # ?????????????????????????????????Robot?????????????????????????????????NOT_STARTED
        # ???????????????????????????????????????
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

        # ??????????????????
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
        logger.info("????????????????????? ")
        for robotOption in robotOptions:
            logger.info("    " + str(robotOption))
        rc = run_robot(robotOptions, exit=False)
        logger.info("?????????????????? [" + robotFile + "]. ???????????? =[" + str(rc) + "]")

        # ??????XML???????????????????????????????????????JSON??????
        xmlResultFile = os.path.abspath(os.path.join(
            os.environ['T_WORK'], workingDirectory + ".xml"))
        try:
            ExecutionResult(xmlResultFile).suite
        except DataError:
            # ????????????????????????XML???????????????
            logger.info("???????????? ???" + str(xmlResultFile) + "??? ???????????????????????????.")
            with open(xmlResultFile, encoding="UTF-8", mode="r") as infile:
                fixed = str(RobotXMLSoupParser(infile, features='xml'))
            with open(xmlResultFile, encoding="UTF-8", mode='w') as outfile:
                outfile.write(fixed)

        # ?????????????????????????????????
        sys.__stdout__ = saved__Stdout
        sys.__stderr__ = saved__Stderr
        sys.stdout = m_SavedStdout
        sys.stderr = m_SavedStderr
        stdoutFile.close()
        stderrFile.close()

        # ????????????????????????
        os.chdir(oldDirectory)
        os.environ['T_WORK'] = upperWorkingDirectory

        # ????????????????????????????????????????????????, ???????????????????????????
        testStatistics.append(list(testCaseResults.values()))
    except Exception:
        print('traceback.print_exc():\n%s' % traceback.print_exc())
        print('traceback.format_exc():\n%s' % traceback.format_exc())
