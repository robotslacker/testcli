# -*- coding: UTF-8 -*-
import os
import sys
import traceback
import pytest
import sqlite3
import time
import multiprocessing
from robot.errors import ExecutionFailed
from robot.api import logger
from robot.running.context import EXECUTION_CONTEXTS
from abc import ABC, abstractmethod
from collections import defaultdict
import re
import datetime
import xml.etree.ElementTree as ElementTree
from typing import Dict, Any, Optional, Union, List


class TransformerException(Exception):
    pass


class AbstractTransformer(ABC):
    """Abstract class for implementation transformers"""
    key = None

    def __init__(self, ignore_errors: bool = False,
                 removing_types: bool = False):
        self.ignore_errors = ignore_errors
        self.removing_types = removing_types

    def transform_node(self, node_data: Dict) -> Dict:
        if self.check_node_data(node_data):
            if self.ignore_errors:
                node_data['#text'] = self.get_safe_value(node_data)
            else:
                node_data['#text'] = self.get_value(node_data)
            node_data = self.remove_type_from_node_data(node_data)
        return node_data

    def check_node_data(self, node_data: Dict) -> bool:
        if node_data.get("@type") != self.key:
            return False
        if "#text" not in node_data:
            return False
        return True

    def get_safe_value(self, node_data: Dict) -> Any:
        try:
            value = self.get_value(node_data)
        except TransformerException:
            value = node_data.get("#text")
        return value

    def get_value(self, node_data: Dict) -> Any:
        try:
            return self.get_value_or_raise_exception(node_data)
        except Exception as e:
            raise TransformerException(
                '{0}: {1}'.format(self.__class__, str(e)))

    @abstractmethod
    def get_value_or_raise_exception(self, node_data: Dict) -> Any:
        pass

    def remove_type_from_node_data(self, node_data: Dict) -> Dict:
        if self.removing_types:
            del node_data["@type"]
        return node_data

    def set_ignore_errors(self, ignore_errors: bool) -> None:
        self.ignore_errors = ignore_errors

    def set_removing_types(self, removing_types: bool) -> None:
        self.removing_types = removing_types


class IntegerTransformer(AbstractTransformer):
    """Transformer for integers"""
    key = "integer"

    def get_value_or_raise_exception(self, node_data: Dict) -> int:
        return int(node_data['#text'])


class BoolTransformer(AbstractTransformer):
    """Transformer for booleans"""
    key = "bool"

    def get_value_or_raise_exception(self, node_data: Dict) -> bool:
        value = node_data['#text'].lower()
        if value == 'true':
            value = True
        elif value == 'false':
            value = False
        else:
            raise TypeError('Value has to be "true" or "false"')
        return value


class DateTimeTransformer(AbstractTransformer):
    """Transformer for datetime.datetime"""
    key = "datetime"
    datetime_format = "%Y-%m-%dT%H:%M:%SZ"

    def get_value_or_raise_exception(
            self, node_data: Dict) -> datetime.datetime:
        value = node_data['#text'].lower()
        value = datetime.datetime.strptime(value, self.datetime_format)
        return value

    def set_datetime_format(self, datetime_format: str) -> None:
        self.datetime_format = datetime_format


class PullTransformers:
    def __init__(self, *transformers):
        self.transformers = dict()
        self.add_transformers(*transformers)

    def add_transformers(self, *transformers) -> None:
        for transformer in transformers:
            self.__register_transformer(transformer)

    def __register_transformer(
            self, transformer: Union[AbstractTransformer, type]) -> None:
        transformer_instance = self.__get_transformer_instance(transformer)
        if isinstance(transformer_instance, AbstractTransformer):
            self.transformers[transformer_instance.key] = transformer_instance

    @staticmethod
    def __get_transformer_instance(
            transformer: Union[AbstractTransformer, type]
            ) -> AbstractTransformer:
        if isinstance(transformer, type):
            return transformer()
        return transformer

    def transform_node(self, node_data: Dict) -> Dict:
        key = self.get_key(node_data)
        if key is not None:
            transformer = self.get_transformer(key)
            if transformer is not None:
                return transformer.transform_node(node_data)
        return node_data

    @staticmethod
    def get_key(node_data: Dict) -> Optional[str]:
        if '@type' in node_data:
            return node_data['@type']

    def get_transformer(self, key: str) -> Optional[AbstractTransformer]:
        if key in self.transformers:
            return self.transformers[key]
        return None

    def set_ignore_errors(self, ignore_errors: bool) -> None:
        for transformer_key in self.transformers:
            self.transformers[transformer_key].set_ignore_errors(
                ignore_errors
            )

    def set_removing_types(self, removing_types: bool) -> None:
        for transformer_key in self.transformers:
            self.transformers[transformer_key].set_removing_types(
                removing_types
            )


