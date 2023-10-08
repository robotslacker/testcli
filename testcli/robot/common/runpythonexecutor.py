# -*- coding: utf-8 -*-
import os
import sys
import logging
import pytest
from .regressexception import RegressException


def runPythonExecutor(args):
    # 禁止掉一些不必要显示的log信息
    logging.getLogger('hdfs.client').setLevel(level=logging.ERROR)
    logging.getLogger('urllib3.connectionpool').setLevel(level=logging.ERROR)
    logging.getLogger("paramiko").setLevel(level=logging.ERROR)
    logger = logging.getLogger("runPythonExecutor")

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

        # 初始化进程日志
        LOG_FORMAT = "%(asctime)s - %(levelname)9s - %(message)s"
        logFormat = logging.Formatter(LOG_FORMAT)
        fileLogHandler = logging.FileHandler(
            filename=os.path.join(workingDirectory, "runPythonExecutor.log"),
            mode="a",
            encoding="UTF-8")
        fileLogHandler.setFormatter(logFormat)
        logger.setLevel(logging.INFO)
        logger.addHandler(fileLogHandler)

        # 需要运行的Robot文件
        pythonFile = args["pythonFile"]
        testName = os.path.basename(pythonFile)[:-len(".py")]

        # 开始运行测试
        logger.info("Begin to execute [" + pythonFile + "] ...")

        # 检查文件路径是否存在
        if not os.path.exists(pythonFile):
            raise RegressException("Python File [" + pythonFile + "] does not exist! task failed.")

        # 建立报告的目录
        htmlReportFile = os.path.join(workingDirectory, os.path.basename(workingDirectory) + ".html")
        junitReportFile = os.path.join(workingDirectory, os.path.basename(workingDirectory) + ".junit")

        # 切换标准输入输出
        stdoutFile = open(os.path.join(workingDirectory, testName + ".stdout"), 'w')
        stderrFile = open(os.path.join(workingDirectory, testName + ".stderr"), 'w')
        sys.__stdout__ = stdoutFile
        sys.__stderr__ = stderrFile
        sys.stdout = stdoutFile
        sys.stderr = stderrFile

        # 记录当前的文件目录位置，切换工作目录到robot文件所在的目录
        os.chdir(os.path.dirname(pythonFile))

        # 重置T_WORK到子目录下
        os.environ['T_WORK'] = workingDirectory

        # 处理Python的测试源目录
        if "TEST_ROOT" not in os.environ:
            if args["testRoot"] is not None:
                # 如果参数提供了testRoot，以参数为准
                os.environ['TEST_ROOT'] = args["testRoot"]
            else:
                # 如果参数没有提供，以TEST_ROOT环境变量为准, 否则以当前目录的上一级目录为准
                os.environ['TEST_ROOT'] = os.path.dirname(os.path.dirname(__file__))
        logger.info("TEST_ROOT [" + os.environ['TEST_ROOT'] + "]")
        if os.environ['TEST_ROOT'] not in sys.path:
            sys.path.append(os.environ['TEST_ROOT'])
        logger.info("Python PATH:")
        for path in sys.path:
            logger.info("  " + str(path))

        # 运行pytest脚本
        pytest.main(
            args=[
                "-vs",
                "--capture=sys",
                "--html=" + htmlReportFile,
                "--junitxml=" + junitReportFile,
                pythonFile,
            ],
        )
        logger.info("End execute [" + pythonFile + "].")
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
