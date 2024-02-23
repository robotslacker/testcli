# -*- coding: utf-8 -*-
import os
import sys
import time
import stat
import shutil
import click
import platform
import signal
import logging
import coloredlogs
import multiprocessing
import traceback
from time import strftime, localtime
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
# args               程序参数
# executorMonitor    运行信息监控，字典结构
def runRegress(args, executorMonitor=None):
    # 初始化进程日志
    LOG_FORMAT = "%(asctime)s - %(levelname)9s - %(message)s"
    logFormat = logging.Formatter(LOG_FORMAT)
    fileLogHandler = logging.FileHandler(
        filename=os.path.join(args["workDirectory"], "runRegress.log"), mode="a", encoding="UTF-8"
    )
    fileLogHandler.setFormatter(logFormat)
    logger = logging.getLogger("runRegrss")
    logger.setLevel(logging.INFO)
    logger.addHandler(fileLogHandler)

    # 如果环境变量中有ROBOTOPTIONS，则会利用这个参数
    if "ROBOTOPTIONS" in os.environ:
        robotOptions = os.environ["ROBOTOPTIONS"]
    else:
        robotOptions = None

    # 初始化运行监控进程
    if executorMonitor is None:
        executorMonitor = dict()

    # 正式开始运行Case
    regressHandler = Regress(
        jobList=args["jobList"],
        testRoot=args["testRoot"],
        workDirectory=args["workDirectory"],
        maxProcess=args["maxProcess"],
        robotOptions=robotOptions,
        scriptTimeout=args["scriptTimeout"],
        workerTimeout=args["workerTimeout"],
        logger=logger,
        executorMonitor=executorMonitor,
        testRunId=args["testRunId"],
        testResultDb=args["testResultDb"],
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
                     "Please check logfile under [" + args["workDirectory"] + "]")
        exitCode = 1
        executorMonitor["end"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        executorMonitor["running"] = False
    if exitCode != 0:
        # 如果已经失败，没有必要继续统计报表
        return exitCode

    try:
        logger.info("Generating report ...")
        regressHandler.generateTestReport()
        logger.info("Finished. Generating report Done.")
        executorMonitor["end"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        executorMonitor["running"] = False
    except RegressException as re:
        logger.exception(re)
        logger.error("Report failed. " + repr(re) + "\n" +
                     "Please check logfile under [" +
                     os.path.abspath(os.path.join(args["workDirectory"], "report")) + "]")
        exitCode = 1
    executorMonitor["end"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    executorMonitor["running"] = False
    return exitCode


@click.command()
@click.option("--job", type=str, required=False, multiple=True,
              help="Specify robot job file or directory. Separated by commas, if multiple files are included.",)
@click.option("--jobgroup", type=str, required=False, multiple=True,
              help="Specify robot job list file. Each line represents one job.",)
@click.option("--work", type=str, required=True,
              help="Specify the work directory(ALL FILES IN THIS DIRECTORY WILL BE CLEANED).",)
@click.option("--parallel", type=int, default=1,
              help="Specify the parallelism of the job, default is 1, means no parallel.")
@click.option("--jobtimeout", type=int, default=-1,
              help="Specify the timeout limit(seconds) of the job, Default is -1, means no limit.")
@click.option("--workertimeout", type=int, default=-1,
              help="Specify the timeout limit(seconds) of one suite, Default is -1, means no limit.")
@click.option("--force", is_flag=True,
              help="Clean all files under working directory if not empty.")
@click.option("--runid", type=str,
              help="Test run unique id. Default is timestamp+host+pid. will save in extend log for later analyze.")
@click.option("--resultdb", type=str,
              help="Will save test result into database for later analyze.")
def cli(
        job,
        jobgroup,
        work,
        parallel,
        jobtimeout,
        workertimeout,
        force,
        runid,
        resultdb
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

    # 默认的RunId为 时间戳+主机名+PID
    if runid is None:
        runid = strftime("%Y-%m-%d %H:%M:%S", localtime()) + "-" + str(platform.node()) + "-" + str(os.getpid())

    # 整理任务列表，把Job和JobGroup的内容都添加到一起
    jobList = []
    if job is not None:
        for jobItem in job:
            jobList.extend(str(jobItem).split(','))
    if jobgroup is not None:
        for jobgroupItem in jobgroup:
            if not os.path.isfile(jobgroupItem):
                logger.error("Job failed. job group [" + str(jobgroupItem) + "] must be a valid text file.")
                sys.exit(255)
            with open(file=jobgroupItem, mode="r", encoding="utf-8") as fp:
                jobList.extend(fp.readlines())
    # 去掉其中无效的空格信息, 去除重复的数据
    jobList = [s.strip() for s in jobList if s is not None and s.strip() != ""]
    jobList = list(set(jobList))

    # JOB和jobGroup参数至少定义一个
    if len(jobList) == 0:
        logger.error("Job failed. Please define at least one job.")
        sys.exit(255)
    logger.info("Total [" + str(len(jobList)) + "] jobs accepted.")

    # 设置程序运行的目录
    if not os.path.isdir(work):
        logger.error("Work directory [" + os.path.abspath(work) + "] does not exist or invalid.")
        sys.exit(255)
    else:
        workDirectory = os.path.abspath(work)

    # 清空所有T_WORK下的内容
    logger.info("WILL CLEAN ALL FILES UNDER DIRECTORY [" + workDirectory + "] !!!")
    if os.path.exists(workDirectory):
        try:
            files = os.listdir(workDirectory)
            if len(files) != 0 and not force:
                logger.error("Work directory [" + workDirectory + "] is NOT EMPTY! ")
                sys.exit(255)
            for file in files:
                filePath = os.path.join(workDirectory, file)
                if os.path.isdir(filePath):
                    if platform.system().upper() in ["LINUX", "DARWIN"]:
                        shutil.rmtree(filePath)
                    else:
                        # 删除只读文件，解决Windows的PermissionError问题
                        def on_rm_error(func, path, _):
                            os.chmod(path, stat.S_IWRITE)
                            func(path)
                        shutil.rmtree(path=filePath, onerror=on_rm_error)
                else:
                    os.remove(filePath)
        except Exception as ex:
            if "TESTCLI_DEBUG" in os.environ:
                print('traceback.print_exc():\n%s' % traceback.print_exc())
                print('traceback.format_exc():\n%s' % traceback.format_exc())
            click.secho(repr(ex), err=True, fg="red")
            sys.exit(255)

    # 设置需要执行的文件任务或者任务目录
    # 1. 可以为一个目录，该目录下所有robot文件（包括子目录）都会被运行
    # 2. 可以为一个文件，该文件将会被运行
    # 3. 可以为多个文件或者多个目录，中间用逗号隔开

    # 任务会放在子进程中完成，而不会在主进程中完成
    # 这样做的目的是便于后续显示作业的完成情况
    processManagerContext = multiprocessing.get_context("spawn")
    executorMonitor = Manager().dict()
    args = {
        "maxProcess": parallel,
        "scriptTimeout": jobtimeout,
        "workerTimeout": workertimeout,
        "testRoot": os.path.join(os.path.dirname(__file__), "robot"),
        "workDirectory": workDirectory,
        "jobList": jobList,
        "testRunId": runid,
        "testResultDb": resultdb
    }

    # 运行回归测试
    process = processManagerContext.Process(
        target=runRegress,
        args=(args, executorMonitor)
    )
    logger.info("Regress process started ...")
    logger.info("Regress log will forward to [%s] ...",
                os.path.abspath(os.path.join(workDirectory, "runRegress.log")))
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
                                "(" + runningJobInfo["script"] + ") started at " +
                                runningJobInfo["started"] + ".")
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
    htmlReportFile = os.path.abspath(os.path.join(workDirectory, "report", "report.html"))
    if os.path.exists(htmlReportFile):
        logger.info("Finished. Please read report from [%s]." % htmlReportFile)
    else:
        logger.info("Finished. Please read log uner [%s]." % workDirectory)
  
    sys.exit(exitCode)


if __name__ == '__main__':
    cli()