DefaultTransformerList = [
    IntegerTransformer, BoolTransformer, DateTimeTransformer]


class XmlToDict(object):
    """Class to work with xml.etree.ElementTree objects"""
    _pull_transformers = None

    def __init__(self, node: ElementTree, ignore_namespace: bool = False):
        """
        Init instance
        :param node: XML object
        :param ignore_namespace: removing namespace from tags
        """
        self.node = node
        self.ignore_namespace = ignore_namespace
        self.child_nodes = list()

    def get_dict(self) -> Dict:
        """
        Extract data from xml.etree.ElementTree object
            which has been passed during initialization of an instance
        :return: extracted data as a python dict
        """
        tag = self.get_tag()
        self.child_nodes = self._get_child_nodes()
        if self._is_single_node():
            value = self._get_dict_from_single_node()
        else:
            value = self._get_dict_from_node_with_children()
        return {tag: value}

    def get_tag(self) -> str:
        """
        Get a tag of the current node.
            If ignore_namespace is True then
            namespace will be removed from a tag.
        :return: a tag
        """
        tag = self.node.tag
        if self.ignore_namespace:
            tag = re.sub(r'{[^}]+}', '', tag)
        return tag

    def _get_child_nodes(self) -> List:
        """
        Get child nodes of xml.etree.ElementTree object
            which has been passed during initialization of an instance
            as XmlToDict instances.
            All options (ignore_namespace, transformers) of the current class
            will be used for children nodes
        :return: List of XmlToDict instances
        """
        child_nodes = []
        for child_node in self.node:
            xml_to_dict_node = XmlToDict(
                child_node, ignore_namespace=self.ignore_namespace)
            if self._pull_transformers is not None:
                xml_to_dict_node.use_pull_transformers(
                    self._pull_transformers)
            child_nodes.append(xml_to_dict_node)
        return child_nodes

    def _is_single_node(self) -> bool:
        """
        If node has no child nodes, this node is a single node
        :return: result of check
        """
        return True if not self.child_nodes else False

    def _get_dict_from_single_node(self) -> Dict:
        """
        Extract data from the current node, ignoring child nodes, and
            transform result, using instance transformers
        :return: Python dict with data node
        """
        data_node = self._get_single_data_node()
        transformed_data_node = self._transform_node(data_node)
        grouped_data_node = self._group_single_node_data(transformed_data_node)
        return grouped_data_node

    def _get_single_data_node(self) -> Dict:
        """
        Extract value and attributes of the current node
        :return: Python dict with data node
        """
        attributes = self._get_attributes()
        node_value = {'#text': self._get_value()}
        data_node = {**attributes, **node_value}
        return data_node

    def _get_value(self) -> Union[str, None]:
        """
        Get node value
        :return: node value
        """
        value = self.node.text
        if value is not None:
            value = value.strip()
        return value

    def _transform_node(self, node_data: Dict) -> Dict:
        """
        Transform data node, using instance transformers
        :param node_data: data for transformation
        :return: transformed data
        """
        if self._pull_transformers is not None:
            node_data = self._pull_transformers.transform_node(node_data)
        return node_data

    @staticmethod
    def _group_single_node_data(node_data: Dict) -> Dict:
        """
        Group node data if node data has just a value
        xmltodict3.XmlToDict._group_single_node_data({'#text': '1'})
        '1'
        :param node_data: node data to group
        :return:grouped node data
        """
        if tuple(node_data.keys()) == ('#text',):
            node_data = node_data['#text']
        return node_data

    def _get_dict_from_node_with_children(self) -> Dict:
        """
        Get node attributes and data from child nodes
        :return: node data
        """
        attributes = self._get_attributes()
        children_data = self._get_children_data()
        value = {**children_data, **attributes}
        return value

    def _get_attributes(self) -> Dict:
        """
        Get node attributes.
            Attributes are marked with "@" in the attribute name
        :return: node attributes as dict
        """
        attributes = dict()
        for attribute_name in self.node.attrib:
            key = '@' + attribute_name
            attributes[key] = self.node.attrib[attribute_name]
        return attributes

    def _get_children_data(self) -> Dict:
        """
        Get data from child nodes
        :return: nodes data as dict
        """
        node_data = defaultdict(list)
        for child_node in self.child_nodes:
            tag = child_node.get_tag()
            node_data[tag].append(child_node.get_dict()[tag])
        node_data = self._group_children_data(node_data)
        return node_data

    @staticmethod
    def _group_children_data(children_data: defaultdict) -> Dict:
        """
         children_data = defaultdict(list)
         children_data['tag1'].append({'#value': None})
         children_data['tag2'].append({'#value': None})
         children_data['tag2'].append({'#value': '111'})
         xmltodict3.XmlToDict._group_children_data(children_data)
        {'tag1': {'#value': None},
        'tag2': [{'#value': None}, {'#value': '111'}]}
        :param children_data: data from child nodes
        :return: grouped data
        """
        grouped_data = dict()
        for tag in children_data:
            sub_node_data = children_data[tag]
            if len(sub_node_data) == 1:
                grouped_data[tag] = sub_node_data[0]
            else:
                grouped_data[tag] = sub_node_data
        return grouped_data

    def use_pull_transformers(
            self, pull_transformers: PullTransformers) -> None:
        """
        Set up pull_transformation for data transformation
        :param pull_transformers: PullTransformers instance
        """
        if isinstance(pull_transformers, PullTransformers):
            self._pull_transformers = pull_transformers


