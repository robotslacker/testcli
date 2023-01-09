# -*- coding: utf-8 -*-
import os
import shutil
import copy
import threading
from time import strftime, gmtime, localtime
from enum import Enum
from xml.sax import saxutils

__version__ = "0.0.1"


# ----------------------------------------------------------------------
# Template
class HtmlFileTemplate(object):
    """
    Define a HTML template for report customerization and generation.

    Overall structure of an HTML report

    HTML
    +------------------------+
    |<html>                  |
    |  <head>                |
    |                        |
    |   STYLESHEET           |
    |   +----------------+   |
    |   |                |   |
    |   +----------------+   |
    |                        |
    |  </head>               |
    |                        |
    |  <body>                |
    |                        |
    |   HEADING              |
    |   +----------------+   |
    |   |                |   |
    |   +----------------+   |
    |                        |
    |   REPORT               |
    |   +----------------+   |
    |   |                |   |
    |   +----------------+   |
    |                        |
    |   ENDING               |
    |   +----------------+   |
    |   |                |   |
    |   +----------------+   |
    |                        |
    |  </body>               |
    |</html>                 |
    +------------------------+
    """

    STATUS = {
        0: u'通过',
        1: u'失败',
        2: u'错误',
    }

    DEFAULT_TITLE = 'Unit Test Report'
    DEFAULT_DESCRIPTION = '无详细信息'

    # ------------------------------------------------------------------------
    # HTML Template

    HTML_TMPL = r"""
<!DOCTYPE html>
<html>
<head>
    <title>%(title)s</title>
    <meta name="generator" content="%(generator)s"/>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>

    <link href="css/bootstrap.min.css" rel="stylesheet">
    <script type="text/javascript" src="js/jquery.min.js"></script>
    <script type="text/javascript" src="js/bootstrap.min.js"></script>
    <script type="text/javascript" src="js/echarts.min.js"></script>

    %(stylesheet)s

</head>
<body>
    <script type="text/javascript"><!--
    output_list = Array();

    /* level - 0:Summary; 1:Failed; 2:All */
    function showCase(level) {
        trs = document.getElementsByTagName("tr");
        for (var i = 0; i < trs.length; i++) {
            tr = trs[i];
            id = tr.id;
            if (id.substr(0,2) == 'ft') {
                if (level < 1) {
                    tr.className = 'hiddenRow';
                }
                else {
                    tr.className = '';
                }
            }
            if (id.substr(0,2) == 'pt') {
                if (level > 1) {
                    tr.className = '';
                }
                else {
                    tr.className = 'hiddenRow';
                }
            }
        }
    }


    function showClassDetail(cid, count) {
        var id_list = Array(count);
        var toHide = 1;
        for (var i = 0; i < count; i++) {
            tid0 = 't' + cid.substr(1) + '.' + (i+1);
            tid = 'f' + tid0;
            tr = document.getElementById(tid);
            if (!tr) {
                tid = 'p' + tid0;
                tr = document.getElementById(tid);
            }
            id_list[i] = tid;
            if (tr.className) {
                toHide = 0;
            }
        }
        for (var i = 0; i < count; i++) {
            tid = id_list[i];
            if (toHide) {
                document.getElementById('div_'+tid).style.display = 'none'
                document.getElementById(tid).className = 'hiddenRow';
            }
            else {
                document.getElementById(tid).className = '';
            }
        }
    }


    function showTestDetail(div_id){
        var details_div = document.getElementById(div_id)
        var displayState = details_div.style.display
        // alert(displayState)
        if (displayState != 'block' ) {
            displayState = 'block'
            details_div.style.display = 'block'
        }
        else {
            details_div.style.display = 'none'
        }
    }


    function html_escape(s) {
        s = s.replace(/&/g,'&amp;');
        s = s.replace(/</g,'&lt;');
        s = s.replace(/>/g,'&gt;');
        return s;
    }

    /* obsoleted by detail in <div>
    function showOutput(id, name) {
        var w = window.open("", //url
                        name,
                        "resizable,scrollbars,status,width=800,height=450");
        d = w.document;
        d.write("<pre>");
        d.write(html_escape(output_list[id]));
        d.write("\n");
        d.write("<a href='javascript:window.close()'>close</a>\n");
        d.write("</pre>\n");
        d.close();
    }
    */
    --></script>

    <div id="div_base">
        %(heading)s
        %(report)s
        %(ending)s
        %(chart_script1)s
        %(chart_script2)s
    </div>
</body>
</html>
"""  # variables: (title, generator, stylesheet, heading, report, ending, chart_script)

    ECHARTS_SCRIPT_1 = """
    <script type="text/javascript">
        // 基于准备好的dom，初始化echarts实例
        var myChart = echarts.init(document.getElementById('chart1'));

        // 指定图表的配置项和数据
        var option = {
            tooltip : {
                trigger: 'item',
                formatter: "{a} <br/>{b} : {c} ({d}%%)"
            },
            color: ['LightGreen', 'Orange', 'OrangeRed'],
            legend: {
                orient: 'vertical',
                left: 'left',
                data: ['通过','失败','错误']
            },
            series : [
                {
                    name: '测试执行情况',
                    type: 'pie',
                    radius: ['50%%', '70%%'],
                    center: ['50%%', '60%%'],
                    label: {
                        show: true,
                        position: 'center',
                        formatter: '{title|' + '总体测试通过率' +'}'+ '\\n\\r' + '{percent|%(PassPercent)s}',
                        rich: {
                            title:{
                                fontSize: 20,
                                fontFamily : "Lucida Console",
                                color:'#454c5c'
                            },
                            percent: {
                                fontFamily : "Lucida Console",
                                fontSize: 16,
                                color:'#6c7a89',
                                lineHeight:30,
                            },
                        }
                    },
                    data:[
                        {value:%(Pass)s, name:'通过'},
                        {value:%(fail)s, name:'失败'},
                        {value:%(error)s, name:'错误'}
                    ],
                    itemStyle: {
                        emphasis: {
                            shadowBlur: 10,
                            shadowOffsetX: 0,
                            shadowColor: 'rgba(0, 0, 0, 0.5)'
                        }
                    }
                }
            ]
        };

        // 使用刚指定的配置项和数据显示图表。
        myChart.setOption(option);
    </script>
    """  # variables: (PassPercent, Pass, fail, error)

    ECHARTS_SCRIPT_2 = """
    <script type="text/javascript">
        // 基于准备好的dom，初始化echarts实例
        var myChart = echarts.init(document.getElementById('chart2'));

        // 指定图表的配置项和数据
        option = {
            tooltip: {
                trigger: 'axis',
                axisPointer: {            // Use axis to trigger tooltip
                    type: 'shadow'        // 'shadow' as default; can also be 'line' or 'shadow'
                }
            },
            color: ['OrangeRed','Orange', 'LightGreen'],
            legend: {
                data: ['错误', '失败', '成功'],
            },
            grid: {
                left: '3%%',
                right: '4%%',
                bottom: '3%%',
                containLabel: true
            },
            xAxis: {
                type: 'value'
            },
            yAxis: {
                type: 'category',
                data: [%(userlist)s]
            },
            series: [
                {
                    name: '错误',
                    type: 'bar',
                    stack: 'total',
                    label: {
                        show: true
                    },
                    emphasis: {
                        focus: 'series'
                    },
                    data: [%(userdata_error)s]
                },
                {
                    name: '失败',
                    type: 'bar',
                    stack: 'total',
                    label: {
                        show: true
                    },
                    emphasis: {
                        focus: 'series'
                    },
                    data: [%(userdata_fail)s]
                },
                {
                    name: '成功',
                    type: 'bar',
                    stack: 'total',
                    label: {
                        show: true
                    },
                    emphasis: {
                        focus: 'series'
                    },
                    data: [%(userdata_pass)s]
                },
          ]
        };
        // 使用刚指定的配置项和数据显示图表。
        myChart.setOption(option);
    </script>
    """  # variables: (PassPercent, Pass, fail, error)

    # ------------------------------------------------------------------------
    # Stylesheet
    #
    # alternatively use a <link> for external style sheet, e.g.
    #   <link rel="stylesheet" href="$url" type="text/css">

    STYLESHEET_TMPL = """
<style type="text/css" media="screen">
    body        { font-family: Microsoft YaHei,Consolas,arial,sans-serif; font-size: 80%; }
    table       { font-size: 100%; }
    pre         { white-space: pre-wrap;word-wrap: break-word; }

    /* -- heading ---------------------------------------------------------------------- */
    h1 {
        font-size: 16pt;
        color: gray;
    }
    .heading {
        margin-top: 0ex;
        margin-bottom: 1ex;
    }

    .attribute {
        margin-top: 1ex;
        margin-bottom: 0;
    }

    .description {
        margin-top: 2ex;
        margin-bottom: 3ex;
    }

    /* -- css div popup ------------------------------------------------------------------------ */
    a.popup_link {
    }

    a.popup_link:hover {
        color: red;
    }

    .popup_window {
        display: none;
        position: relative;
        left: 0px;
        top: 0px;
        /*border: solid #627173 1px; */
        padding: 10px;
        /*background-color: #E6E6D6; */
        font-family: "Lucida Console", "Courier New", Courier, monospace;
        text-align: left;
        font-size: 8pt;
        /* width: 500px;*/
    }

    }
    /* -- report ------------------------------------------------------------------------ */
    #show_detail_line {
        margin-top: 3ex;
        margin-bottom: 1ex;
    }
    #result_table {
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
    .errorClass { background-color: OrangeRed; }
    .passCase   { color: Black; }
    .failCase   { color: Orange; font-weight: bold; }
    .errorCase  { color: OrangeRed; font-weight: bold; }
    .hiddenRow  { display: none; }
    .testcase   { margin-left: 2em; }


    /* -- ending ---------------------------------------------------------------------- */
    #ending {
    }

    #div_base {
                position:absolute;
                top:0%;
                left:5%;
                right:5%;
                width: auto;
                height: auto;
                margin: -15px 0 0 0;
    }
</style>
"""

    # ------------------------------------------------------------------------
    # Heading
    #

    HEADING_TMPL = """
    <div class='page-header'>
        <h1>%(title)s</h1>
    %(parameters)s
    </div>
    <div style="float: left;width:100%%;">
        <div style="float: left;width:40%%;"><p class='description'>%(description)s</p></div>
        <div id="chart1" style="width:30%%;height:300px;float:left;"></div>
        <div id="chart2" style="width:30%%;height:300px;float:left;"></div>
    </div>
"""  # variables: (title, parameters, description)

    HEADING_ATTRIBUTE_TMPL = """<p class='attribute'><strong>%(name)s:</strong> %(value)s</p>
"""  # variables: (name, value)

    # ------------------------------------------------------------------------
    # Report
    #

    REPORT_TMPL = u"""
    <div class="btn-group btn-group-sm">
        <button class="btn btn-default" onclick='javascript:showCase(0)'>总结</button>
        <button class="btn btn-default" onclick='javascript:showCase(1)'>失败</button>
        <button class="btn btn-default" onclick='javascript:showCase(2)'>全部</button>
    </div>
    <p></p>
    <table id='result_table' class="table table-bordered">
        <colgroup>
            <col align='left' />
            <col align='right' />
            <col align='right' />
            <col align='right' />
            <col align='right' />
            <col align='right' />
        </colgroup>
        <tr id='header_row'>
            <td align='center'>测试套件/测试用例</td>
            <td align='center'>总数</td>
            <td align='center'>通过</td>
            <td align='center'>失败</td>
            <td align='center'>错误</td>
            <td align='center'>负责人</td>
            <td align='center'>开始时间</td>
            <td align='center'>运行耗时</td>
            <td align='center'>首次失败版本</td>
            <td colspan=2 align='center'>详细日志</td>
        </tr>
        %(test_list)s
        <tr id='total_row'>
            <td>总计</td>
            <td align='right'>%(count)s</td>
            <td align='right'>%(Pass)s</td>
            <td align='right'>%(fail)s</td>
            <td align='right'>%(error)s</td>
            <td align='center'>--------</td>            
            <td align='center'>%(starttime)s</td>
            <td align='center'>%(elapsedtime)s</td>
            <td align='center'>--------</td>
            <td>&nbsp;</td>
            <td>&nbsp;</td>
        </tr>
    </table>
"""  # variables: (test_list, count, Pass, fail, error)

    # 整个Suite的统计信息
    REPORT_CLASS_TMPL = u"""
    <tr class='%(style)s'>
        <td>%(desc)s</td>
        <td align='right'>%(count)s</td>
        <td align='right'>%(Pass)s</td>
        <td align='right'>%(fail)s</td>
        <td align='right'>%(error)s</td>
        <td align='center'>%(owner)s</td>
        <td align='center'>%(starttime)s</td>
        <td align='center'>%(elapsedtime)s</td>
        <td align='center'>%(firstbadlabel)s</td>
        <td colspan=2 align='center'><a href="javascript:showClassDetail('%(cid)s',%(count)s)">详情</a></td>
    </tr>
"""  # variables: (style, desc, count, Pass, fail, error, cid)

    # 具体Case的统计信息
    REPORT_TEST_WITH_OUTPUT_TMPL = r"""
<tr id='%(tid)s' class='%(Class)s'>
    <td class='%(style)s'><div class='testcase'>%(desc)s</div></td>
    <td colspan='4' align='center'>
        <!--css div popup start-->
        <a class="popup_link" onfocus='this.blur();' href="javascript:showTestDetail('div_%(tid)s')" >
            %(status)s</a>
        <div id='div_%(tid)s' class="popup_window">
            <pre>%(script)s</pre>
        </div>
        <!--css div popup end-->
    </td>
    <td align='center'>%(owner)s</td>
    <td align='center'>%(starttime)s</td>
    <td align='center'>%(elapsedtime)s</td>
    <td align='center'>%(firstbadlabel)s</td>
    <td align='center'><a href="%(link)s">详细测试报告</a></td>
    <td align='center'><a href="%(download)s">运行日志下载</a></td>
</tr>
"""  # variables: (tid, Class, style, desc, link, status)

    # 具体Case的统计信息
    REPORT_TEST_NO_OUTPUT_TMPL = r"""
<tr id='%(tid)s' class='%(Class)s'>
    <td class='%(style)s'><div class='testcase'>%(desc)s</div></td>
    <td colspan='4' align='center'>%(status)s</td>
    <td align='center'>%(owner)s</td>
    <td align='center'>%(starttime)s</td>
    <td align='center'>%(elapsedtime)s</td>
    <td align='center'>%(firstbadlabel)s</td>
    <td align='center'><a href="%(link)s">详细测试报告</a></td>
    <td align='center'><a href="%(download)s">运行日志下载</a></td>
</tr>
"""  # variables: (tid, Class, style, desc, status)

    REPORT_TEST_OUTPUT_TMPL = r"""%(id)s: %(output)s"""  # variables: (id, output)

    # ------------------------------------------------------------------------
    # ENDING
    #

    ENDING_TMPL = """<div id='ending'>&nbsp;</div>"""


