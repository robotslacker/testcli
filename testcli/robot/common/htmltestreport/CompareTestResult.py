# -*- coding: utf-8 -*-
import os
import shutil
from xml.sax import saxutils

__version__ = "0.0.1"


# ----------------------------------------------------------------------
# Template
class CompareTestResultTemplate(object):
    STATUS = {
        0: u'通过',
        1: u'失败',
        2: u'错误',
    }

    DEFAULT_TITLE = '测试报告'
    DEFAULT_DESCRIPTION = '无详细信息'

    # ------------------------------------------------------------------------
    # HTML Template

    HTML_TMPL = r"""
<!DOCTYPE html>
<html lang="zh">
<head>
    <title>Unit Test Report</title>
    <meta name="generator" content="HTMLTestRunner 0.0.1"/>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>

    <link href="css/bootstrap.min.css" rel="stylesheet">
    <script type="text/javascript" src="js/jquery.min.js"></script>
    <script type="text/javascript" src="js/bootstrap.min.js"></script>
    <script type="text/javascript" src="js/echarts.min.js"></script>

    %(stylesheet)s
</head>

<body>
    <script type="text/javascript">
    </script>
    <div id="div_base">
        %(heading)s
        %(report)s
        %(ending)s
    </div>
</body>
</html>
"""

    STYLESHEET_TMPL = r"""
    <style media="screen">
        body        { font-family: Microsoft YaHei,Consolas,arial,sans-serif; font-size: 80%; }
        table       { font-size: 100%; }
        pre         { white-space: pre-wrap;word-wrap: break-word; }

        /* -- heading ---------------------------------------------------------------------- */
        h1 {
            font-size: 16pt;
            color: gray;
        }

        .tableTitle {
            font-size: 12pt;
            color: black;
        }
        .attribute {
            margin-top: 1ex;
            margin-bottom: 0;
        }

        .description {
            margin-top: 2ex;
            margin-bottom: 3ex;
        }

        .resultTable {
            width: 99%;
        }
        #header_row {
            font-weight: bold;
            color: #303641;
            background-color: #ebebeb;
        }
        #total_row  { font-weight: bold; }
        .passClass  { background-color: LightGreen; }
        .failClass  { background-color: Orange; }
        .deprecatedClass  { background-color: Orange; }
        .hiddenRow  { display: none; }

        #ending {
        }

        #div_base {
                    position:absolute;
                    top:0;
                    left:5%;
                    right:5%;
                    width: auto;
                    height: auto;
                    margin: -15px 0 0 0;
        }
    </style>
    """

    HEADING_TMPL = r"""
    <div class='page-header'>
        <h1>%(title)s</h1>
        %(parameters)s
        <p></p>
    </div>
    <p></p>
    """

    HEADING_ATTRIBUTE_TMPL = """<p class='attribute'><strong>%(name)s:</strong> %(value)s</p>"""

    REPORT_TMPL = u"""
        <p class='tableTitle'>
            <strong>汇总信息：</strong><br>
        </p>
        <table id='summary_table' class="resultTable table table-bordered">
            <colgroup>
                <col style = "text-align: left;"/>
                <col style = "text-align: right;"/>
                <col style = "text-align: right;"/>
                <col style = "text-align: right;"/>
                <col style = "text-align: right;"/>
                <col style = "text-align: right;"/>
                <col style = "text-align: right;"/>
                <col style = "text-align: right;"/>
            </colgroup>
            <tr id='header_row'>
                <td style = "text-align: center;">测试组件</td>
                <td style = "text-align: center;">成功率</td>
                <td style = "text-align: center;">失败数量</td>
                <td style = "text-align: center;">成功数量</td>
                <td style = "text-align: center;">新失败的用例数量</td>
                <td style = "text-align: center;">新成功的用例数量</td>
                <td style = "text-align: center;">被废弃的用例数量</td>
                <td style = "text-align: center;">长期未解决的用例数量</td>
            </tr>
            %(componentSummaryList)s
            <tr id='total_row'>
                <td>总计</td>
                <td>1</td>
                <td>0</td>
                <td>1</td>
                <td>0</td>
                <td>--------</td>
                <td>2021-12-09 14:57:34</td>
                <td>00:00:03</td>
            </tr>
            <p></p>
        </table>
        %(componentDetailList)s
    """

    COMPONENTSUMMARYLIST_TMPL = r"""
        <tr class='%(cssClass)s'>
            <td>%(componentName)s</td>
            <td>%(succRate)s</td>
            <td>%(failCount)s</td>
            <td>%(succCount)s</td>
            <td>%(newFailCount)s</td>
            <td>%(newSuccCount)s</td>
            <td>%(deprecatedCount)s</td>
            <td>%(longFailureCount)s</td>
        </tr>
    """

    COMPONENTDETAILLIST_TMPL = r"""
        <div>
            <p class='tableTitle'>
                <strong>组件名称：</strong><br>
            </p>
            <p class='attribute'>
                <strong>新的失败</strong><br>
            </p>
            <p></p>
            <table class="resultTable table table-bordered">
                <colgroup>
                    <col style = "text-align: left;"/>
                    <col style = "text-align: left;"/>
                    <col style = "text-align: left;"/>
                    <col style = "text-align: left;"/>
                </colgroup>
                <tr>
                    <td style = "text-align: center;">测试套件名称</td>
                    <td style = "text-align: center;">测试用例名称</td>
                    <td style = "text-align: center;">测试场景名称</td>
                    <td style = "text-align: center;">错误信息</td>
                </tr>
                %(componentDetailNewFail)s
                <tr>
                    <td>总计</td>
                    <td>1</td>
                    <td>0</td>
                    <td>1</td>
                </tr>
            </table>
    
            <p class='attribute'>
                <strong>新的成功</strong><br>
            </p>
            <p></p>
            <table class="resultTable table table-bordered">
                <colgroup>
                    <col style = "text-align: left;"/>
                    <col style = "text-align: left;"/>
                    <col style = "text-align: left;"/>
                    <col style = "text-align: left;"/>
                </colgroup>
                <tr>
                    <td style = "text-align: center;">测试套件名称</td>
                    <td style = "text-align: center;">测试用例名称</td>
                    <td style = "text-align: center;">测试场景名称</td>
                    <td style = "text-align: center;">错误信息</td>
                </tr>
                %(componentDetailNewSucc)s
                <tr>
                    <td>总计</td>
                    <td>1</td>
                    <td>0</td>
                    <td>1</td>
                </tr>
            </table>
    
            <p class='attribute'>
                <strong>已经被废弃</strong><br>
            </p>
            <p></p>
            <table class="resultTable table table-bordered">
                <colgroup>
                    <col style = "text-align: left;"/>
                    <col style = "text-align: left;"/>
                    <col style = "text-align: left;"/>
                    <col style = "text-align: left;"/>
                </colgroup>
                <tr>
                    <td style = "text-align: center;">测试套件名称</td>
                    <td style = "text-align: center;">测试用例名称</td>
                    <td style = "text-align: center;">测试场景名称</td>
                    <td style = "text-align: center;">错误信息</td>
                </tr>
                %(componentDetailDeprecated)s
                <tr>
                    <td>总计</td>
                    <td>1</td>
                    <td>0</td>
                    <td>1</td>
                </tr>
            </table>
    
            <p class='attribute'>
                <strong>长时间失败</strong><br>
            </p>
            <p></p>
            <table class="resultTable table table-bordered">
                <colgroup>
                    <col style = "text-align: left;"/>
                    <col style = "text-align: left;"/>
                    <col style = "text-align: left;"/>
                    <col style = "text-align: left;"/>
                </colgroup>
                <tr>
                    <td style = "text-align: center;">测试套件名称</td>
                    <td style = "text-align: center;">测试用例名称</td>
                    <td style = "text-align: center;">测试场景名称</td>
                    <td style = "text-align: center;">错误信息</td>
                </tr>
                %(componentDetailLongFailure)s
                <tr>
                    <td>总计</td>
                    <td>1</td>
                    <td>0</td>
                    <td>1</td>
                </tr>
            </table>
        </div>
    """

    COMPONENTDETAILNEWFAIL_TMPL = r"""
            <tr class='failClass'>
                <td>%(suiteName)s</td>
                <td>%(caseName)s</td>
                <td>%(scenarioName)s</td>
                <td>%(errorStack)s</td>
            </tr>
    """

    ENDING_TMPL = """<div id='ending'>&nbsp;</div>"""