class XmlTextToDict:
    """Class to work with strings which contain XML"""
    def __init__(self, xml_text: str, ignore_namespace: bool = False):
        """
        Init instance
        :param xml_text: string with XML
        :param ignore_namespace: removing namespace from tags
        """
        self.xml_text = xml_text
        self.ignore_namespace = ignore_namespace
        self._pull_transformers = None

    def get_dict(self) -> Dict:
        """
        Extract data which has been passed during initialization of an instance
        :return: extracted data as a python dict
        """
        xml_to_dict_node = self.get_xml_to_dict_node()
        if self._pull_transformers is not None:
            xml_to_dict_node.use_pull_transformers(
                self._pull_transformers)
        return xml_to_dict_node.get_dict()

    def get_xml_to_dict_node(self) -> XmlToDict:
        """
        Prepare a XmlToDict instance
        :return: a XmlToDict instance with data
        """
        root_node = ElementTree.fromstring(self.xml_text)
        xml_to_dict_node = XmlToDict(
            root_node, ignore_namespace=self.ignore_namespace)
        return xml_to_dict_node

    def use_pull_transformers(
            self, pull_transformers: PullTransformers) -> None:
        """
        Set up pull_transformation for using into XmlToDict object
        :param pull_transformers: PullTransformers instance
        """
        if isinstance(pull_transformers, PullTransformers):
            self._pull_transformers = pull_transformers


class XmlFileToDict:
    """Class to work with XML files"""
    def __init__(self, file_path: str, ignore_namespace: bool = False):
        """
        Init instance
        :param file_path: path to XML file
        :param ignore_namespace: removing namespace from tags
        """
        self.file_path = file_path
        self.ignore_namespace = ignore_namespace
        self._pull_transformers = None

    def get_dict(self) -> Dict:
        """
        Prepare a XmlToDict instance
        :return: a XmlToDict instance with data
        """
        tree_node = ElementTree.parse(self.file_path)
        root_node = tree_node.getroot()
        xml_to_dict_node = XmlToDict(
            root_node, ignore_namespace=self.ignore_namespace)
        return xml_to_dict_node.get_dict()


def runPythonScript(scriptFileName, logFileName, pythonPathList):
    # 切换输出到指定的文件中
    sys.stdout = open(logFileName, mode="a")
    sys.stderr = open(logFileName, mode="a")
    sys.__stdout__ = open(logFileName, mode="a")
    sys.__stderr__ = open(logFileName, mode="a")

    # 增加Python的执行路径
    for pythonPath in pythonPathList:
        if pythonPath not in sys.path:
            sys.path.append(pythonPath)

    # 开始运行指定的Python程序
    try:
        with open(scriptFileName, mode='r', encoding="utf-8") as f:
            scriptContent = f.read()
            exec(scriptContent)
    except Exception:
        print('traceback.print_exc():\n%s' % traceback.print_exc())
        print('traceback.format_exc():\n%s' % traceback.format_exc())

    # 关闭输出文件
    sys.stdout.close()
    sys.stderr.close()
    sys.__stderr__.close()
    sys.__stdout__.close()