# -------------------- The end of the Template class -------------------


class TestCaseStatus(Enum):
    UNKNOWN = 0
    SUCCESS = 1
    FAILURE = 2
    ERROR = 3


class TestCase(object):
    def __init__(self):
        self.CaseName = None
        self.CaseStatus = TestCaseStatus.UNKNOWN
        self.CaseDescription = ""
        self.ErrorStackTrace = ""
        # tid 命名方法：  pt%d%d     成功Case
        # tid 命名方法：  ft%d%d     失败Case  %suiteid.%caseid
        self.tid = ""  # case id
        self.DetailReportLink = ""  # 指向外部的测试报告
        self.DownloadURLLink = ""  # 日志文件下载链接
        self.CaseStartTime = ""
        self.CaseElapsedTime = 0  # 用秒来计算的运行时间
        self.CaseOwner = ""
        self.CaseRTI = ""  # Case的Regress Tracking Issue ID
        self.CaseFirstBadLabel = ""  # Case第一次失败的版本

    def getCaseRTI(self):
        return self.CaseRTI

    def setCaseRTI(self, p_CaseRTI):
        self.CaseRTI = p_CaseRTI

    def getCaseFirstBadLabel(self):
        return self.CaseFirstBadLabel

    def setCaseFirstBadLabel(self, p_CaseFirstBadLabel):
        self.CaseFirstBadLabel = p_CaseFirstBadLabel

    def getCaseName(self):
        return self.CaseName

    def setCaseName(self, p_CaseName):
        self.CaseName = p_CaseName

    def getCaseOwner(self):
        return self.CaseOwner

    def setCaseOwner(self, p_CaseOwner):
        self.CaseOwner = p_CaseOwner

    def getDownloadURLLink(self):
        return self.DownloadURLLink

    def setDownloadURLLink(self, p_DownloadURLLink):
        self.DownloadURLLink = p_DownloadURLLink

    def getCaseStartTime(self):
        return self.CaseStartTime

    def setCaseStartTime(self, p_CaseStartTime):
        self.CaseStartTime = p_CaseStartTime

    def getCaseElapsedTime(self):
        return self.CaseElapsedTime

    def setCaseElapsedTime(self, p_CaseElapsedTime):
        self.CaseElapsedTime = p_CaseElapsedTime

    def setCaseStatus(self, p_CaseStatus):
        self.CaseStatus = p_CaseStatus

    def getCaseStatus(self):
        return self.CaseStatus

    def getCaseDescription(self):
        return self.CaseDescription

    def getErrorStackTrace(self):
        return self.ErrorStackTrace

    def setErrorStackTrace(self, p_ErrorStackTrace):
        self.ErrorStackTrace = p_ErrorStackTrace

    def setTID(self, p_TID):
        self.tid = p_TID

    def getTID(self):
        return self.tid

    def getDetailReportLink(self):
        return self.DetailReportLink

    def setDetailReportLink(self, p_DetailReportLink):
        self.DetailReportLink = p_DetailReportLink


