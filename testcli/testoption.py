# -*- coding: utf-8 -*-
"""处理程序运行的各种参数."""
import os


class TestOptions(object):
    """处理程序运行的各种参数."""
    def __init__(self):
        self.testOptionList = []

        self.testOptionList.append({"Name": "WHENEVER_ERROR",
                                    "Value": "CONTINUE",
                                    "Comments": '',
                                    "Hidden": False})
        self.testOptionList.append({"Name": "PAGE",
                                    "Value": "OFF",
                                    "Comments": 'ON|OFF',
                                    "Hidden": False})
        self.testOptionList.append({"Name": "ECHO",
                                    "Value": "ON",
                                    "Comments": 'ON|OFF',
                                    "Hidden": False})
        self.testOptionList.append({"Name": "TIMING",
                                    "Value": "OFF",
                                    "Comments": 'ON|OFF',
                                    "Hidden": False})
        self.testOptionList.append({"Name": "TIME",
                                    "Value": "OFF",
                                    "Comments": 'ON|OFF',
                                    "Hidden": False})
        self.testOptionList.append({"Name": "FEEDBACK",
                                    "Value": "ON",
                                    "Comments": 'ON|OFF',
                                    "Hidden": False
                                    })
        self.testOptionList.append({"Name": "TERMOUT",
                                    "Value": "ON",
                                    "Comments": 'ON|OFF',
                                    "Hidden": False
                                    })
        self.testOptionList.append({"Name": "SQL_FETCHSIZE",
                                    "Value": 10000,
                                    "Comments": '',
                                    "Hidden": False})
        self.testOptionList.append({"Name": "LOB_LENGTH",
                                    "Value": 20,
                                    "Comments": '',
                                    "Hidden": False})
        self.testOptionList.append({"Name": "FLOAT_FORMAT",
                                    "Value": "%.7g",
                                    "Comments": '',
                                    "Hidden": False})
        self.testOptionList.append({"Name": "DECIMAL_FORMAT",
                                    "Value": "",
                                    "Comments": '',
                                    "Hidden": False})
        self.testOptionList.append({"Name": "DATE_FORMAT",
                                    "Value": "%Y-%m-%d",
                                    "Comments": '',
                                    "Hidden": False})
        self.testOptionList.append({"Name": "DATETIME_FORMAT",
                                    "Value": "%Y-%m-%d %H:%M:%S.%f",
                                    "Comments": '',
                                    "Hidden": False})
        self.testOptionList.append({"Name": "TIME_FORMAT",
                                    "Value": "%H:%M:%S.%f",
                                    "Comments": '',
                                    "Hidden": False})
        self.testOptionList.append({"Name": "DATETIME-TZ_FORMAT",
                                    "Value": "%Y-%m-%d %H:%M:%S %z",
                                    "Comments": '',
                                    "Hidden": False})

        self.testOptionList.append({"Name": "OUTPUT_SORT_ARRAY",
                                    "Value": "ON",
                                    "Comments": 'Print Array output with sort order. ON|OFF',
                                    "Hidden": False})
        self.testOptionList.append({"Name": "OUTPUT_PREFIX",
                                    "Value": "",
                                    "Comments": 'Output Prefix',
                                    "Hidden": False})
        self.testOptionList.append({"Name": "OUTPUT_ERROR_PREFIX",
                                    "Value": "",
                                    "Comments": 'Error Output Prefix',
                                    "Hidden": False})
        self.testOptionList.append({"Name": "OUTPUT_FORMAT",
                                    "Value": "TAB",
                                    "Comments": 'TAB|CSV',
                                    "Hidden": False
                                    })
        self.testOptionList.append({"Name": "OUTPUT_CSV_HEADER",
                                    "Value": "OFF",
                                    "Comments": 'ON|OFF',
                                    "Hidden": False})
        self.testOptionList.append({"Name": "OUTPUT_CSV_DELIMITER",
                                    "Value": ",",
                                    "Comments": '',
                                    "Hidden": False})
        self.testOptionList.append({"Name": "OUTPUT_CSV_QUOTECHAR",
                                    "Value": "",
                                    "Comments": '',
                                    "Hidden": False})

        self.testOptionList.append({"Name": "SQLCONN_RETRYTIMES",
                                    "Value": "1",
                                    "Comments": 'Connect retry times.',
                                    "Hidden": False})
        self.testOptionList.append({"Name": "DEBUG",
                                    "Value": "OFF",
                                    "Comments": 'ON|OFF',
                                    "Hidden": True})
        self.testOptionList.append({"Name": "CONNURL",
                                    "Value": "",
                                    "Comments": 'Connection URL',
                                    "Hidden": False})
        self.testOptionList.append({"Name": "CONNSCHEMA",
                                    "Value": "",
                                    "Comments": 'Current DB schema',
                                    "Hidden": False})
        self.testOptionList.append({"Name": "SILENT",
                                    "Value": "OFF",
                                    "Comments": 'ON|OFF',
                                    "Hidden": True})
        self.testOptionList.append({"Name": "SQL_EXECUTE",
                                    "Value": "PREPARE",
                                    "Comments": 'DIRECT|PREPARE',
                                    "Hidden": False})

        self.testOptionList.append({"Name": "JOBMANAGER",
                                    "Value": "OFF",
                                    "Comments": 'ON|OFF',
                                    "Hidden": False})
        self.testOptionList.append({"Name": "JOBMANAGER_METAURL",
                                    "Value": "",
                                    "Comments": '',
                                    "Hidden": False})

        self.testOptionList.append({"Name": "SCRIPT_TIMEOUT",
                                    "Value": -1,
                                    "Comments": '',
                                    "Hidden": False})
        self.testOptionList.append({"Name": "SQL_TIMEOUT",
                                    "Value": -1,
                                    "Comments": '',
                                    "Hidden": False})
        self.testOptionList.append({"Name": "API_TIMEOUT",
                                    "Value": -1,
                                    "Comments": '',
                                    "Hidden": False})

        self.testOptionList.append({"Name": "SCRIPT_ENCODING",
                                    "Value": "UTF-8",
                                    "Comments": '',
                                    "Hidden": False})

        self.testOptionList.append({"Name": "RESULT_ENCODING",
                                    "Value": "UTF-8",
                                    "Comments": '',
                                    "Hidden": False})

        self.testOptionList.append({"Name": "SSH_ENCODING",
                                    "Value": "UTF-8",
                                    "Comments": 'SSH channel default encoding.',
                                    "Hidden": False})

        self.testOptionList.append({"Name": "COMPARE_DEFAULT_METHOD",
                                    "Value": "AUTO",
                                    "Comments": 'Default compare algorithm.',
                                    "Hidden": False})

        self.testOptionList.append({"Name": "COMPARE_DIFFLIB_THRESHOLD",
                                    "Value": 1000,
                                    "Comments": 'Threshold(lines) for use difflib in auto compare algorithm.',
                                    "Hidden": False})

        self.testOptionList.append({"Name": "NAMESPACE",
                                    "Value": "SQL",
                                    "Comments": 'Script Namespace, SQL|API',
                                    "Hidden": False})

        self.testOptionList.append({"Name": "MONITORMANAGER",
                                    "Value": "OFF",
                                    "Comments": 'ON|OFF',
                                    "Hidden": False})

        self.testOptionList.append({"Name": "API_HTTPSVERIFY",
                                    "Value": "OFF",
                                    "Comments": 'ON|OFF (Default)',
                                    "Hidden": False})
        self.testOptionList.append({"Name": "API_HTTPPROXY",
                                    "Value": "",
                                    "Comments": 'Proxy address of http request. (Default)',
                                    "Hidden": False})

        # 如果DEBUG选项设置为TRUE，需要处理
        for pos in range(0, len(self.testOptionList)):
            # 如果环境变量中未设置TESTCLI_DEBUG，则用参数的值去设置
            if "TESTCLI_DEBUG" not in os.environ:
                if self.testOptionList[pos]["Name"] == 'DEBUG':
                    if self.testOptionList[pos]["Value"] == 'ON':
                        os.environ['TESTCLI_DEBUG'] = "1"
                    elif self.testOptionList[pos]["Value"] == 'OFF':
                        if 'TESTCLI_DEBUG' in os.environ:
                            del os.environ['TESTCLI_DEBUG']

    def get(self, p_ParameterName):
        """根据参数名称返回参数，若不存在该参数，返回None."""
        for item in self.testOptionList:
            if item["Name"] == p_ParameterName:
                return item["Value"]
        return None

    def getOptionList(self):
        """返回全部的运行参数列表"""
        return self.testOptionList

    def set(self, p_ParameterName, p_ParameterValue, p_ParameterDefaultValue=None, p_Hidden=False):
        """设置运行参数， 若p_ParameterValue为空，则加载默认参数"""
        for pos in range(0, len(self.testOptionList)):
            if self.testOptionList[pos]["Name"] == p_ParameterName:
                if p_ParameterValue is None:
                    m_ParameterValue = None
                else:
                    m_ParameterValue = str(p_ParameterValue).strip()
                    if m_ParameterValue.upper().startswith("${ENV(") and m_ParameterValue.upper().endswith(")}"):
                        m_EnvName = m_ParameterValue[6:-2]
                        if m_EnvName in os.environ:
                            m_ParameterValue = os.environ[m_EnvName]
                        else:
                            m_ParameterValue = None
                if m_ParameterValue is None:
                    if p_ParameterDefaultValue is None:
                        m_ParameterValue = ""
                    else:
                        m_ParameterValue = p_ParameterDefaultValue
                self.testOptionList[pos]["Value"] = m_ParameterValue
                return True

        # 对@开头的进行保存和处理
        m_ParameterName = p_ParameterName.strip()
        if m_ParameterName.startswith("@"):
            m_ParameterValue = p_ParameterValue.strip()
            if m_ParameterValue.upper().startswith("${ENV(") and m_ParameterValue.upper().endswith(")}"):
                m_EnvName = m_ParameterValue[6:-2]
                if m_EnvName in os.environ:
                    m_ParameterValue = os.environ[m_EnvName]
                else:
                    m_ParameterValue = None

            if m_ParameterValue is None:
                if p_ParameterDefaultValue is None:
                    m_ParameterValue = ""
                else:
                    m_ParameterValue = p_ParameterDefaultValue
            self.testOptionList.append({"Name": m_ParameterName,
                                        "Value": m_ParameterValue,
                                        "Hidden": p_Hidden,
                                        "Comments": 'User session variable'})
            return True

        # 对于不认识的参数信息，直接抛出到上一级别，做CommmonNotFound处理
        return False
