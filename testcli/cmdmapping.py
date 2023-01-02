# -*- coding: utf-8 -*-
import re
import os
import shlex
from .testcliexception import TestCliException


class CmdMapping(object):
    # MappingList = { Mapping_Name : Mapping_Contents}
    # Mapping_Contents = [ filename_pattern, match_roles[] ]
    # match_roles = [ Key, Value]
    commandMappingList = {}

    def loadCommandMappings(self, commandScriptFileName, commandMappings):
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
                raise TestCliException("Mapping file [" + commandMappingFile + "] not found.")

            # 加载配置文件
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
            filePattern = None
            replaceRules = []
            m_szFileMatchRules = []
            for configLine in commandMappingContents:
                configLine = configLine.strip()
                if not m_inSection and configLine.startswith("#.") and configLine.endswith(':'):
                    # 文件注释开始
                    m_inSection = True
                    filePattern = configLine[2:-1].strip()  # 去掉开始的的#.以前最后的:
                    replaceRules = []
                    continue
                if m_inSection and configLine == "#.":
                    # 文件注释结束
                    m_szFileMatchRules.append(
                        {
                            "filePattern": filePattern,
                            "replaceRules": replaceRules
                        }
                    )
                    filePattern = None
                    replaceRules = []
                    m_inSection = False
                    continue
                if m_inSection:
                    # 文件配置段中的内容
                    replaceRuleConfig = configLine.split('=>')
                    if len(replaceRuleConfig) == 2:
                        replaceRuleSrc = replaceRuleConfig[0].strip()
                        replaceRuleDst = replaceRuleConfig[1].strip()
                        replaceRule = {replaceRuleSrc: replaceRuleDst}
                        replaceRules.append(replaceRule)
                    else:
                        if "TESTCLI_DEBUG" in os.environ:
                            raise TestCliException("Replace rule [" + configLine + "] has synatx error. ignore")
                    continue

            # 每个文件的配置都加载到MappingList中
            self.commandMappingList[commandMappingBaseName] = m_szFileMatchRules

    def RewriteWord(self, commandScriptFileName, word):
        # 检查是否存在command mapping文件
        if len(self.commandMappingList) == 0:
            return word

        # 获得绝对文件名
        if commandScriptFileName is not None:
            commandScriptFileName = os.path.basename(commandScriptFileName)
        else:
            # 用户从Console上启动，没有脚本文件名
            commandScriptFileName = "Console"

        # 检查文件名是否匹配
        # 如果一个字符串在多个匹配规则中出现，可能被多次匹配。后一次匹配的依据是前一次匹配的结果
        for mappingFiles in self.commandMappingList.values():                   # 所有的Command Mapping信息
            for mappingFile in mappingFiles:
                try:
                    if re.match(mappingFile["filePattern"], commandScriptFileName):     # 文件名匹配
                        replaceRules = mappingFile["replaceRules"]
                        for replaceRule in replaceRules:
                            if word in replaceRule.keys():
                                word = replaceRule[word]
                            else:
                                for matchKey, matchValue in replaceRule.items():
                                    matchObj = re.match(pattern=matchKey, string=word)
                                    if matchObj:
                                        _, end = matchObj.span()
                                        if end == len(str(word)):
                                            # 正则必须全文匹配
                                            try:
                                                word = re.sub(pattern=matchKey, repl=matchValue,
                                                              string=word, flags=re.DOTALL)
                                            except re.error:
                                                word = matchValue
                except re.error as ex:
                    raise TestCliException("[WARNING] Invalid regex pattern in filePattern match. "
                                           "[" + str(mappingFile["filePattern"]) +
                                           "]:[" + commandScriptFileName + "]  " + repr(ex))
        return word