class TestSuite(object):
    def __init__(self):
        self.SuiteName = None
        self.TestCases = []
        self.SuiteDescription = ""
        self.PassedCaseCount = 0
        self.FailedCaseCount = 0
        self.ErrorCaseCount = 0
        self.sid = 0
        self.max_tid = 1
        self.SuiteStartTime = ""
        self.SuiteElapsedTime = 0  # 用秒来计算的运行时间
        self.SuiteOwnerList = ""  # Suite的所有人，可能包含多个人，多个人用逗号分割
        self.SuiteFirstBadLabel = ""  # 第一次出问题的Label

    def getSuiteName(self):
        return self.SuiteName

    def getSuiteOwnerList(self):
        return self.SuiteOwnerList

    def getSuiteFirstBadLabel(self):
        return self.SuiteFirstBadLabel

    def setSuiteFirstBadLabel(self, p_SuiteFirstBadLabel):
        self.SuiteFirstBadLabel = p_SuiteFirstBadLabel

    def getSuiteStartTime(self):
        return self.SuiteStartTime

    def setSuiteStartTime(self, p_SuiteStartTime):
        self.SuiteStartTime = p_SuiteStartTime

    def getSuiteElapsedTime(self):
        return self.SuiteElapsedTime

    def setSuiteElapsedTime(self, p_SuiteElapsedTime):
        self.SuiteElapsedTime = p_SuiteElapsedTime

    def setSuiteName(self, p_SuiteName):
        self.SuiteName = p_SuiteName

    def addTestCase(self, p_TestCase):
        for testCase in self.TestCases:
            if testCase.getCaseName() == p_TestCase.getCaseName():
                self.TestCases.remove(testCase)
                break
        m_TestCase = copy.copy(p_TestCase)
        self.TestCases.append(m_TestCase)

    def SummaryTestCase(self):
        m_OldCases = copy.copy(self.TestCases)
        m_TestCasesOwnerList = []
        self.TestCases = []
        for m_case in m_OldCases:
            if m_case.getCaseStatus() == TestCaseStatus.SUCCESS:
                self.PassedCaseCount = self.PassedCaseCount + 1
            if m_case.getCaseStatus() == TestCaseStatus.FAILURE:
                self.FailedCaseCount = self.FailedCaseCount + 1
            if m_case.getCaseStatus() == TestCaseStatus.ERROR:
                self.ErrorCaseCount = self.ErrorCaseCount + 1
            # 从Suite中查找最早的StartTime以及累计ElapsedTime
            if self.getSuiteStartTime() == "":
                self.setSuiteStartTime(m_case.getCaseStartTime())
            elif self.getSuiteStartTime() > m_case.getCaseStartTime():
                self.setSuiteStartTime(m_case.getCaseStartTime())
            self.setSuiteElapsedTime(self.getSuiteElapsedTime() + int(m_case.getCaseElapsedTime()))
            if self.getSuiteFirstBadLabel() == "":
                self.setSuiteFirstBadLabel(m_case.getCaseFirstBadLabel())
            elif self.getSuiteFirstBadLabel() > m_case.getCaseFirstBadLabel():
                self.setSuiteFirstBadLabel(m_case.getCaseFirstBadLabel())
            # 不重复的记录每一个Case的Owner
            if m_case.getCaseOwner() not in m_TestCasesOwnerList:
                m_TestCasesOwnerList.append(m_case.getCaseOwner())
            m_case.setTID(self.max_tid)
            self.max_tid = self.max_tid + 1
            self.TestCases.append(m_case)
        # 拼接整个Suite的Owner，即把所有Case的Owner都用逗号隔开
        if m_TestCasesOwnerList is None:
            self.SuiteOwnerList = "Not defined."
        else:
            # 不排除没有填写owner的情况
            while None in m_TestCasesOwnerList:
                m_TestCasesOwnerList.remove(None)
            self.SuiteOwnerList = ','.join(m_TestCasesOwnerList)

    def getSuiteDescription(self):
        return self.SuiteDescription

    def setSuiteDescription(self, p_SuiteDescription):
        self.SuiteDescription = p_SuiteDescription

    def getPassedCaseCount(self):
        return self.PassedCaseCount

    def getFailedCaseCount(self):
        return self.FailedCaseCount

    def getErrorCaseCount(self):
        return self.ErrorCaseCount

    def setSID(self, p_SID):
        self.sid = p_SID

    def getSID(self):
        return self.sid