class RunPython(object):
    # TEST SUITE 在suite中引用，只会实例化一次
    # 也就是说多test case都引用了这个类的方法，但是只有第一个test case调用的时候实例化
    # 如果一个Suite多个Case引用设置类的方法，要注意先后的影响
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    __BreakWithError = False                # 是否遇到错误就退出，默认是不退出
    xlogFileHandle = None                   # 扩展日志的句柄
    pythonPathList = []                     # Python的执行包路径

    def Append_Python_Path(self, pythonPath):
        pythonPath = os.path.abspath(pythonPath)
        if os.path.exists(pythonPath):
            if pythonPath not in self.pythonPathList:
                self.pythonPathList.append(pythonPath)
                logger.info("<b>Append Python Path : " + str(pythonPath) + "</b>", html=True)
            else:
                logger.warn(
                    "<b>Append Python Path : " + str(pythonPath) + " SKIP. Duplicate directory!</b>",
                    html=True)
        else:
            logger.warn(
                "<b>Append Python Path : " + str(pythonPath) + " SKIP. Directory does not exist!</b>",
                html=True)

    def Execute_Python_Script(self, scriptFileName, logFileName=None):
        try:
            logger.info('<b>===== Logon_And_Execute_Script</b> [' + str(scriptFileName) + '] ', html=True)

            # 判断文件是否存在
            if not os.path.exists(scriptFileName):
                raise RuntimeError("Script [" + scriptFileName + "] does not exist.")

            # 如果路径名中包含空格，则需要用单引号包括起来
            if str(scriptFileName).find(' ') != -1 and not str(scriptFileName).startswith("'"):
                scriptFileName = "'" + scriptFileName + "'"

            # 处理日志文件名
            # 如果没有提供文件名， 有T_WORK，   日志是T_WORK下和SQL同名的.log文件
            # 如果没有提供文件名， 没有T_WORK， 日志是当前目录下和SQL同名的.log文件
            # 如果提供了文件名，   并且是全路径名， 用提供的名字
            # 如果提供了文件名，   但不是全路径名，有T_WORK下，在T_WORK下生成提供的文件名
            # 如果提供了文件名，   但不是全路径名，没有T_WORK下，在当前目录下生成提供的文件名
            if logFileName is None:
                if "T_WORK" in os.environ:
                    m_szLogOutPutFileName = os.path.join(
                        os.environ["T_WORK"],
                        os.path.basename(scriptFileName).split('.')[0] + ".log")
                    logOutPutFullFileName = os.path.join(os.environ["T_WORK"], m_szLogOutPutFileName)
                else:
                    m_szLogOutPutFileName = os.path.join(
                        os.getcwd(),
                        os.path.basename(scriptFileName).split('.')[0] + ".log")
                    logOutPutFullFileName = os.path.join(os.getcwd(), m_szLogOutPutFileName)
            else:
                if "T_WORK" in os.environ:
                    logOutPutFullFileName = os.path.join(os.environ["T_WORK"], logFileName)
                else:
                    logOutPutFullFileName = os.path.join(os.getcwd(), logFileName)
            xdbReportFile = logOutPutFullFileName[:-4] + ".xdb"

            # 如果Log目录不存在，则创建Log目录
            if not os.path.exists(os.path.dirname(logOutPutFullFileName)):
                os.makedirs(os.path.dirname(logOutPutFullFileName))

            logger.info('<b>===== Execute</b>     [' + scriptFileName + ']', html=True)
            logger.info('<b>===== LogFile</b>     [' + str(logOutPutFullFileName) + ']', html=True)

            sys.__stdout__.write('\n')  # 打印一个空行，好保证在Robot上Console显示不错行
            sys.__stdout__.write('===== Execute     [' + scriptFileName + ']\n')
            sys.__stdout__.write('===== LogFile     [' + logOutPutFullFileName + ']\n')
            sys.__stdout__.write('===== Starting .....\n')

            # 备份当前的系统输出和错误输出
            stdout_bak = sys.stdout
            stderr_bak = sys.stderr
            internal_stdout_bak = sys.__stdout__
            internal_stderr_bak = sys.__stderr__

            # 在子进程中运行，以确保子进程的失败不会影响到主程序
            processManagerContext = multiprocessing.get_context("spawn")
            process = processManagerContext.Process(
                target=runPythonScript,
                args=(scriptFileName, logOutPutFullFileName, self.pythonPathList)
            )
            processStartTime = time.time()
            process.start()
            process.join()
            processEndTime = time.time()
            exitCode = process.exitcode

            # 还原当前的系统输出和错误输出
            sys.stdout = stdout_bak
            sys.stderr = stderr_bak
            sys.__stdout__ = internal_stdout_bak
            sys.__stderr__ = internal_stderr_bak

            sys.__stdout__.write("===== Finished with ret [" + str(exitCode) + "] .....\n")

            # 记录扩展日志
            if EXECUTION_CONTEXTS.current is None:
                suiteName = "--------"
                caseName = "--------"
            else:
                suiteName = str(EXECUTION_CONTEXTS.current.suite)
                if hasattr(EXECUTION_CONTEXTS.current.test, "name"):
                    caseName = str(EXECUTION_CONTEXTS.current.test.name)
                else:
                    caseName = "--------"  # Setup Or TearDown

            self.xlogFileHandle = sqlite3.connect(
                database=xdbReportFile,
                check_same_thread=False,
            )
            cursor = self.xlogFileHandle.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS TestCli_Xlog "
                           "("
                           "  Id              INTEGER PRIMARY KEY AUTOINCREMENT,"
                           "  Script          TEXT,"
                           "  Started         DATETIME,"
                           "  Elapsed         NUMERIC,"
                           "  ErrorCode       TEXT,"
                           "  WorkerName      TEXT,"
                           "  SuiteName       TEXT,"
                           "  CaseName        TEXT,"
                           "  ScenarioId      TEXT,"
                           "  TestRunId       TEXT,"
                           "  ScenarioName    TEXT"
                           ")"
                           "")
            cursor = self.xlogFileHandle.cursor()
            # 对于单体的Python测试，scenarioId, scenarioName同时为caseName
            data = (
                scriptFileName,
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(processStartTime)),
                "%8.2f" % (processEndTime - processStartTime),
                str(exitCode),
                os.path.basename(scriptFileName) + "-" + str(os.getpid()),
                str(suiteName),
                str(caseName),
                str(os.environ['T_RUNID']),
                caseName,
                caseName
            )
            cursor.execute(
                "Insert Into TestCli_Xlog(Script,Started,Elapsed,"
                "ErrorCode,WorkerName,SuiteName,CaseName,"
                "ScenarioId, TestRunId, ScenarioName) "
                "Values(?,?,?,  ?,?,?,?, ?,?,?)",
                data
            )
            cursor.close()
            self.xlogFileHandle.commit()
            self.xlogFileHandle.close()

            # 如果有失败信息，则直接退出
            if exitCode != 0:
                raise ExecutionFailed(
                    message="Test failed. Please check more information.",
                    continue_on_failure=self.__BreakWithError
                )
        except RuntimeError as ex:
            raise ex
        except Exception as ex:
            logger.info('str(e):  ', str(ex))
            logger.info('repr(e):  ', repr(ex))
            logger.info('traceback.print_exc():\n%s' % traceback.print_exc())
            logger.info('traceback.format_exc():\n%s' % traceback.format_exc())
            raise RuntimeError("TEST Execute failed.")

    def Execute_Pytest_Script(self, scriptFileName, logFileName=None):
        try:
            logger.info('<b>===== Logon_And_Execute_Script</b> [' + str(scriptFileName) + '] ', html=True)

            # 判断文件是否存在
            if not os.path.exists(scriptFileName):
                raise RuntimeError("Script [" + scriptFileName + "] does not exist.")

            # 如果路径名中包含空格，则需要用单引号包括起来
            if str(scriptFileName).find(' ') != -1 and not str(scriptFileName).startswith("'"):
                scriptFileName = "'" + scriptFileName + "'"

            # 处理日志文件名
            # 如果没有提供文件名， 有T_WORK，   日志是T_WORK下和SQL同名的.log文件
            # 如果没有提供文件名， 没有T_WORK， 日志是当前目录下和SQL同名的.log文件
            # 如果提供了文件名，   并且是全路径名， 用提供的名字
            # 如果提供了文件名，   但不是全路径名，有T_WORK下，在T_WORK下生成提供的文件名
            # 如果提供了文件名，   但不是全路径名，没有T_WORK下，在当前目录下生成提供的文件名
            if logFileName is None:
                if "T_WORK" in os.environ:
                    m_szLogOutPutFileName = os.path.join(
                        os.environ["T_WORK"],
                        os.path.basename(scriptFileName).split('.')[0] + ".log")
                    logOutPutFullFileName = os.path.join(os.environ["T_WORK"], m_szLogOutPutFileName)
                else:
                    m_szLogOutPutFileName = os.path.join(
                        os.getcwd(),
                        os.path.basename(scriptFileName).split('.')[0] + ".log")
                    logOutPutFullFileName = os.path.join(os.getcwd(), m_szLogOutPutFileName)
            else:
                if "T_WORK" in os.environ:
                    logOutPutFullFileName = os.path.join(os.environ["T_WORK"], logFileName)
                else:
                    logOutPutFullFileName = os.path.join(os.getcwd(), logFileName)
            htmlReportFile = logOutPutFullFileName[:-4] + ".html"
            junitReportFile = logOutPutFullFileName[:-4] + ".xml"
            xdbReportFile = logOutPutFullFileName[:-4] + ".xdb"

            # 如果Log目录不存在，则创建Log目录
            if not os.path.exists(os.path.dirname(logOutPutFullFileName)):
                os.makedirs(os.path.dirname(logOutPutFullFileName))

            logger.info('<b>===== Execute</b>     [' + scriptFileName + ']', html=True)
            logger.info('<b>===== LogFile</b>     [' + str(logOutPutFullFileName) + ']', html=True)
            logger.info('<b>===== PytestLog</b>   [<a href="' + os.path.basename(htmlReportFile) + '">Pytest report: ' +
                        os.path.basename(htmlReportFile) + '</a>].', html=True)

            sys.__stdout__.write('\n')  # 打印一个空行，好保证在Robot上Console显示不错行
            sys.__stdout__.write('===== Execute     [' + scriptFileName + ']\n')
            sys.__stdout__.write('===== LogFile     [' + logOutPutFullFileName + ']\n')
            sys.__stdout__.write('===== Starting .....\n')

            # 备份当前的系统输出和错误输出
            stdout_bak = sys.stdout
            stderr_bak = sys.stderr
            internal_stdout_bak = sys.__stdout__
            internal_stderr_bak = sys.__stderr__

            # 切换输出到指定的文件中
            sys.stdout = open(logOutPutFullFileName, mode="a")
            sys.stderr = open(logOutPutFullFileName, mode="a")
            sys.__stdout__ = open(logOutPutFullFileName, mode="a")
            sys.__stderr__ = open(logOutPutFullFileName, mode="a")
            myargs = [
                "-vs",
                "--capture=sys",
                "--html=" + htmlReportFile,
                "--junitxml=" + junitReportFile,
                scriptFileName,
            ]
            logger.info('<b>===== args</b>     [' + str(myargs) + ']', html=True)
            logger.info('<b>=====  pwd</b>     [' + str(os.getcwd()) + ']', html=True)

            # 追加新的Python路径
            for pythonPath in self.pythonPathList:
                if pythonPath not in sys.path:
                    logger.info('<b>Add Python Path' + str(pythonPath) + '</b>', html=True)
                    sys.path.append(pythonPath)

            # 打印当前的Python执行路径，便于调试
            logger.info('<b>Python Path</b>', html=True)
            print("Python Path:")
            for modulePath in sys.path:
                logger.info("<b>    " + modulePath + "</b>", html=True)
                print("    " + str(modulePath))

            processStartTime = time.time()
            # 运行pytest脚本
            try:
                exitCode = pytest.main(args=myargs, )
            except Exception:
                exitCode = 255
                print('traceback.print_exc():\n%s' % traceback.print_exc())
                print('traceback.format_exc():\n%s' % traceback.format_exc())

            # 关闭输出文件
            sys.stdout.close()
            sys.stderr.close()
            sys.__stderr__.close()
            sys.__stdout__.close()

            # 还原当前的系统输出和错误输出
            sys.stdout = stdout_bak
            sys.stderr = stderr_bak
            sys.__stdout__ = internal_stdout_bak
            sys.__stderr__ = internal_stderr_bak

            sys.__stdout__.write("===== Finished with ret [" + str(exitCode) + "] .....\n")

            # 记录扩展日志
            if EXECUTION_CONTEXTS.current is None:
                suiteName = "--------"
                caseName = "--------"
            else:
                suiteName = str(EXECUTION_CONTEXTS.current.suite)
                if hasattr(EXECUTION_CONTEXTS.current.test, "name"):
                    caseName = str(EXECUTION_CONTEXTS.current.test.name)
                else:
                    caseName = "--------"  # Setup Or TearDown

            self.xlogFileHandle = sqlite3.connect(
                database=xdbReportFile,
                check_same_thread=False,
            )
            cursor = self.xlogFileHandle.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS TestCli_Xlog "
                           "("
                           "  Id              INTEGER PRIMARY KEY AUTOINCREMENT,"
                           "  Script          TEXT,"
                           "  Started         DATETIME,"
                           "  Elapsed         NUMERIC,"
                           "  CommandType     TEXT,"
                           "  Command         TEXT,"
                           "  CommandStatus   TEXT,"
                           "  ErrorCode       TEXT,"
                           "  WorkerName      TEXT,"
                           "  SuiteName       TEXT,"
                           "  CaseName        TEXT,"
                           "  ScenarioId      TEXT,"
                           "  TestRunId       TEXT,"
                           "  ScenarioName    TEXT"
                           ")"
                           "")
            cursor = self.xlogFileHandle.cursor()
            # 对于Pytest测试，读取junitReportFile作为结果
            testResultJson = XmlFileToDict(junitReportFile).get_dict()
            testCases = testResultJson["testsuites"]["testsuite"]["testcase"]
            failureMessages = ""
            if type(testCases) == dict:
                if "error" in testCases.keys():
                    failureMessages = (failureMessages + "\nmessage:\n" + testCases["error"]["@message"] +
                                       "\n" + "text:\n" + testCases["error"]["#text"])
            if type(testCases) == list:
                for testCase in testCases:
                    if "skipped" in testCase.keys():
                        continue
                    if "failure" in testCase.keys():
                        failureMessages = (failureMessages + "\nmessage:\n" + testCase["failure"]["@message"] +
                                           "\n" + "text:\n" + testCase["failure"]["#text"])
                        commandStatus = "Failure"
                    else:
                        commandStatus = "Failure"
                    scenarioName = testCase["@name"]
                    # 这里有一个隐含的规则，即假设case的名称为 xxx_123，即最后为数字，则将数字作为scenarioId
                    if str(scenarioName).split('_')[-1].isdigit():
                        scenarioId = str(scenarioName).split('_')[-1]
                    else:
                        scenarioId = scenarioName
                    elapsedTime = str(testCase["@time"])
                    data = (
                        scriptFileName,
                        time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(processStartTime)),
                        elapsedTime,
                        "PYTEST",
                        str(caseName),
                        commandStatus,
                        str(exitCode),
                        os.path.basename(scriptFileName) + "-" + str(os.getpid()),
                        str(suiteName),
                        str(caseName),
                        str(os.environ['T_RUNID']),
                        scenarioId,
                        scenarioName
                    )
                    cursor.execute(
                        "Insert Into TestCli_Xlog(Script,Started,Elapsed,"
                        "CommandType, Command, CommandStatus,"
                        "ErrorCode, WorkerName, SuiteName, CaseName,"
                        "ScenarioId, TestRunId, ScenarioName) "
                        "Values(?,?,?, ?,?,?,  ?,?,?,?, ?,?,?)",
                        data
                    )
                cursor.close()
                self.xlogFileHandle.commit()
            self.xlogFileHandle.close()

            # 如果有失败信息，则打印错误消息，直接退出
            if len(failureMessages) != 0:
                print(failureMessages)
            if exitCode != 0:
                raise ExecutionFailed(
                    message="Test failed. Please check more information.",
                    continue_on_failure=self.__BreakWithError
                )
        except ExecutionFailed as ex:
            raise RuntimeError("TEST Execute failed. " + str(ex.message))
        except Exception as ex:
            logger.info('str(e):  ', str(ex))
            logger.info('repr(e):  ', repr(ex))
            logger.info('traceback.print_exc():\n%s' % traceback.print_exc())
            logger.info('traceback.format_exc():\n%s' % traceback.format_exc())
            raise RuntimeError("TEST Execute failed.")
