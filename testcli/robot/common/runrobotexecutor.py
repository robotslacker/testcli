# -*- coding: utf-8 -*-
import os
import sys
import logging
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
        # 建立工作目录
        workingDirectory = args["workingDirectory"]
        os.makedirs(workingDirectory, exist_ok=True)

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
        if 'T_WORK' not in os.environ:
            os.environ['T_WORK'] = workingDirectory
        if 'TEST_ROOT' not in os.environ:
            if args["testRoot"] is not None:
                os.environ['TEST_ROOT'] = args["testRoot"]
            else:
                # 当前目录的上一级目录，即robot目录
                os.environ['TEST_ROOT'] = os.path.dirname(os.path.dirname(__file__))

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
        rc = run_robot(robotOptions, exit=False)
        logger.info("Finished test [" + robotFile + "]. ret=[" + str(rc) + "]")

        # 根据XML文件生成一个测试数据的汇总JSON信息
        xmlResultFile = os.path.abspath(os.path.join(workingDirectory, os.path.basename(workingDirectory) + ".xml"),)
        if not os.path.exists(xmlResultFile):
            raise RegressException("Result file [" + str(xmlResultFile) + "] is missed. " +
                                   "Probably robot run with fatal error.")
        else:
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
