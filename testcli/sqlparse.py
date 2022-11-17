# -*- coding: utf-8 -*-
import re
import os
import shlex
from antlr4 import InputStream
from antlr4 import CommonTokenStream
from antlr4.error.ErrorListener import ErrorListener
from .datawrapper import random_ascii_letters_and_digits
from .testcliexception import TestCliException
from .antlrgen.ClientLexer import ClientLexer
from .antlrgen.ClientParser import ClientParser
from .ClientVisitor import ClientVisitor


class ClientErrorListener(ErrorListener):
    __slots__ = 'num_errors'

    def __init__(self):
        super().__init__()
        self.num_errors = 0
        self.msg = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.num_errors = self.num_errors + 1

        errMsg = "行{}:{}  {} ".format(str(line), str(column), msg)

        self.msg.append(errMsg)

        super().syntaxError(recognizer, offendingSymbol, line, column, msg, e)


class SQLMapping(object):
    # MappingList = { Mapping_Name : Mapping_Contents}
    # Mapping_Contents = [ filename_pattern, match_roles[] ]
    # match_roles = [ Key, Value]
    m_SQL_MappingList = {}

    def Load_SQL_Mappings(self, p_szTestScriptFileName, p_szSQLMappings):
        # 如果不带任何参数，或者参数为空，则清空SQLMapping信息
        if p_szSQLMappings is None:
            self.m_SQL_MappingList = {}
            return

        m_SQL_Mappings = shlex.shlex(p_szSQLMappings)
        m_SQL_Mappings.whitespace = ','
        m_SQL_Mappings.quotes = "'"
        m_SQL_Mappings.whitespace_split = True

        # 如果没有传递脚本名称，则认为是在Console中执行
        if p_szTestScriptFileName is None:
            m_szTestScriptFileName = "Console"
        else:
            m_szTestScriptFileName = p_szTestScriptFileName

        # 循环处理每一个Mapping信息
        for m_SQL_MappingFile in list(m_SQL_Mappings):
            m_SQL_MappingBaseName = None
            m_SQL_MappingFullName = None

            if os.path.isfile(m_SQL_MappingFile):
                # 用户提供的是全路径名
                m_SQL_MappingBaseName = os.path.basename(m_SQL_MappingFile)  # 不包含路径的文件名
                m_SQL_MappingFullName = os.path.abspath(m_SQL_MappingFile)
            elif os.path.isfile(os.path.join(
                    os.path.dirname(m_szTestScriptFileName),
                    m_SQL_MappingFile)):
                # 用户提供的是当前目录下的文件
                m_SQL_MappingBaseName = os.path.basename(m_SQL_MappingFile)  # 不包含路径的文件名
                m_SQL_MappingFullName = os.path.join(
                    os.path.dirname(m_szTestScriptFileName), m_SQL_MappingFile)
            elif os.path.isfile(os.path.join(
                    os.path.dirname(m_szTestScriptFileName),
                    m_SQL_MappingFile + ".map")):
                # 用户提供的是当前目录下的文件
                m_SQL_MappingBaseName = os.path.basename(m_SQL_MappingFile)  # 不包含路径的文件名
                m_SQL_MappingFullName = os.path.join(
                    os.path.dirname(m_szTestScriptFileName),
                    m_SQL_MappingFile + ".map")
            if m_SQL_MappingFullName is None or m_SQL_MappingBaseName is None:
                # 压根没有找到这个文件
                if "TESTCLI_DEBUG" in os.environ:
                    print("SQLCLI-0003::  Mapping file [" + m_SQL_MappingFile + "] not found.")
                continue

            # 加载配置文件
            if "TESTCLI_DEBUG" in os.environ:
                print("Loading ... [" + m_SQL_MappingFullName + "]")
            with open(m_SQL_MappingFullName, 'r') as f:
                m_SQL_Mapping_Contents = f.readlines()

            # 去掉配置文件中的注释信息, 包含空行，单行完全注释，以及文件行内注释的注释部分
            pos = 0
            while pos < len(m_SQL_Mapping_Contents):
                if (m_SQL_Mapping_Contents[pos].startswith('#') and
                    not m_SQL_Mapping_Contents[pos].startswith('#.')) or \
                        len(m_SQL_Mapping_Contents[pos]) == 0:
                    m_SQL_Mapping_Contents.pop(pos)
                else:
                    pos = pos + 1
            for pos in range(0, len(m_SQL_Mapping_Contents)):
                if m_SQL_Mapping_Contents[pos].find('#') != -1 and \
                        not m_SQL_Mapping_Contents[pos].startswith('#.'):
                    m_SQL_Mapping_Contents[pos] = \
                        m_SQL_Mapping_Contents[pos][0:m_SQL_Mapping_Contents[pos].find('#')]

            # 分段加载配置文件
            m_inSection = False
            m_szNamePattern = None
            m_szMatchRules = []
            m_szFileMatchRules = []
            for m_szLine in m_SQL_Mapping_Contents:
                m_szLine = m_szLine.strip()
                if not m_inSection and m_szLine.startswith("#.") and m_szLine.endswith(':'):
                    # 文件注释开始
                    m_inSection = True
                    m_szNamePattern = m_szLine[2:-1]  # 去掉开始的的#.以前最后的:
                    m_szMatchRules = []
                    continue
                if m_inSection and m_szLine == "#.":
                    # 文件注释结束
                    m_szFileMatchRules.append([m_szNamePattern, m_szMatchRules])
                    m_szNamePattern = None
                    m_szMatchRules = []
                    m_inSection = False
                    continue
                if m_inSection:
                    # 文件配置段中的内容
                    if m_szLine.find('=>') != -1:
                        m_szMatchRule = [m_szLine[0:m_szLine.find('=>')].strip(),
                                         m_szLine[m_szLine.find('=>') + 2:].strip()]
                        m_szMatchRules.append(m_szMatchRule)
                    continue

            # 每个文件的配置都加载到MappingList中
            self.m_SQL_MappingList[m_SQL_MappingBaseName] = m_szFileMatchRules

    @staticmethod
    def ReplaceMacro_Env(p_arg):
        m_EnvName = p_arg[0].replace("'", "").replace('"', "").strip()
        if m_EnvName in os.environ:
            return os.environ[m_EnvName]
        else:
            return ""

    @staticmethod
    def ReplaceMacro_Random(p_arg):
        m_RandomType = p_arg[0].replace("'", "").replace('"', "").strip()
        if m_RandomType.lower() == "random_ascii_letters_and_digits":
            if str(p_arg[1]).isnumeric():
                m_RandomLength = int(p_arg[1])
                return random_ascii_letters_and_digits([m_RandomLength, ])
            else:
                return ""

    def ReplaceSQL(self, p_szSQL, p_Key, p_Value):
        # 首先查找是否有匹配的内容，如果没有，直接返回
        try:
            m_SearchResult = re.search(p_Key, p_szSQL, re.DOTALL)
        except re.error as ex:
            raise TestCliException("[WARNING] Invalid regex pattern. [" + str(p_Key) + "]  " + repr(ex))

        if m_SearchResult is None:
            return p_szSQL
        else:
            # 记录匹配到的内容
            m_SearchedKey = m_SearchResult.group()

        # 将内容用{}来进行分割，以处理各种内置的函数，如env等
        m_row_struct = re.split('[{}]', p_Value)
        if len(m_row_struct) == 1:
            # 没有任何内置的函数， 直接替换掉结果就可以了
            m_Value = p_Value
        else:
            # 存在内置的函数，即数据中存在{}包括的内容
            for m_nRowPos in range(0, len(m_row_struct)):
                if re.search(r'env(.*)', m_row_struct[m_nRowPos], re.IGNORECASE):
                    # 函数的参数处理，即函数的参数可能包含， 如 func(a,b)，将a，b作为数组记录
                    m_function_struct = re.split(r'[(,)]', m_row_struct[m_nRowPos])
                    # 特殊替换本地标识符:1， :1表示=>前面的内容
                    for pos in range(1, len(m_function_struct)):
                        if m_function_struct[pos] == ":1":
                            m_function_struct[pos] = m_SearchedKey

                    # 执行替换函数
                    if len(m_function_struct) <= 1:
                        raise TestCliException("[WARNING] Invalid env macro, use env(). "
                                               "[" + str(p_Key) + "=>" + str(p_Value) + "]")
                    else:
                        m_row_struct[m_nRowPos] = self.ReplaceMacro_Env(m_function_struct[1:])

                if re.search(r'random(.*)', m_row_struct[m_nRowPos], re.IGNORECASE):
                    # 函数的参数处理，即函数的参数可能包含， 如 func(a,b)，将a，b作为数组记录
                    m_function_struct = re.split(r'[(,)]', m_row_struct[m_nRowPos])
                    # 特殊替换本地标识符:1， :1表示=>前面的内容
                    for pos in range(1, len(m_function_struct)):
                        if m_function_struct[pos] == ":1":
                            m_function_struct[pos] = m_SearchedKey
                    # 执行替换函数
                    if len(m_function_struct) <= 1:
                        raise TestCliException("[WARNING] Invalid random macro, use random(). "
                                               "[" + str(p_Key) + "=>" + str(p_Value) + "]")
                    else:
                        m_row_struct[m_nRowPos] = self.ReplaceMacro_Random(m_function_struct[1:])

            # 重新拼接字符串
            m_Value = None
            for m_nRowPos in range(0, len(m_row_struct)):
                if m_Value is None:
                    m_Value = m_row_struct[m_nRowPos]
                else:
                    m_Value = m_Value + str(m_row_struct[m_nRowPos])

        try:
            m_ResultSQL = re.sub(p_Key, m_Value, p_szSQL, flags=re.DOTALL)
        except re.error as ex:
            raise TestCliException("[WARNING] Invalid regex pattern in ReplaceSQL. "
                                   "[" + str(p_Key) + "]:[" + m_Value + "]:[" + p_szSQL + "]  " + repr(ex))
        return m_ResultSQL

    def RewriteSQL(self, p_szTestScriptFileName, p_szSQL):
        # 检查是否存在sql mapping文件
        if len(self.m_SQL_MappingList) == 0:
            return p_szSQL

        # 获得绝对文件名
        if p_szTestScriptFileName is not None:
            m_TestScriptFileName = os.path.basename(p_szTestScriptFileName)
        else:
            # 用户从Console上启动，没有脚本文件名
            m_TestScriptFileName = "Console"

        # 检查文件名是否匹配
        # 如果一个字符串在多个匹配规则中出现，可能被多次匹配。后一次匹配的依据是前一次匹配的结果
        m_New_SQL = p_szSQL
        for m_MappingFiles in self.m_SQL_MappingList:                           # 所有的SQL Mapping信息
            m_MappingFile_Contents = self.m_SQL_MappingList[m_MappingFiles]     # 具体的一个SQL Mapping文件
            for m_Mapping_Contents in m_MappingFile_Contents:                   # 具体的一个映射信息
                try:
                    if re.match(m_Mapping_Contents[0], m_TestScriptFileName):       # 文件名匹配
                        for (m_Key, m_Value) in m_Mapping_Contents[1]:              # 内容遍历
                            try:
                                m_New_SQL = self.ReplaceSQL(m_New_SQL, m_Key, m_Value)
                            except re.error:
                                raise TestCliException("[WARNING] Invalid regex pattern in ReplaceSQL. ")
                except re.error as ex:
                    raise TestCliException("[WARNING] Invalid regex pattern in filename match. "
                                           "[" + str(m_Mapping_Contents[0]) + "]:[" + m_TestScriptFileName +
                                           "]:[" + m_MappingFiles + "]  " + repr(ex))
        return m_New_SQL