class TestResult(object):

    def __init__(self):
        self.TestSuites = []
        self.pass_count = 0
        self.fail_count = 0
        self.error_count = 0
        self.max_sid = 1
        self.starttime = ""
        self.elapsedtime = 0
        self.Title = "未知标题"
        self.Description = "无描述信息"
        self.targetLabel = ""
        self.testBranch = ""
        self.robotOptions = ""
        self.testOptions = ""
        self.lock = threading.Lock()

    def getTitle(self):
        return self.Title

    def setTitle(self, p_Title):
        self.Title = p_Title

    def getDescription(self):
        return self.Description

    def setDescription(self, p_Description):
        self.Description = p_Description

    def getTestStartTime(self):
        return self.starttime

    def setTestStartTime(self, p_TestStartTime):
        self.starttime = p_TestStartTime

    def getTestElapsedTime(self):
        return self.elapsedtime

    def setTestElapsedTime(self, p_TestElapsedTime):
        self.elapsedtime = p_TestElapsedTime

    def addSuite(self, p_TestSuite):
        # 考虑并发操作下的线程安全
        self.lock.acquire()

        try:
            # 更新TestResult的全局统计信息
            self.pass_count = self.pass_count + p_TestSuite.PassedCaseCount
            self.fail_count = self.fail_count + p_TestSuite.FailedCaseCount
            self.error_count = self.error_count + p_TestSuite.ErrorCaseCount
            if self.getTestStartTime() == "":
                self.setTestStartTime(p_TestSuite.getSuiteStartTime())
            elif self.getTestStartTime() > p_TestSuite.getSuiteStartTime():
                self.setTestStartTime(p_TestSuite.getSuiteStartTime())
            self.setTestElapsedTime(self.getTestElapsedTime() + p_TestSuite.getSuiteElapsedTime())

            m_TestSuite = copy.copy(p_TestSuite)
            m_TestSuite.setSID(self.max_sid)
            self.max_sid = self.max_sid + 1
            self.TestSuites.append(m_TestSuite)
        except Exception as e:
            raise e
        finally:
            self.lock.release()