class Component(object):
    componentName = None
    newDif = []
    newSuc = []
    depreacted = []
    longFailure = []


class CompareTestResult(object):
    title = ""
    taskStartTime = ""
    taskEndTime = ""
    testBranch = ""
    targetLabel = ""
    baseLabel = ""
    submitUser = ""
    workerHost = ""
    componentSummaryList = []
    componentDetailList = []


# -------------------- The end of the Template class -------------------
class CompareTestResultRunner(CompareTestResultTemplate):

    def __init__(self, title=None, description=None):
        self.stopTime = 0

        if title is None:
            self.title = self.DEFAULT_TITLE
        else:
            self.title = title
        if description is None:
            self.description = self.DEFAULT_DESCRIPTION
        else:
            self.description = description

    def getReportAttributes(self, result):
        if self:
            pass
        return [
            (u'任务开始时间', result.taskStartTime),
            (u'任务结束时间', result.taskEndTime),
            (u'比对参考版本', result.baseLabel),
            (u'任务提交来自', result.submitUser),
            (u'任务运行环境', result.workerHost)
        ]

    def generateReport(self, result, output):
        generator = 'HTMLTestRunner %s' % __version__
        stylesheet = self._generate_stylesheet()
        heading = self._generate_heading(result)
        report = self._generate_report(result)
        ending = self._generate_ending()
        htmlContents = self.HTML_TMPL % dict(
            title=saxutils.escape(self.title),
            generator=generator,
            stylesheet=stylesheet,
            heading=heading,
            report=report,
            ending=ending
        )
        # 生成html文件
        m_OutputHandler = open(output, "w", encoding='utf8')
        m_OutputHandler.write(htmlContents)
        m_OutputHandler.close()

        # 复制需要的css和js文件
        m_csspath = os.path.abspath(os.path.join(os.path.dirname(__file__), "css"))
        m_jspath = os.path.abspath(os.path.join(os.path.dirname(__file__), "js"))
        m_new_csspath = os.path.abspath(os.path.join(os.path.dirname(output), "css"))
        m_new_jspath = os.path.abspath(os.path.join(os.path.dirname(output), "js"))
        if m_csspath != m_new_csspath:
            if os.path.exists(m_new_csspath):
                shutil.rmtree(m_new_csspath)
            shutil.copytree(m_csspath, m_new_csspath)
        if m_jspath != m_new_jspath:
            if os.path.exists(m_new_jspath):
                shutil.rmtree(m_new_jspath)
            shutil.copytree(m_jspath, m_new_jspath)

    def _generate_stylesheet(self):
        return self.STYLESHEET_TMPL

    def _generate_heading(self, result):
        report_attrs = self.getReportAttributes(result)
        a_lines = []
        for name, value in report_attrs:
            if value is None:
                value = ""
            line = self.HEADING_ATTRIBUTE_TMPL % dict(
                name=saxutils.escape(name),
                value=saxutils.escape(value),
            )
            a_lines.append(line)
        heading = self.HEADING_TMPL % dict(
            title=saxutils.escape(result.title),
            parameters=''.join(a_lines),
        )
        return heading

    def _generate_report(self, result):
        if self:
            pass
        summaryRows = []
        for component in result.componentSummaryList:
            summaryRow = self.COMPONENTSUMMARYLIST_TMPL % dict(
                cssClass=component["cssClass"],
                componentName=component["componentName"],
                succRate=component["succRate"],
                succCount=component["succCount"],
                failCount=component["failCount"],
                newFailCount=component["newFailCount"],
                newSuccCount=component["newSuccCount"],
                deprecatedCount=component["deprecatedCount"],
                longFailureCount=component["longFailureCount"]
            )
            summaryRows.append(summaryRow)
        detailRows = []
        for component in result.componentDetailList:
            newFails = []
            for newFail in component["componentNewFail"]:
                newFails.append(
                    self.COMPONENTDETAILNEWFAIL_TMPL % dict
                    (
                        suiteName=newFail["suiteName"],
                        caseName=newFail["caseName"],
                        scenarioName=newFail["scenarioName"],
                        errorStack=newFail["errorStack"]
                    )
                )
            newSuccs = []
            for newSucc in component["componentNewSucc"]:
                newSuccs.append(
                    self.COMPONENTDETAILNEWFAIL_TMPL % dict
                    (
                        suiteName=newSucc["suiteName"],
                        caseName=newSucc["caseName"],
                        scenarioName=newSucc["scenarioName"],
                        errorStack=newSucc["errorStack"]
                    )
                )
            deprecateds = []
            for deprecated in component["componentDeprecated"]:
                newFails.append(
                    self.COMPONENTDETAILNEWFAIL_TMPL % dict
                    (
                        suiteName=deprecated["suiteName"],
                        caseName=deprecated["caseName"],
                        scenarioName=deprecated["scenarioName"],
                        errorStack=deprecated["errorStack"]
                    )
                )
            longFailures = []
            for longFailure in component["componentLongFailure"]:
                longFailures.append(
                    self.COMPONENTDETAILNEWFAIL_TMPL % dict
                    (
                        suiteName=longFailure["suiteName"],
                        caseName=longFailure["caseName"],
                        scenarioName=longFailure["scenarioName"],
                        errorStack=longFailure["errorStack"]
                    )
                )
            detailRow = self.COMPONENTDETAILLIST_TMPL % dict(
                componentDetailNewFail="".join(newFails),
                componentDetailNewSucc="".join(newSuccs),
                componentDetailDeprecated="".join(deprecateds),
                componentDetailLongFailure="".join(longFailures),
            )
            detailRows.append(detailRow)

        report = self.REPORT_TMPL % dict(
            componentSummaryList=''.join(summaryRows),
            componentDetailList=''.join(detailRows)
        )
        return report

    def _generate_ending(self):
        return self.ENDING_TMPL