def SQLFormatWithPrefix(p_szCommentSQLScript, p_szOutputPrefix=""):
    # 如果是完全空行的内容，则跳过
    if len(p_szCommentSQLScript) == 0:
        return None

    # 把所有的SQL换行, 第一行加入[SQL >]， 随后加入[   >]
    formattedString = None
    commentSQLLists = p_szCommentSQLScript.split('\n')
    if len(p_szCommentSQLScript) >= 1:
        # 如果原来的内容最后一个字符就是回车换行符，split函数会在后面补一个换行符，这里要去掉，否则前端显示就会多一个空格
        if p_szCommentSQLScript[-1] == "\n":
            del commentSQLLists[-1]

    # 去掉语句列表最后的空行
    while True:
        if len(commentSQLLists) >= 1:
            if len(commentSQLLists[-1]) == 0:
                del commentSQLLists[-1]
            else:
                break
        else:
            break

    # 拼接字符串
    bSQLPrefix = 'SQL> '
    for pos in range(0, len(commentSQLLists)):
        if pos == 0:
            formattedString = p_szOutputPrefix + bSQLPrefix + commentSQLLists[pos]
        else:
            formattedString = formattedString + '\n' + p_szOutputPrefix + bSQLPrefix + commentSQLLists[pos]
        if len(commentSQLLists[pos].strip()) != 0:
            bSQLPrefix = '   > '
    return formattedString


