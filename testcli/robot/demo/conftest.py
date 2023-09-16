# -*- coding: utf-8 -*-
import copy
import json
import time
import os
import pytest
from py.xml import html

# 记录测试的运行结果
scenarioResults = {}


@pytest.mark.optionalhook
def pytest_html_results_table_header(cells):
    # cells.insert(2, html.th('Description'))
    cells.insert(1, html.th('Time', class_='sortable time', col='time'))
    cells.pop()


@pytest.mark.optionalhook
def pytest_html_results_table_row(report, cells):
    if report:
        pass
    cells.insert(1, html.td(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), class_='col-time'))
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
    if session:
        pass
    if "T_WORK" in os.environ:
        testName = os.path.basename(os.environ["T_WORK"])
        scenarioResultFile = \
            os.path.join(os.environ["T_WORK"], testName + ".pytestlog")
    else:
        scenarioResultFile = "scenarioResult.xlog"

    if "T_TEST_JOBID" in os.environ:
        jobId = int(os.environ["T_TEST_JOBID"])
    else:
        jobId = 0
    if "T_TEST_SQLID" in os.environ:
        sqlId = int(os.environ["T_TEST_SQLID"])
    else:
        sqlId = 0
    if "T_TEST_ROBOTID" in os.environ:
        robotId = int(os.environ["T_TEST_ROBOTID"])
    else:
        robotId = 0
    scenarioResults["summary"] = {
        "jobId": jobId,
        "sqlId": sqlId,
        "robotId": robotId
    }
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