if __name__ == "__main__":
    componentSummaryList = [
        {
            "cssClass": "failClass",
            "componentName": "AA",
            "succRate": "AA",
            "succCount": "AA",
            "failCount": "AA",
            "newFailCount": "AA",
            "newSuccCount": "AA",
            "deprecatedCount": "AA",
            "longFailureCount": "AA",
        }]
    componentDetailList = [
        {
            "componentName": "XXXX",
            "componentNewFail":
                [
                    {"suiteName": "xxx", "caseName": "yyy", "scenarioName": "zzz", "errorStack": "abc"},
                ],
            "componentNewSucc":
                [
                    {"suiteName": "xxx", "caseName": "yyy", "scenarioName": "zzz", "errorStack": "abc"},
                ],
            "componentDeprecated":
                [
                    {"suiteName": "xxx", "caseName": "yyy", "scenarioName": "zzz", "errorStack": "abc"},
                ],
            "componentLongFailure":
                [
                    {"suiteName": "xxx", "caseName": "yyy", "scenarioName": "zzz", "errorStack": "abc"},
                ],
        },
    ]
    compareTestResult = CompareTestResult()
    compareTestResult.title = "测试报告-比对结果"
    compareTestResult.taskStartTime = "2010"
    compareTestResult.taskEndTime = "2010"
    compareTestResult.componentSummaryList = componentSummaryList
    compareTestResult.componentDetailList = componentDetailList

    CompareTestResultRunner = CompareTestResultRunner()
    CompareTestResultRunner.generateReport(
        result=compareTestResult,
        output="E:\\Temp\\aa.html")
