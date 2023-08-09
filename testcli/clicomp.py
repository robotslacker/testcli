# -*- coding: utf-8 -*-
import os
import sys
import click
import platform
import signal

from testcli.htmldiff.diffhtmlgenerate import diffHtmlGenerate
from .commands.compare import POSIXCompare
from .sqlparse import SQLAnalyze


# 信号处理程序
def abortSignalHandler(signum, frame):
    click.secho("Got signal [" + str(signum) + "]. Quit application.", err=True, fg="red")
    if frame:
        pass
    # 直接退出
    sys.exit(255)


@click.command()
@click.option("--reference", type=str, required=True, help="Specify the log file for reference.",)
@click.option("--logfile", type=str, required=True, help="Specify the log file for comparison.",)
@click.option("--rule", type=str, help="Compare rule file.")
@click.option("--output", type=str, default="CONSOLE", help="Specify the result file location. default is console.")
@click.option("--outputformat", type=str, default="TXT", help="Specify the result output file format TXT|HTML|CONSOLE.")
def cli(
        reference,
        logfile,
        rule,
        output,
        outputformat
):
    # 捕捉信号，处理服务中断的情况
    if platform.system().upper() in ["LINUX", "DARWIN"]:
        # 通信管道中断，不处理中断信息，放弃后续数据
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
        # 被操作系统KILL
        signal.signal(signal.SIGTERM, abortSignalHandler)

    # 校验报告输出格式
    outputformat = str(outputformat).strip().upper()
    if outputformat not in ["TXT", "HTML"]:
        click.secho(
            "Compare tool only support TXT(text mode) or HTML(html mode).",
            err=True,
            fg="red"
        )
        sys.exit(255)

    # 解析比较配置文件
    optionCompareIgnoreCase = False        # 是否忽略大小写
    optionCompareWithMask = True           # 是否在比较中使用正则
    optionIgnoreEmptyLine = False          # 是否忽略空行
    optionIgnoreTailOrHeadBlank = False    # 是否忽略首尾空格
    optionCompareAlgorithm = "MYERS"       # 默认的比较算法
    optionSkipLines = []                   # 需要忽略的比对信息
    optionMaskLines = {}                   # 需要掩码的比对信息

    ruleList = []
    if rule is not None:
        if not os.path.exists(rule):
            click.secho("Invalid compare rule file, file [" + str(rule) + "] does not exist!", err=True, fg="red")
            sys.exit(255)
        with open(file=rule, mode="r", encoding="UTF-8") as fp:
            ruleList = fp.readlines()
    lineno = 1
    for compareRule in ruleList:
        compareRule = str(compareRule).strip()
        if not compareRule.upper().startswith("_COMPARE "):
            compareRule = "_COMPARE " + compareRule
        (isFinished, ret_CommandSplitResult, ret_errorCode, ret_errorMsg) = SQLAnalyze(compareRule)
        if ret_errorCode != 0:
            click.secho("Invalid compare rule config in [" + str(rule) + ":" + str(lineno) + "], " + str(ret_errorMsg),
                        err=True,
                        fg="red"
                        )
            sys.exit(255)
        lineno = lineno + 1
        requestObject = ret_CommandSplitResult
        if requestObject["action"] == "set":
            for optionName, optionValue in requestObject["compareOptions"].items():
                if str(optionName) == "case":
                    if optionValue:
                        optionCompareIgnoreCase = False
                    else:
                        optionCompareIgnoreCase = True
                if str(optionName) == "mask":
                    if optionValue:
                        optionCompareWithMask = True
                    else:
                        optionCompareWithMask = False
                if str(optionName) == "igblank":
                    if optionValue:
                        optionIgnoreEmptyLine = True
                    else:
                        optionIgnoreEmptyLine = False
                if str(optionName) == "trim":
                    if optionValue:
                        optionIgnoreTailOrHeadBlank = True
                    else:
                        optionIgnoreTailOrHeadBlank = False
                if str(optionName) == "algorithm":
                    if optionValue == "lcs":
                        optionCompareAlgorithm = "LCS"
                    if optionValue == "myers":
                        optionCompareAlgorithm = "MYERS"
        if requestObject["action"] == "skip":
            optionSkipLines.append(requestObject["source"])
        if requestObject["action"] == "mask":
            optionMaskLines.update(
                {
                    requestObject["source"]: requestObject["target"]
                }
            )

    # 检查各种目录参数
    if logfile is None or not os.path.exists(logfile):
        click.secho("Compare logfile [" + str(logfile) + "] does not exist. ", err=True, fg="red")
        sys.exit(255)
    if reference is None or not os.path.exists(reference):
        click.secho("Compare reference [" + str(reference) + "] does not exist. ", err=True, fg="red")
        sys.exit(255)
    # 如果指定输出到控制台，则不再判断output的目录
    if not str(output).strip().upper() == "CONSOLE":
        if not os.path.isdir(output):
            click.secho(
                "Output must be valid directory [" + str(reference) + "] to generate dif/suc file. ",
                err=True,
                fg="red"
            )
            sys.exit(255)

    # 进行文件比对
    compareHandler = POSIXCompare()
    logFile = os.path.abspath(logfile)
    refFile = os.path.abspath(reference)
    compareResult, compareReport = \
        compareHandler.compare_text_files(
            file1=logFile,
            file2=refFile,
            skipLines=optionSkipLines,
            maskLines=optionMaskLines,
            ignoreEmptyLine=optionIgnoreEmptyLine,
            CompareWithMask=optionCompareWithMask,
            CompareIgnoreCase=optionCompareIgnoreCase,
            CompareIgnoreTailOrHeadBlank=optionIgnoreTailOrHeadBlank,
            compareAlgorithm=optionCompareAlgorithm,
            CompareWorkEncoding='UTF-8',
            CompareRefEncoding='UTF-8'
        )
    if not compareResult:
        if not str(output).strip().upper() == "CONSOLE":
            suffix = os.path.splitext(logFile)[-1]
            if outputformat == "TXT":
                diffFile = os.path.join(
                    output,
                    os.path.basename(logFile)[0:-1*len(suffix)] + ".dif"
                )
                with open(file=diffFile, mode="w") as fp:
                    for line in compareReport:
                        fp.write(line + "\n")
                fp.close()
                print("Compare failed. "
                      "Please check diff file [" + os.path.abspath(diffFile) + "] to get detail information.")
            elif outputformat == "HTML":
                htmlDiffFile = os.path.join(
                    output,
                    os.path.basename(logFile)[0:-1 * len(suffix)] + ".html"
                )
                diffhtmlGenerate = diffHtmlGenerate()
                htmlResult = diffhtmlGenerate.generateHtmlFromDif(
                    workFile=logFile,
                    refFile=refFile,
                    diffLines=compareReport
                )
                fp = open(file=htmlDiffFile, mode="w", encoding="UTF-8")
                for line in htmlResult:
                    fp.write(line + "\n")
                fp.close()
                print("Compare failed. "
                      "Please read diff html report [" + os.path.abspath(htmlDiffFile) + "] to get detail information.")
        else:
            for line in compareReport:
                if line.startswith("-") or line.startswith("+"):
                    print(line)
            print("Compare failed.")
        sys.exit(1)
    else:
        if not str(output).strip().upper() == "CONSOLE":
            suffix = os.path.splitext(logFile)[-1]
            succFile = os.path.join(
                output,
                os.path.basename(logFile)[0:-1*len(suffix)] + ".suc"
            )
            with open(file=succFile, mode="w"):
                pass
        print("Compare successful.")
        sys.exit(0)


# 主程序
if __name__ == "__main__":
    cli()
