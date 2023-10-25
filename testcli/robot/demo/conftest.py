# -*- coding: utf-8 -*-
import copy
import json
import time
import os
import re
import pytest

# 记录测试的运行结果
scenarioResults = {
    "summary": {
        "caseId": "0",
        "suiteId": "0"
    }
}


@pytest.mark.optionalhook
def pytest_html_results_table_header(cells):
    # cells.insert(2, html.th('Description'))
    cells.insert(1, '<th class="sortable time" col="time">Time</th>')
    cells.pop()


@pytest.mark.optionalhook
def pytest_html_results_table_row(report, cells):
    if report:
        pass
    cells.insert(1, '<td class="col-time">' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '</td>')
    # cells.insert(2, html.td(report.description))
    cells.pop()


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    global scenarioResults

    if call:
        pass

    # 获取钩子方法的调用结果，返回一个result对象
    out = yield

    # 从钩子方法的调用结果中获取测试报告
    report = out.get_result()
    report.description = str(item.function.__doc__)
    report.nodeid = report.nodeid.encode("utf-8").decode("unicode_escape")  # 设置编码显示中文

    # 获取测试的唯一标识
    nodeId = str(report.nodeid)
    suiteName = os.path.basename(nodeId.split("::")[0]).rstrip(".py")
    className = nodeId.split("::")[1]
    caseName = nodeId.split("::")[-1]
    scenarioResult = {}
    if nodeId in scenarioResults.keys():
        scenarioResult = scenarioResults[nodeId]
    when = report.when

    if when == "setup":
        # 记录开始时间
        scenarioResult["startTime"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

        # 记录caseId，suiteId等信息
        pythonFileName = os.path.abspath(
            os.path.join(os.path.dirname(__file__), os.path.basename(nodeId.split("::")[0]))
        )
        with open(file=pythonFileName, mode="r", encoding="utf-8") as fp:
            pythonLines = fp.readlines()
        metadata = {}
        for pythonLine in pythonLines:
            pythonLine = str(pythonLine).strip()
            matchObj = re.match(r"^#(\s+)?MetaData(\s+)?(.*)\s+(.*)$", pythonLine, re.IGNORECASE)
            if matchObj:
                metaKey = matchObj.group(3).strip()
                metaValue = matchObj.group(4).strip()
                metadata.update(
                    {
                        metaKey: metaValue
                    }
                )
        if "suiteId" in metadata.keys():
            suiteId = metadata["suiteId"]
        else:
            suiteId = 0
        if "caseId" in metadata.keys():
            caseId = metadata["caseId"]
        else:
            caseId = 0
        scenarioResults["summary"] = {
            "caseId": str(caseId),
            "suiteId": str(suiteId)
        }

    if when == "teardown":
        # 记录结束时间
        scenarioResult["endTime"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

    if report.when == "call":
        scenarioResult["suiteName"] = str(suiteName)
        scenarioResult["className"] = str(className)
        scenarioResult["caseName"] = str(caseName)
        scenarioResult["scenarioId"] = caseName.split("_")[-1]
        scenarioResult["result"] = str(report.outcome)
    scenarioResults[nodeId] = copy.copy(scenarioResult)


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session):
    global scenarioResults

    if session:
        pass

    if "T_WORK" in os.environ:
        testName = os.path.basename(os.environ["T_WORK"])
        scenarioResultFile = \
            os.path.join(os.environ["T_WORK"], testName + ".pytestlog")
    else:
        scenarioResultFile = "scenarioResult.xlog"
    fp = open(file=scenarioResultFile, mode='w', encoding='UTF-8')
    fp.write(
        json.dumps(
            obj=scenarioResults,
            sort_keys=True,
            indent=4,
            ensure_ascii=False,
        )
    )
    fp.close()
