# -*- coding: utf-8 -*-
import re
import os
import shlex
from .datawrapper import random_ascii_letters_and_digits
from .testcliexception import TestCliException


class CmdMapping(object):
    # MappingList = { Mapping_Name : Mapping_Contents}
    # Mapping_Contents = [ filename_pattern, match_roles[] ]
    # match_roles = [ Key, Value]
    commandMappingList = {}

    def loadCommandMappings(self, commandScriptFileName, commandMappings):
        # 如果不带任何参数，或者参数为空，则清空CommandMapping信息
        if commandMappings is None:
            self.commandMappingList = {}
            return

        commandMappings = shlex.shlex(commandMappings)
        commandMappings.whitespace = ','
        commandMappings.quotes = "'"
        commandMappings.whitespace_split = True

        # 如果没有传递脚本名称，则认为是在Console中执行
        if commandScriptFileName is None:
            m_szTestScriptFileName = "Console"
        else:
            m_szTestScriptFileName = commandScriptFileName

        # 循环处理每一个Mapping信息
        for commandMappingFile in list(commandMappings):
            commandMappingBaseName = None
            commandMappingFullName = None

            if os.path.isfile(commandMappingFile):
                # 用户提供的是全路径名
                commandMappingBaseName = os.path.basename(commandMappingFile)  # 不包含路径的文件名
                commandMappingFullName = os.path.abspath(commandMappingFile)
            elif os.path.isfile(os.path.join(
                    os.path.dirname(m_szTestScriptFileName),
                    commandMappingFile)):
                # 用户提供的是当前目录下的文件
                commandMappingBaseName = os.path.basename(commandMappingFile)  # 不包含路径的文件名
                commandMappingFullName = os.path.join(
                    os.path.dirname(m_szTestScriptFileName), commandMappingFile)
            elif os.path.isfile(os.path.join(
                    os.path.dirname(m_szTestScriptFileName),
                    commandMappingFile + ".map")):
                # 用户提供的是当前目录下的文件
                commandMappingBaseName = os.path.basename(commandMappingFile)  # 不包含路径的文件名
                commandMappingFullName = os.path.join(
                    os.path.dirname(m_szTestScriptFileName),
                    commandMappingFile + ".map")
            if commandMappingFullName is None or commandMappingBaseName is None:
                # 压根没有找到这个文件
                if "TESTCLI_DEBUG" in os.environ:
                    print("TestCli-003::  Mapping file [" + commandMappingFile + "] not found.")
                continue

            # 加载配置文件
            if "TESTCLI_DEBUG" in os.environ:
                print("Loading ... [" + commandMappingFullName + "]")
            with open(commandMappingFullName, 'r') as f:
                commandMappingContents = f.readlines()

            # 去掉配置文件中的注释信息, 包含空行，单行完全注释，以及文件行内注释的注释部分
            pos = 0
            while pos < len(commandMappingContents):
                if (commandMappingContents[pos].startswith('#') and
                    not commandMappingContents[pos].startswith('#.')) or \
                        len(commandMappingContents[pos]) == 0:
                    commandMappingContents.pop(pos)
                else:
                    pos = pos + 1
            for pos in range(0, len(commandMappingContents)):
                if commandMappingContents[pos].find('#') != -1 and \
                        not commandMappingContents[pos].startswith('#.'):
                    commandMappingContents[pos] = \
                        commandMappingContents[pos][0:commandMappingContents[pos].find('#')]

            # 分段加载配置文件
            m_inSection = False
            m_szNamePattern = None
            m_szMatchRules = []
            m_szFileMatchRules = []
            for m_szLine in commandMappingContents:
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
            self.commandMappingList[commandMappingBaseName] = m_szFileMatchRules

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

    def ReplaceCommand(self, command, key, value):
        # 首先查找是否有匹配的内容，如果没有，直接返回
        try:
            m_SearchResult = re.search(key, command, re.DOTALL)
        except re.error as ex:
            raise TestCliException("[WARNING] Invalid regex pattern. [" + str(key) + "]  " + repr(ex))

        if m_SearchResult is None:
            return command
        else:
            # 记录匹配到的内容
            m_SearchedKey = m_SearchResult.group()

        # 将内容用{}来进行分割，以处理各种内置的函数，如env等
        m_row_struct = re.split('[{}]', value)
        if len(m_row_struct) == 1:
            # 没有任何内置的函数， 直接替换掉结果就可以了
            m_Value = value
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
                                               "[" + str(key) + "=>" + str(value) + "]")
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
                                               "[" + str(key) + "=>" + str(value) + "]")
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
            resultCommand = re.sub(key, m_Value, command, flags=re.DOTALL)
        except re.error as ex:
            raise TestCliException("[WARNING] Invalid regex pattern in ReplaceCommand. "
                                   "[" + str(key) + "]:[" + m_Value + "]:[" + command + "]  " + repr(ex))
        return resultCommand

    def RewriteCommand(self, commandScriptFileName, command):
        # 检查是否存在command mapping文件
        if len(self.commandMappingList) == 0:
            return command

        # 获得绝对文件名
        if commandScriptFileName is not None:
            commandScriptFileName = os.path.basename(commandScriptFileName)
        else:
            # 用户从Console上启动，没有脚本文件名
            commandScriptFileName = "Console"

        # 检查文件名是否匹配
        # 如果一个字符串在多个匹配规则中出现，可能被多次匹配。后一次匹配的依据是前一次匹配的结果
        newCommand = command
        for mappingFiles in self.commandMappingList:                          # 所有的Command Mapping信息
            mappingFileContents = self.commandMappingList[mappingFiles]    # 具体的一个Command Mapping文件
            for mappingContents in mappingFileContents:                      # 具体的一个映射信息
                try:
                    if re.match(mappingContents[0], commandScriptFileName):     # 文件名匹配
                        for (key, value) in mappingContents[1]:             # 内容遍历
                            try:
                                newCommand = self.ReplaceCommand(newCommand, key, value)
                            except re.error:
                                raise TestCliException("[WARNING] Invalid regex pattern in ReplaceCommand. ")
                except re.error as ex:
                    raise TestCliException("[WARNING] Invalid regex pattern in filename match. "
                                           "[" + str(mappingContents[0]) + "]:[" + commandScriptFileName +
                                           "]:[" + mappingFiles + "]  " + repr(ex))
        return newCommand