def SQLAnalyze(sqlCommandPlainText, defaultNameSpace="SQL"):
    """ 分析SQL语句，返回如下内容：
        MulitLineSQLHint                该SQL是否为完整SQL， True：完成， False：不完整，需要用户继续输入
        SQLSplitResults                 包含所有SQL信息的一个数组，每一个SQL作为一个元素
        SQLSplitResultsWithComments     包含注释信息的SQL语句信息，数组长度和SQLSplitResults相同
        SQLHints                        SQL的其他各种标志信息，根据SQLSplitResultsWithComments中的注释内容解析获得
    """
    stream = InputStream(sqlCommandPlainText)
    lexer = ClientLexer(stream)
    lexer.removeErrorListeners()
    lexer_listener = ClientErrorListener()
    lexer.addErrorListener(lexer_listener)

    token = CommonTokenStream(lexer)
    parser = ClientParser(token)
    parser.removeErrorListeners()
    parser_listener = ClientErrorListener()
    parser.addErrorListener(parser_listener)
    tree = parser.prog()

    visitor = ClientVisitor(token, defaultNameSpace)
    (isFinished, parsedObjects, originScripts, hints, errorCode, errorMsg) = visitor.visit(tree)

    return isFinished, parsedObjects, sqlCommandPlainText, hints, errorCode, errorMsg