class HTMLTestRunner(HtmlFileTemplate):

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

    def getReportAttributes(self, result: TestResult):
        if self:
            pass
        """
        Return report attributes as a list of (name, value).
        Override this to add custom attributes.
        """
        startTime = str(result.starttime)
        duration = strftime("%H:%M:%S", gmtime(int(result.elapsedtime)))
        status = []
        targetLabel = str(result.targetLabel)
        testBranch = str(result.testBranch)
        robotOptions = str(result.robotOptions)
        testOptions = str(result.testOptions)

        if result.pass_count:
            status.append(u'通过 %s' % result.pass_count)
        if result.fail_count:
            status.append(u'失败 %s' % result.fail_count)
        if result.error_count:
            status.append(u'错误 %s' % result.error_count)
        if status:
            status = ' '.join(status)
        else:
            status = 'none'
        return [
            (u'开始时间', startTime),
            (u'结束时间', strftime("%Y-%m-%d %H:%M:%S", localtime())),
            (u'运行时长', duration),
            (u'状态', status),
            (u'数据库版本', targetLabel),
            (u'测试分支', testBranch),
            (u'测试选项1', robotOptions),
            (u'测试选项2', testOptions),
        ]

    def generateReport(self, result, output):
        generator = 'HTMLTestRunner %s' % __version__
        stylesheet = self._generate_stylesheet()
        heading = self._generate_heading(result)
        report = self._generate_report(result)
        ending = self._generate_ending()
        chart1 = self._generate_chart1(result)
        chart2 = self._generate_chart2(result)
        htmlContents = self.HTML_TMPL % dict(
            title=saxutils.escape(self.title),
            generator=generator,
            stylesheet=stylesheet,
            heading=heading,
            report=report,
            ending=ending,
            chart_script1=chart1,
            chart_script2=chart2
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
            line = self.HEADING_ATTRIBUTE_TMPL % dict(
                name=saxutils.escape(name),
                value=saxutils.escape(value),
            )
            a_lines.append(line)
        heading = self.HEADING_TMPL % dict(
            title=saxutils.escape(result.getTitle()),
            parameters=''.join(a_lines),
            # 对描述信息不进行转义，以保证其中的换行符显示
            description=result.getDescription(),
        )
        return heading

    def _generate_report(self, result):
        rows = []
        nPos = 1
        for m_TestSuite in result.TestSuites:
            m_TestSuite.setSID(nPos)
            nPos = nPos + 1
            if len(m_TestSuite.getSuiteDescription()) == 0:
                desc = m_TestSuite.getSuiteName()
            else:
                desc = m_TestSuite.getSuiteDescription()

            if m_TestSuite.getErrorCaseCount() > 0:
                m_CSSStype = "errorClass"
            elif m_TestSuite.getFailedCaseCount() > 0:
                m_CSSStype = "failClass"
            else:
                m_CSSStype = "passClass"
            m_TotalCaseCount = \
                m_TestSuite.getPassedCaseCount() + m_TestSuite.getFailedCaseCount() + m_TestSuite.getErrorCaseCount()
            row = self.REPORT_CLASS_TMPL % dict(
                style=m_CSSStype,
                desc=desc,
                count=m_TotalCaseCount,
                Pass=m_TestSuite.getPassedCaseCount(),
                fail=m_TestSuite.getFailedCaseCount(),
                error=m_TestSuite.getErrorCaseCount(),
                owner=m_TestSuite.getSuiteOwnerList(),
                starttime=m_TestSuite.getSuiteStartTime(),
                elapsedtime=strftime("%H:%M:%S", gmtime(int(m_TestSuite.getSuiteElapsedTime()))),
                firstbadlabel=m_TestSuite.getSuiteFirstBadLabel(),
                cid="c" + str(m_TestSuite.getSID()),
            )
            rows.append(row)

            # 生成Suite下面TestCase的详细内容
            for m_TestCase in m_TestSuite.TestCases:
                self._generate_report_test(rows, m_TestSuite.getSID(), m_TestCase)

        report = self.REPORT_TMPL % dict(
            test_list=''.join(rows),
            count=str(result.pass_count + result.fail_count + result.error_count),
            Pass=str(result.pass_count),
            fail=str(result.fail_count),
            starttime=result.starttime,
            elapsedtime=strftime("%H:%M:%S", gmtime(int(result.elapsedtime))),
            error=str(result.error_count),
        )
        return report

    def _generate_chart1(self, result):
        m_TotalCaseCount = result.pass_count + result.fail_count + result.error_count
        if m_TotalCaseCount == 0:
            m_PassPercent = "-----"
        else:
            m_PassPercent = str("{:.2f}".format(result.pass_count / m_TotalCaseCount * 100)) + "%"
        chart = self.ECHARTS_SCRIPT_1 % dict(
            PassPercent=m_PassPercent,
            Pass=str(result.pass_count),
            fail=str(result.fail_count),
            error=str(result.error_count),
        )
        return chart

    def _generate_chart2(self, result):
        # 遍历所有的TestCase，获得TestCase的Owner列表
        m_TestCaseOwnerList = []
        for m_TestSuite in result.TestSuites:
            for m_TestCase in m_TestSuite.TestCases:
                if m_TestCase.getCaseOwner() not in m_TestCaseOwnerList:
                    m_TestCaseOwnerList.append(m_TestCase.getCaseOwner())
        # 循环获得用户列表
        m_TestCaseOwnerParameter = ""
        # 不排除没有填写owner的情况
        while None in m_TestCaseOwnerList:
            m_TestCaseOwnerList.remove(None)
        for m_User in m_TestCaseOwnerList:
            if m_TestCaseOwnerParameter == "":
                m_TestCaseOwnerParameter = "'" + m_User + "'"
            else:
                m_TestCaseOwnerParameter = m_TestCaseOwnerParameter + ",'" + m_User + "'"
        # 循环获得用户各种情况测试案例的统计数据
        m_TestCaseFailCountList = []
        m_TestCaseErrorCountList = []
        m_TestCasePassCountList = []
        m_TestCaseOwnerFailParameter = ""
        m_TestCaseOwnerErrorParameter = ""
        m_TestCaseOwnerPassParameter = ""
        for m_User in m_TestCaseOwnerList:
            m_TestCaseFailCount = 0
            m_TestCaseErrorCount = 0
            m_TestCasePassCount = 0
            for m_TestSuite in result.TestSuites:
                for m_TestCase in m_TestSuite.TestCases:
                    if m_TestCase.getCaseOwner() == m_User:
                        if m_TestCase.getCaseStatus() == TestCaseStatus.FAILURE:
                            m_TestCaseFailCount = m_TestCaseFailCount + 1
                        if m_TestCase.getCaseStatus() == TestCaseStatus.ERROR:
                            m_TestCaseErrorCount = m_TestCaseErrorCount + 1
                        if m_TestCase.getCaseStatus() == TestCaseStatus.SUCCESS:
                            m_TestCasePassCount = m_TestCasePassCount + 1
            m_TestCaseFailCountList.append(m_TestCaseFailCount)
            m_TestCaseErrorCountList.append(m_TestCaseErrorCount)
            m_TestCasePassCountList.append(m_TestCasePassCount)
        for m_Count in m_TestCaseFailCountList:
            if m_TestCaseOwnerFailParameter == "":
                m_TestCaseOwnerFailParameter = str(m_Count)
            else:
                m_TestCaseOwnerFailParameter = m_TestCaseOwnerFailParameter + "," + str(m_Count)
        for m_Count in m_TestCaseErrorCountList:
            if m_TestCaseOwnerErrorParameter == "":
                m_TestCaseOwnerErrorParameter = str(m_Count)
            else:
                m_TestCaseOwnerErrorParameter = m_TestCaseOwnerErrorParameter + "," + str(m_Count)
        for m_Count in m_TestCasePassCountList:
            if m_TestCaseOwnerPassParameter == "":
                m_TestCaseOwnerPassParameter = str(m_Count)
            else:
                m_TestCaseOwnerPassParameter = m_TestCaseOwnerPassParameter + "," + str(m_Count)
        chart = self.ECHARTS_SCRIPT_2 % dict(
            userlist=m_TestCaseOwnerParameter,
            userdata_error=m_TestCaseOwnerErrorParameter,
            userdata_fail=m_TestCaseOwnerFailParameter,
            userdata_pass=m_TestCaseOwnerPassParameter,
        )
        return chart

    def _generate_report_test(self, rows, cid, p_TestCase):
        has_output = len(p_TestCase.getErrorStackTrace()) != 0
        if p_TestCase.getCaseStatus() == TestCaseStatus.SUCCESS:
            tid = "pt" + str(cid) + "." + str(p_TestCase.getTID())
            m_Status = "通过"
        elif p_TestCase.getCaseStatus() == TestCaseStatus.FAILURE:
            tid = "ft" + str(cid) + "." + str(p_TestCase.getTID())
            m_Status = "失败" + "(RTI: " + str(p_TestCase.getCaseRTI()) + ")"
        else:
            tid = "ft" + str(cid) + "." + str(p_TestCase.getTID())
            m_Status = "错误" + "(RTI: " + str(p_TestCase.getCaseRTI()) + ")"
        if has_output:
            m_Status = m_Status + "(点击查看详细信息)"
        if len(p_TestCase.getCaseDescription()) == 0:
            desc = p_TestCase.getCaseName()
        else:
            desc = p_TestCase.getCaseDescription()
        tmpl = has_output and self.REPORT_TEST_WITH_OUTPUT_TMPL or self.REPORT_TEST_NO_OUTPUT_TMPL

        script = self.REPORT_TEST_OUTPUT_TMPL % dict(
            id=tid,
            output=saxutils.escape(p_TestCase.getErrorStackTrace()),
        )

        if p_TestCase.getCaseStatus() == TestCaseStatus.SUCCESS:
            m_CSS_CaseStyle = "none"
        elif p_TestCase.getCaseStatus() == TestCaseStatus.FAILURE:
            m_CSS_CaseStyle = "failCase"
        else:
            m_CSS_CaseStyle = "errorCase"
        row = tmpl % dict(
            tid=tid,
            Class='hiddenRow',
            style=m_CSS_CaseStyle,
            desc=desc,
            starttime=p_TestCase.getCaseStartTime(),
            elapsedtime=strftime("%H:%M:%S", gmtime(int(p_TestCase.getCaseElapsedTime()))),
            link=p_TestCase.getDetailReportLink(),
            download=p_TestCase.getDownloadURLLink(),
            firstbadlabel=p_TestCase.getCaseFirstBadLabel(),
            script=script,
            status=m_Status,
            owner=p_TestCase.getCaseOwner()
        )
        rows.append(row)
        if not has_output:
            return

    def _generate_ending(self):
        return self.ENDING_TMPL
