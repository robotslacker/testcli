# -*- coding: utf-8 -*-
import os
import sys
import time
import shutil
import click
import platform
import signal
import logging
import coloredlogs
import multiprocessing
from multiprocessing import Manager
from .robot.common.runregress import Regress, RegressException


# 信号处理程序
def abortSignalHandler(signum, frame):
    click.secho("Got signal [" + str(signum) + "]. Quit application.", err=True, fg="red")
    if frame:
        pass
    # 直接退出
    sys.exit(255)


# 运行回归测试应用
def runRegress(args, executorMonitor):
    # 初始化进程日志
    LOG_FORMAT = "%(asctime)s - %(levelname)9s - %(message)s"
    logFormat = logging.Formatter(LOG_FORMAT)
    fileLogHandler = logging.FileHandler(
        filename=os.path.join(
            os.environ["T_WORK"], "runRegress.log"),
        mode="a",
        encoding="UTF-8")
    fileLogHandler.setFormatter(logFormat)
    logger = logging.getLogger("runRegrss")
    logger.setLevel(logging.INFO)
    logger.addHandler(fileLogHandler)

    # 正式开始运行Case
    regressHandler = Regress(
        maxProcess=args["maxProcess"],
        scriptTimeout=args["scriptTimeout"],
        workerTimeout=args["workerTimeout"],
        logger=logger,
        jobList=args["jobList"],
        executorMonitor=executorMonitor
    )
    executorMonitor["pid"] = os.getpid()
    executorMonitor["maxProcess"] = args["maxProcess"]
    executorMonitor["scriptTimeout"] = args["scriptTimeout"]
    executorMonitor["workerTimeout"] = args["workerTimeout"]
    executorMonitor["jobList"] = args["jobList"]
    executorMonitor["started"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    executorMonitor["end"] = ""
    executorMonitor["running"] = True

    exitCode = 0
    try:
        logger.info("Regress start ...")
        regressHandler.run()
        logger.info("Regress end.")
    except RegressException as re:
        logger.error("Regress failed. " + repr(re) + "\n" +
                     "Please check logfile under [" + os.path.abspath(os.environ["T_WORK"]) + "]")
        exitCode = 1
        executorMonitor["end"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        executorMonitor["running"] = False
    if exitCode != 0:
        # 如果已经失败，没有必要继续统计报表
        sys.exit(exitCode)

    try:
        logger.info("Generating report ...")
        regressHandler.generateTestReport()
        logger.info("Finished. Please read report from [" +
                    os.path.abspath(os.path.join(os.environ["T_WORK"], "report", "report.html")) + "]")
        executorMonitor["end"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        executorMonitor["running"] = False
    except RegressException as re:
        logger.exception(re)
        logger.error("Report failed. " + repr(re) + "\n" +
                     "Please check logfile under [" +
                     os.path.abspath(os.path.join(os.environ["T_WORK"], "report")) + "]")
        exitCode = 1
    executorMonitor["end"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    executorMonitor["running"] = False
    sys.exit(exitCode)


@click.command()
@click.option("--job", type=str, required=True, help="Specify robot job file or directory.",)
@click.option("--work", type=str, required=True,
              help="Specify the work directory(ALL FILES IN THIS DIRECTORY WILL BE CLEANED).",)
@click.option("--parallel", type=int, default=1,
              help="Specify the parallelism of the jobs, default is 1, means no parallel.")
@click.option("--jobtimeout", type=int, default=-1,
              help="Specify the timeout limit of whole jobs, Default is -1, means no limit.")
@click.option("--workertimeout", type=int, default=-1,
              help="Specify the timeout limit of one job, Default is -1, means no limit.")
@click.option("--force", is_flag=True,
              help="Overwrite old job working directory even it has test data.")
def cli(
        job,
        work,
        parallel,
        jobtimeout,
        workertimeout,
        force
):
    # 初始化信号变量
    # 捕捉信号，处理服务中断的情况
    if platform.system().upper() in ["LINUX", "DARWIN"]:
        # 通信管道中断，不处理中断信息，放弃后续数据
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
        # 被操作系统KILL
        signal.signal(signal.SIGTERM, abortSignalHandler)

    # 初始化进程日志
    os.environ["COLOREDLOGS_LEVEL_STYLES"] = \
        "spam=22;debug=28;verbose=34;notice=220;warning=202;success=118,bold;" \
        "error=background=red,bold;critical=background=red"
    LOG_FORMAT = "%(asctime)s - %(name)15s-[%(process)8d] - %(levelname)9s - %(message)s"
    fFormat = logging.Formatter(LOG_FORMAT)
    consoleLogHandler = logging.StreamHandler()
    consoleLogHandler.setFormatter(fFormat)
    consoleLogHandler.setLevel(logging.INFO)
    logger = logging.getLogger("clirobot")
    coloredlogs.install(
        level=consoleLogHandler.level,
        fmt=LOG_FORMAT,
        logger=logger,
        isatty=True
    )

    # 设置程序运行的目录
    if not os.path.isdir(work):
        logger.error("Work directory [" + os.path.abspath(work) + "] does not exist or invalid.")
        sys.exit(255)
    else:
        os.environ["T_WORK"] = os.path.abspath(work)
        workDirectory = os.environ["T_WORK"]

    # 清空所有T_WORK下的内容
    logger.info("WILL CLEAN ALL FILES UNDER DIRECTORY [" + workDirectory + "] !!!")
    if os.path.exists(workDirectory):
        files = os.listdir(workDirectory)
        if len(files) != 0 and not force:
            logger.error("Work directory [" + workDirectory + "] is NOT EMPTY! ")
            sys.exit(255)
        for file in files:
            filePath = os.path.join(workDirectory, file)
            if os.path.isdir(filePath):
                shutil.rmtree(path=filePath, ignore_errors=True)
            else:
                os.remove(filePath)

    # 设置Robot的引导文件位置
    os.environ["TEST_ROOT"] = os.path.join(os.path.dirname(__file__), "robot")

    # 设置需要执行的文件任务或者任务目录
    # 1. 可以为一个目录，该目录下所有robot文件（包括子目录）都会被运行
    # 2. 可以为一个文件，该文件将会被运行
    # 3. 可以为多个文件或者多个目录，中间用逗号隔开
    os.environ["JOB_LIST"] = job

    # 任务会放在子进程中完成，而不会在主进程中完成
    processManagerContext = multiprocessing.get_context("spawn")
    executorMonitor = Manager().dict()
    args = {
        "maxProcess": parallel,
        "scriptTimeout": jobtimeout,
        "workerTimeout": workertimeout,
        "jobList": os.environ["JOB_LIST"]
    }

    # 运行回归测试
    process = processManagerContext.Process(
        target=runRegress,
        args=(args, executorMonitor)
    )
    logger.info("Regress process started ...")
    logger.info("Regress log will be rediected to [%s] ...",
                os.path.abspath(os.path.join(os.environ["T_WORK"], "runRegress.log")))
    process.start()

    # 循环等待进行运行结束
    while True:
        if process.is_alive():
            if "taskCount" in executorMonitor.keys():
                logger.info("Running ... Total [%s/%s] tasks finished. Total [%s/%s] runlevels finished. " %
                            (
                                executorMonitor["taskCount"] - executorMonitor["taskLeft"],
                                executorMonitor["taskCount"],
                                executorMonitor["runLevelCount"] - executorMonitor["runLevelLeft"],
                                executorMonitor["runLevelCount"],
                            ))
                for runningJobName, runningJobInfo in dict(executorMonitor["runningJobs"]).items():
                    logger.info("--- " +
                                runningJobName + ":" +
                                runningJobInfo["workingDirectory"] +
                                "(" + runningJobInfo["script"] + ") started at " + runningJobInfo["started"] + ".")
                time.sleep(10)
            else:
                logger.info("Waiting for runExecutor join ...")
                time.sleep(3)
        else:
            exitCode = process.exitcode
            break

    # 打印测试报告
    logger.info("============================= Test Report ==========================")
    if "testReport" in executorMonitor.keys():
        testReport = executorMonitor["testReport"]
        for testSuite in testReport:
            if testSuite["errorCount"] != 0:
                logger.error(
                    "Suite: [%s]. %d/%d/%d (Error/Fail/Pass)" %
                    (testSuite["suiteName"],
                     testSuite["errorCount"], testSuite["failedCount"], testSuite["passedCount"],)
                )
            elif testSuite["failedCount"] != 0:
                logger.warning(
                    "Suite: [%s]. %d/%d/%d (Error/Fail/Pass)" %
                    (testSuite["suiteName"],
                     testSuite["errorCount"], testSuite["failedCount"], testSuite["passedCount"],)
                )
            else:
                logger.info(
                    "Suite: [%s]. %d/%d/%d (Error/Fail/Pass)" %
                    (testSuite["suiteName"],
                     testSuite["errorCount"], testSuite["failedCount"], testSuite["passedCount"],)
                )
            for testcase in testSuite["cases"]:
                if testcase["caseStatus"] == "ERROR":
                    logger.error(
                        "    Case: [%s]. %s" % (testcase["caseName"], testcase["caseStatus"])
                    )
                elif testcase["caseStatus"] == "FAILURE":
                    logger.warning(
                        "    Case: [%s]. %s" % (testcase["caseName"], testcase["caseStatus"])
                    )
                else:
                    logger.info(
                        "    Case: [%s]. %s" % (testcase["caseName"], testcase["caseStatus"])
                    )
            logger.info("--------------------------------------------------------------------")
    logger.info("============================= Test Report ==========================")

    if exitCode == 0:
        logger.info("Job finished.")
    else:
        logger.error("Job failed with exitcode [%d]. " % exitCode)

    # 显示HTML文件的位置
    htmlReportFile = os.path.abspath(os.path.join(os.environ["T_WORK"], "report", "report.html"))
    if os.path.exists(htmlReportFile):
        logger.info("Finished. Please read report from [%s]." % htmlReportFile)
    else:
        logger.info("Finished. Please read log uner [%s]." % os.environ["T_WORK"])
    sys.exit(exitCode)


if __name__ == '__main__':
    cli()
