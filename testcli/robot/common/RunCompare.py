# -*- coding: UTF-8 -*-
import os
import platform
import re
import json
import random
import html
import sqlite3
from shutil import copyfile, SameFileError
from robot.api import logger
from difflib import SequenceMatcher
from robot.errors import ExecutionFailed
from robot.running.context import EXECUTION_CONTEXTS
from collections import namedtuple


class DiffException(Exception):
    def __init__(self, message):
        Exception.__init__(self)
        self.message = message


class POSIXCompare:
    CompiledRegexPattern = {}
    ErrorRegexPattern = []

    # These define the structure of the history, and correspond to diff output with
    # lines that start with a space, a + and a - respectively.
    Keep = namedtuple('Keep', ['line', 'lineno'])
    Insert = namedtuple('Insert', ['line', 'lineno'])
    Remove = namedtuple('Remove', ['line', 'lineno'])
    # See frontier in myers_diff
    Frontier = namedtuple('Frontier', ['x', 'history'])

    def __init__(self):
        pass

    # 正则表达比较两个字符串
    # p_str1                  原字符串
    # p_str2                  正则表达式
    # p_compare_maskEnabled   是否按照正则表达式来判断是否相等
    # p_compare_ignoreCase    是否忽略匹配中的大小写
    def compare_string(self, p_str1, p_str2,
                       p_compare_maskEnabled=False,
                       p_compare_ignoreCase=False):
        # 如果两个字符串完全相等，直接返回
        if p_str1 == p_str2:
            return True

        # 如果忽略大小写的情况下，两个字符串的大写相同，则直接返回
        if p_compare_ignoreCase:
            if p_str1.upper() == p_str2.upper():
                return True

        # 如果没有启用正则，则直接返回不相等
        if not p_compare_maskEnabled:
            return False

        # 用正则判断表达式是否相等
        try:
            # 对正则表达式进行预先编译
            if p_str2 in self.CompiledRegexPattern:
                m_CompiledPattern = self.CompiledRegexPattern[p_str2]
            else:
                # 如果之前编译过，且没有编译成功，不再尝试编译，直接判断不匹配
                if p_str2 in self.ErrorRegexPattern:
                    return False
                # 如果字符串内容不包含特定的正则字符，则直接失败，不再尝试编译
                # 如何快速判断？
                # 正则编译
                if p_compare_ignoreCase:
                    m_CompiledPattern = re.compile(p_str2, re.IGNORECASE)
                else:
                    m_CompiledPattern = re.compile(p_str2)
                self.CompiledRegexPattern[p_str2] = m_CompiledPattern
            matchObj = re.match(m_CompiledPattern, p_str1)
            if matchObj is None:
                return False
            elif str(matchObj.group()) != p_str1:
                return False
            else:
                return True
        except re.error:
            self.ErrorRegexPattern.append(p_str2)
            # 正则表达式错误，可能是由于这并非是一个正则表达式
            return False

    def compareMyers(self,
                     a_lines,
                     b_lines,
                     a_lineno,
                     b_lineno,
                     p_compare_maskEnabled=False,
                     p_compare_ignoreCase=False):
        # This marks the farthest-right point along each diagonal in the edit
        # graph, along with the history that got it there
        frontier = {1: self.Frontier(0, [])}

        history = []
        a_max = len(a_lines)
        b_max = len(b_lines)
        finished = False
        for d in range(0, a_max + b_max + 1):
            for k in range(-d, d + 1, 2):
                # This determines whether our next search point will be going down
                # in the edit graph, or to the right.
                #
                # The intuition for this is that we should go down if we're on the
                # left edge (k == -d) to make sure that the left edge is fully
                # explored.
                #
                # If we aren't on the top (k != d), then only go down if going down
                # would take us to territory that hasn't sufficiently been explored
                # yet.
                go_down = (k == -d or (k != d and frontier[k - 1].x < frontier[k + 1].x))

                # Figure out the starting point of this iteration. The diagonal
                # offsets come from the geometry of the edit grid - if you're going
                # down, your diagonal is lower, and if you're going right, your
                # diagonal is higher.
                if go_down:
                    old_x, history = frontier[k + 1]
                    x = old_x
                else:
                    old_x, history = frontier[k - 1]
                    x = old_x + 1

                # We want to avoid modifying the old history, since some other step
                # may decide to use it.
                history = history[:]
                y = x - k

                # We start at the invalid point (0, 0) - we should only start building
                # up history when we move off of it.
                if 1 <= y <= b_max and go_down:
                    history.append(self.Insert(b_lines[y - 1], b_lineno[y - 1]))
                elif 1 <= x <= a_max:
                    history.append(self.Remove(a_lines[x - 1], a_lineno[x - 1]))

                # Chew up as many diagonal moves as we can - these correspond to common lines,
                # and they're considered "free" by the algorithm because we want to maximize
                # the number of these in the output.
                while x < a_max and y < b_max and \
                        self.compare_string(a_lines[x], b_lines[y],
                                            p_compare_maskEnabled=p_compare_maskEnabled,
                                            p_compare_ignoreCase=p_compare_ignoreCase):
                    x += 1
                    y += 1
                    history.append(self.Keep(a_lines[x - 1], a_lineno[x - 1]))

                if x >= a_max and y >= b_max:
                    # If we're here, then we've traversed through the bottom-left corner,
                    # and are done.
                    finished = True
                    break
                else:
                    frontier[k] = self.Frontier(x, history)
            if finished:
                break
        compareResult = True
        compareDiffResult = []
        for elem in history:
            if isinstance(elem, self.Keep):
                compareDiffResult.append(" {:>{}} ".format(elem.lineno, 6) + elem.line)
            elif isinstance(elem, self.Insert):
                compareResult = False
                compareDiffResult.append("+{:>{}} ".format(elem.lineno, 6) + elem.line)
            else:
                compareResult = False
                compareDiffResult.append("-{:>{}} ".format(elem.lineno, 6) + elem.line)

        return compareResult, compareDiffResult

    @staticmethod
    def compareDiffLib(x,
                       y,
                       linenox,
                       linenoy
                       ):
        compareResult = True
        compareDiffResult = []
        for group in SequenceMatcher(None, x, y).get_grouped_opcodes(3):
            for tag, i1, i2, j1, j2 in group:
                if tag == 'equal':
                    # 内容完全相同，标记的行号为日志文件的行号
                    for nPos in range(i1, i2):
                        compareDiffResult.append(" {:>{}} ".format(linenox[nPos], 6) + x[nPos])
                    continue
                if tag in {'replace', 'delete'}:
                    # 当前日志有，但是参考日志中没有
                    compareResult = False
                    for nPos in range(i1, i2):
                        compareDiffResult.append("-{:>{}} ".format(linenox[nPos], 6) + x[nPos])
                if tag in {'replace', 'insert'}:
                    # 当前日志没有，但是参考日志中有
                    compareResult = False
                    for nPos in range(j1, j2):
                        compareDiffResult.append("+{:>{}} ".format(linenoy[nPos], 6) + y[nPos])
        return compareResult, compareDiffResult

    def compareLCS(self,
                   x,
                   y,
                   linenox,
                   linenoy,
                   p_compare_maskEnabled=False,
                   p_compare_ignoreCase=False):
        # LCS问题就是求两个字符串最长公共子串的问题。
        # 解法就是用一个矩阵来记录两个字符串中所有位置的两个字符之间的匹配情况，若是匹配则为1，否则为0。
        # 然后求出对角线最长的1序列，其对应的位置就是最长匹配子串的位置。

        # c           LCS数组
        # x           源数据
        # y           目的数据
        # linenox     源数据行数信息
        # linenoy     目的数据行数信息
        # i           源数据长度
        # j           目的数据长度
        # p_result    比对结果
        next_x = x
        next_y = y
        next_i = len(x) - 1
        next_j = len(y) - 1

        # This is our matrix comprised of list of lists.
        # We allocate extra row and column with zeroes for the base case of empty
        # sequence. Extra row and column is appended to the end and exploit
        # Python's ability of negative indices: x[-1] is the last elem.
        # 构建LCS数组
        c = [[0 for _ in range(len(y) + 1)] for _ in range(len(x) + 1)]
        for i, xi in enumerate(x):
            for j, yj in enumerate(y):
                if self.compare_string(xi, yj,
                                       p_compare_maskEnabled, p_compare_ignoreCase):
                    c[i][j] = 1 + c[i - 1][j - 1]
                else:
                    c[i][j] = max(c[i][j - 1], c[i - 1][j])

        # 开始比较
        compare_result = True
        m_CompareDiffResult = []
        while True:
            if next_i < 0 and next_j < 0:
                break
            elif next_i < 0:
                compare_result = False
                m_CompareDiffResult.append("+{:>{}} ".format(linenoy[next_j], 6) + next_y[next_j])
                next_j = next_j - 1
            elif next_j < 0:
                compare_result = False
                m_CompareDiffResult.append("-{:>{}} ".format(linenox[next_i], 6) + next_x[next_i])
                next_i = next_i - 1
            elif self.compare_string(next_x[next_i], next_y[next_j],
                                     p_compare_maskEnabled, p_compare_ignoreCase):
                m_CompareDiffResult.append(" {:>{}} ".format(linenox[next_i], 6) + next_x[next_i])
                next_i = next_i - 1
                next_j = next_j - 1
            elif c[next_i][next_j - 1] >= c[next_i - 1][next_j]:
                compare_result = False
                m_CompareDiffResult.append("+{:>{}} ".format(linenoy[next_j], 6) + next_y[next_j])
                next_j = next_j - 1
            elif c[next_i][next_j - 1] < c[next_i - 1][next_j]:
                compare_result = False
                m_CompareDiffResult.append("-{:>{}} ".format(linenox[next_i], 6) + next_x[next_i])
                next_i = next_i - 1
        return compare_result, m_CompareDiffResult

    def compare_text_files(self, file1, file2,
                           skipLines=None,
                           maskLines=None,
                           ignoreEmptyLine=False,
                           CompareWithMask=None,
                           CompareIgnoreCase=False,
                           CompareIgnoreTailOrHeadBlank=False,
                           CompareWorkEncoding='UTF-8',
                           CompareRefEncoding='UTF-8',
                           compareAlgorithm='AUTO',
                           compareDifflibThreshold=1000
                           ):
        if not os.path.isfile(file1):
            raise DiffException('ERROR: %s is not a file' % file1)
        if not os.path.isfile(file2):
            raise DiffException('ERROR: %s is not a file' % file2)

        # 将比较文件加载到数组
        fileRawContent = open(file1, mode='r', encoding=CompareWorkEncoding).readlines()
        refFileRawContent = open(file2, mode='r', encoding=CompareRefEncoding).readlines()

        workFileContent = open(file1, mode='r', encoding=CompareWorkEncoding).readlines()
        refFileContent = open(file2, mode='r', encoding=CompareRefEncoding).readlines()

        # linno用来记录行号，在最后输出打印的时候，显示的是原始文件信息，而不是修正后的信息
        lineno1 = []
        lineno2 = []
        for m_nPos in range(0, len(workFileContent)):
            lineno1.append(m_nPos + 1)
        for m_nPos in range(0, len(refFileContent)):
            lineno2.append(m_nPos + 1)

        # 去掉filecontent中的回车换行
        for m_nPos in range(0, len(workFileContent)):
            if workFileContent[m_nPos].endswith('\n'):
                workFileContent[m_nPos] = workFileContent[m_nPos][:-1]
        for m_nPos in range(0, len(refFileContent)):
            if refFileContent[m_nPos].endswith('\n'):
                refFileContent[m_nPos] = refFileContent[m_nPos][:-1]

        # 去掉fileconent中的首尾空格
        if CompareIgnoreTailOrHeadBlank:
            for m_nPos in range(0, len(workFileContent)):
                workFileContent[m_nPos] = workFileContent[m_nPos].lstrip().rstrip()
            for m_nPos in range(0, len(refFileContent)):
                refFileContent[m_nPos] = refFileContent[m_nPos].lstrip().rstrip()

        # 去除在SkipLine里头的所有内容
        if skipLines is not None:
            m_nPos = 0
            while m_nPos < len(workFileContent):
                bMatch = False
                for pattern in skipLines:
                    if self.compare_string(workFileContent[m_nPos], pattern,
                                           p_compare_maskEnabled=True,
                                           p_compare_ignoreCase=True):
                        workFileContent.pop(m_nPos)
                        lineno1.pop(m_nPos)
                        bMatch = True
                        break
                if not bMatch:
                    m_nPos = m_nPos + 1

            m_nPos = 0
            while m_nPos < len(refFileContent):
                bMatch = False
                for pattern in skipLines:
                    if self.compare_string(refFileContent[m_nPos], pattern,
                                           p_compare_maskEnabled=True,
                                           p_compare_ignoreCase=True):
                        refFileContent.pop(m_nPos)
                        lineno2.pop(m_nPos)
                        bMatch = True
                        break
                if not bMatch:
                    m_nPos = m_nPos + 1

        # 去除所有的空行
        if ignoreEmptyLine:
            m_nPos = 0
            while m_nPos < len(workFileContent):
                if len(workFileContent[m_nPos].strip()) == 0:
                    workFileContent.pop(m_nPos)
                    lineno1.pop(m_nPos)
                else:
                    m_nPos = m_nPos + 1
            m_nPos = 0
            while m_nPos < len(refFileContent):
                if len(refFileContent[m_nPos].strip()) == 0:
                    refFileContent.pop(m_nPos)
                    lineno2.pop(m_nPos)
                else:
                    m_nPos = m_nPos + 1

        # 处理MaskLine中的信息，对ref, Work文件进行替换
        if maskLines is not None:
            m_nPos = 0
            while m_nPos < len(refFileContent):
                for pattern in maskLines:
                    m_SQLMask = pattern.split("=>")
                    if len(m_SQLMask) == 2:
                        m_SQLMaskPattern = m_SQLMask[0]
                        m_SQLMaskTarget = m_SQLMask[1]
                        try:
                            if re.search(m_SQLMaskPattern, refFileContent[m_nPos], re.IGNORECASE) is not None:
                                refFileContent[m_nPos] = \
                                    re.sub(m_SQLMaskPattern, m_SQLMaskTarget, refFileContent[m_nPos],
                                           flags=re.IGNORECASE)
                        except re.error as rex:
                            print("LogMask Hint Error, rex =>: [" + str(m_SQLMaskPattern) + "::" + str(rex) + "]")
                    else:
                        print("LogMask Hint Error, missed =>: [" + pattern + "]")
                m_nPos = m_nPos + 1
            m_nPos = 0
            while m_nPos < len(workFileContent):
                for pattern in maskLines:
                    m_SQLMask = pattern.split("=>")
                    if len(m_SQLMask) == 2:
                        m_SQLMaskPattern = m_SQLMask[0]
                        m_SQLMaskTarget = m_SQLMask[1]
                        try:
                            if re.search(m_SQLMaskPattern, workFileContent[m_nPos], re.IGNORECASE) is not None:
                                workFileContent[m_nPos] = \
                                    re.sub(m_SQLMaskPattern, m_SQLMaskTarget, workFileContent[m_nPos],
                                           flags=re.IGNORECASE)
                        except re.error as rex:
                            print("LogMask Hint Error, rex =>: [" + str(m_SQLMaskPattern) + "::" + str(rex) + "]")
                    else:
                        print("LogMask Hint Error, missed =>: [" + pattern + "]")
                m_nPos = m_nPos + 1

        # 输出两个信息
        # 1：  Compare的结果是否存在dif，True/False
        # 2:   Compare的Dif列表. 注意：LCS算法是一个翻转的列表. MYERS算法里头是一个正序列表
        if compareAlgorithm == "AUTO":
            if len(workFileContent) > compareDifflibThreshold or len(refFileContent) > compareDifflibThreshold:
                compareAlgorithm = 'DIFFLIB'
            else:
                compareAlgorithm = 'MYERS'
        if compareAlgorithm == "DIFFLIB":
            (m_CompareResult, m_CompareResultList) = self.compareDiffLib(
                workFileContent, refFileContent, lineno1, lineno2)
        elif compareAlgorithm == "MYERS":
            (m_CompareResult, m_CompareResultList) = self.compareMyers(workFileContent, refFileContent, lineno1,
                                                                       lineno2,
                                                                       p_compare_maskEnabled=CompareWithMask,
                                                                       p_compare_ignoreCase=CompareIgnoreCase)
        elif compareAlgorithm == "LCS":
            (m_CompareResult, m_CompareResultList) = self.compareLCS(workFileContent, refFileContent, lineno1, lineno2,
                                                                     p_compare_maskEnabled=CompareWithMask,
                                                                     p_compare_ignoreCase=CompareIgnoreCase)
            # 翻转数组
            m_CompareResultList = m_CompareResultList[::-1]
        else:
            raise ExecutionFailed("Unknown compare algorithm [" + str(compareAlgorithm) + "]", continue_on_failure=True)
        # 随后从数组中补充进入被Skip掉的内容
        m_nWorkLastPos = 0  # 上次Work文件已经遍历到的位置
        m_nRefLastPos = 0  # 上次Ref文件已经遍历到的位置
        m_NewCompareResultList = []
        # 从列表中反向开始遍历， Step=-1
        for row in m_CompareResultList:
            if row.startswith('+'):
                # 当前日志没有，Reference Log中有的
                # 需要注意的是，Ref文件中被跳过的行不会补充进入dif文件
                m_LineNo = int(row[1:7])
                m_AppendLine = "+{:>{}} ".format(m_LineNo, 6) + refFileRawContent[m_LineNo - 1]
                if m_AppendLine.endswith("\n"):
                    m_AppendLine = m_AppendLine[:-1]
                m_NewCompareResultList.append(m_AppendLine)
                m_nRefLastPos = m_LineNo
                continue
            elif row.startswith('-'):
                # 当前日志有，但是Reference里头没有的
                m_LineNo = int(row[1:7])
                # 补充填写那些已经被忽略规则略掉的内容，只填写LOG文件中的对应信息
                if m_LineNo > (m_nWorkLastPos + 1):
                    # 当前日志中存在，但是比较的过程中被Skip掉的内容，要首先补充进来
                    for m_nPos in range(m_nWorkLastPos + 1, m_LineNo):
                        m_AppendLine = "S{:>{}} ".format(m_nPos, 6) + fileRawContent[m_nPos - 1]
                        if m_AppendLine.endswith("\n"):
                            m_AppendLine = m_AppendLine[:-1]
                        m_NewCompareResultList.append(m_AppendLine)
                m_AppendLine = "-{:>{}} ".format(m_LineNo, 6) + fileRawContent[m_LineNo - 1]
                if m_AppendLine.endswith("\n"):
                    m_AppendLine = m_AppendLine[:-1]
                m_NewCompareResultList.append(m_AppendLine)
                m_nWorkLastPos = m_LineNo
                continue
            elif row.startswith(' '):
                # 两边都有的
                m_LineNo = int(row[0:7])
                # 补充填写那些已经被忽略规则略掉的内容，只填写LOG文件中的对应信息
                if m_LineNo > (m_nWorkLastPos + 1):
                    # 当前日志中存在，但是比较的过程中被Skip掉的内容，要首先补充进来
                    for m_nPos in range(m_nWorkLastPos + 1, m_LineNo):
                        m_AppendLine = "S{:>{}} ".format(m_nPos, 6) + fileRawContent[m_nPos - 1]
                        if m_AppendLine.endswith("\n"):
                            m_AppendLine = m_AppendLine[:-1]
                        m_NewCompareResultList.append(m_AppendLine)
                # 完全一样的内容
                m_AppendLine = " {:>{}} ".format(m_LineNo, 6) + fileRawContent[m_LineNo - 1]
                if m_AppendLine.endswith("\n"):
                    m_AppendLine = m_AppendLine[:-1]
                m_NewCompareResultList.append(m_AppendLine)
                m_nWorkLastPos = m_LineNo
                m_nRefLastPos = m_nRefLastPos + 1
                continue
            else:
                raise ExecutionFailed("Missed line number. Bad compare result. [" + row + "]", continue_on_failure=True)
        return m_CompareResult, m_NewCompareResultList


class RunCompare(object):
    # TEST SUITE 在suite中引用，只会实例化一次
    # 也就是说多test case都引用了这个类的方法，但是只有第一个test case调用的时候实例化
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    __skipLines = []  # Compare比较的时候过滤掉相关内容
    __maskLines = []  # Compare比较的时候掩码相关内容
    __BreakWithDifference = False  # 是否在遇到比对错误的时候抛出运行例外
    __EnableConsoleOutPut = False  # 是否关闭在Console上的显示，默认是不关闭
    __IgnoreEmptyLine = False  # 是否在比对的时候忽略空白行
    __compareWithMask = False  # 是否在比对的时候利用正则表达式
    __compareIgnoreCase = False  # 是否再比对的时候忽略大小写
    __compareIgnoreTailOrHeadBlank = False  # 是否忽略对比的前后空格

    __compareWorkEncoding = 'UTF-8'
    __compareDifEncoding = 'UTF-8'
    __compareRefEncoding = 'UTF-8'
    __compareAlgorithm = 'AUTO'  # 默认的Diff算法
    __compareDifflibThreshold = 1000

    def Compare_Ignore_EmptyLine(self, p_IgnoreEmptyLine):
        """ 设置是否在比对的时候忽略空白行  """
        """
        输入参数：
             p_IgnoreEmptyLine:        是否忽略空白行，默认不忽略
        返回值：
            无

        如果设置为True，则仅仅是空白行的差异不作为文件有差异
        如果设置为False，则需要逐行比对
        """
        if str(p_IgnoreEmptyLine).upper() == 'TRUE':
            self.__IgnoreEmptyLine = True

    def Compare_Enable_ConsoleOutput(self, p_ConsoleOutput):
        """ 设置是否在在屏幕上显示Dif文件的内容  """
        """
        输入参数：
             p_ConsoleOutput:        是否在在屏幕上显示Dif文件的内容， 默认是不显示
        返回值：
            无

        如果设置为True， 则所有Dif会显示在控制台上
        如果设置为False，则所有SQL信息不会显示在控制台上
        对于比对文件较大的场景，不建议将比对结果放在控制台上，会导致报告文件过大，而无法查看
        """
        if str(p_ConsoleOutput).upper() == 'TRUE':
            self.__EnableConsoleOutPut = True
        if str(p_ConsoleOutput).upper() == 'FALSE':
            self.__EnableConsoleOutPut = False

    def Compare_Break_When_Difference(self, p_BreakWithDifference):
        """ 设置是否在遇到错误的时候中断该Case的后续运行  """
        """
        输入参数：
             p_BreakWithDifference:        是否在遇到Dif的时候中断，默认为不中断
        返回值：
            无

        如果设置为True，则Case运行会中断，Case会被判断执行失败
        如果设置为False，则Case运行不会中断，但是在运行目录下会生成一个.dif文件，供参考
        """
        if str(p_BreakWithDifference).upper() == 'TRUE':
            self.__BreakWithDifference = True
        if str(p_BreakWithDifference).upper() == 'FALSE':
            self.__BreakWithDifference = False

    def Compare_Not_Skip(self, p_szSkipLine):
        """ 取消是否在比对的时候忽略某些特殊行  """
        """
         输入参数：
              p_szSkipLine:        特殊行的正则表达式
         返回值：
             无

         可以重复执行来确定所有需要忽略的内容
         """

        if p_szSkipLine in self.__skipLines:
            self.__skipLines.remove(p_szSkipLine)

    def Compare_Skip(self, p_szSkipLine):
        """ 设置是否在比对的时候忽略某些特殊行  """
        """
         输入参数：
              p_szSkipLine:        特殊行的正则表达式
         返回值：
             无

         可以重复执行来确定所有需要忽略的内容
         """

        if p_szSkipLine not in self.__skipLines:
            self.__skipLines.append(p_szSkipLine)

    def Compare_Clean_Skip(self):
        """ 清空之前设置的忽略行  """
        """
         输入参数：
             无
         返回值：
             无

         可以重复执行来确定所有需要忽略的内容
         """
        self.__skipLines = []

    def Compare_Not_Mask(self, p_szMaskLine):
        """ 取消是否在比对的时候掩码某些特殊行  """
        """
         输入参数：
              p_szMaskLine:        特殊行的正则表达式
         返回值：
             无

         可以重复执行来确定所有需要掩码的内容
         """

        if p_szMaskLine in self.__maskLines:
            self.__maskLines.remove(p_szMaskLine)

    def Compare_Mask(self, p_szMaskLine):
        """ 设置是否在比对的时候掩码某些特殊行  """
        """
         输入参数：
              p_szMaskLine:        特殊行的正则表达式
         返回值：
             无

         可以重复执行来确定所有需要掩码的内容
         """

        if p_szMaskLine not in self.__maskLines:
            self.__maskLines.append(p_szMaskLine)

    def Compare_Clean_Mask(self):
        """ 清空之前设置的掩码行  """
        """
         输入参数：
             无
         返回值：
             无

         可以重复执行来确定所有需要掩码的内容
         """
        self.__maskLines = []

    def Compare_Algorithm(self, algorithm):
        """ 设置Dif算法， 有LCS和Myers. 在大数据量下Myers明显占据优势  """
        """
         输入参数：
              algorithm:  Dif算法，LCS和Myers，默认是LCS
         返回值：
             无

         """
        self.__compareAlgorithm = str(algorithm).upper().strip()

    def Compare_Difflib_Threshold(self, threshold):
        self.__compareDifflibThreshold = threshold

    def Compare_Enable_Mask(self, p_CompareWithMask):
        """ 设置是否在比对的时候考虑正则表达式  """
        """
         输入参数：
              p_CompareWithMask:        在比对的时候是否考虑正则，默认是不考虑
         返回值：
             无

         """
        if str(p_CompareWithMask).upper() == 'TRUE':
            self.__compareWithMask = True
        if str(p_CompareWithMask).upper() == 'FALSE':
            self.__compareWithMask = False

    def Compare_IgnoreCase(self, p_IgnoreCase):
        """ 设置是否在比对的时候忽略大小写  """
        """
         输入参数：
              p_IgnoreCase:        在比对的时候是否忽略大小写，默认是不忽略
         返回值：
             无

         """
        if str(p_IgnoreCase).upper() == 'TRUE':
            self.__compareIgnoreCase = True
        if str(p_IgnoreCase).upper() == 'FALSE':
            self.__compareIgnoreCase = False

    def Compare_IgnoreTailOrHeadBlank(self, p_IgnoreTailOrHeadBlank):
        """ 设置是否在比对的时候忽略行首和行末的空格  """
        """
         输入参数：
              p_IgnoreTailOrHeadBlank:        在比对的时候是否忽略行首和行末的空格，默认是不忽略
         返回值：
             无

         """
        if str(p_IgnoreTailOrHeadBlank).upper() == 'TRUE':
            self.__compareIgnoreTailOrHeadBlank = True
        if str(p_IgnoreTailOrHeadBlank).upper() == 'FALSE':
            self.__compareIgnoreTailOrHeadBlank = False

    def Compare_SetEncoding(self, encoding):
        """ 设置Compare在工作时候的字符集  """
        """
         输入参数：
              encoding:        Compare在输入时候的默认Encoding
         返回值：
             无
        """
        self.__compareWorkEncoding = encoding
        self.__compareDifEncoding = encoding
        self.__compareRefEncoding = encoding

    def Compare_SetWorkEncoding(self, p_szWorkEncoding):
        """ 设置在读取工作文件时候用到的Encoding  """
        """
         输入参数：
              p_szWorkEncoding:        读取Dif文件时候用到的Encoding
         返回值：
             无
        """
        self.__compareWorkEncoding = p_szWorkEncoding

    def Compare_SetDiffEncoding(self, p_szDifEncoding):
        """ 设置在生成dif文件时候用到的Encoding  """
        """
         输入参数：
              p_szDifEncoding:        生成Dif文件时候用到的Encoding
         返回值：
             无

        """
        self.__compareDifEncoding = p_szDifEncoding

    def Compare_SetRefEncoding(self, p_szRefEncoding):
        """ 设置在读取Ref文件时候用到的Encoding  """
        """
         输入参数：
              p_szRefEncoding:        读取Ref文件时候用到的Encoding
         返回值：
             无

        """
        self.__compareRefEncoding = p_szRefEncoding

    def Compare_Files(self, p_szWorkFile, p_szReferenceFile):
        """ 比较两个文件是否一致  """
        """
        输入参数：
             p_szWorkFile:        需要比对的当前结果文件
             p_szReferenceFile：  需要比对的结果参考文件

        返回值：
            True           比对完成成功
            False          比对中发现了差异

        例外：
            在Compare_Break_With_Difference为True后，若比对发现差异，则抛出例外
        """

        # 检查work文件是否存在，如果存在，则文件是全路径
        if os.path.exists(p_szWorkFile):
            # 传递的是全路径
            (m_WorkFilePath, m_TempFileName) = os.path.split(p_szWorkFile)
            (m_ShortWorkFileName, m_WorkFileExtension) = os.path.splitext(m_TempFileName)
            # 如果定义了T_WORK，则dif文件生成在T_WORK下, 否则生成在当前目录下
            if "T_WORK" in os.environ:
                logFilePath = os.environ["T_WORK"]
            else:
                logFilePath = os.getcwd()
            m_DifFileName = m_ShortWorkFileName + '.dif'
            m_SucFileName = m_ShortWorkFileName + '.suc'
            m_xlogFileName = m_ShortWorkFileName + '.xlog'
            m_xdbFileName = m_ShortWorkFileName + '.xdb'
            m_DifFullFileName = os.path.join(logFilePath, m_DifFileName)
            m_xlogFullFileName = os.path.join(logFilePath, m_xlogFileName)
            m_SucFullFileName = os.path.join(logFilePath, m_SucFileName)
            m_xdbFullFileName = os.path.join(logFilePath, m_xdbFileName)
            m_szWorkFile = p_szWorkFile
        else:
            if "T_WORK" not in os.environ:
                logger.info('===============   work log [' + p_szWorkFile + '] does not exist. ' +
                            ' T_WORK env does not exist too ============')
                if self.__BreakWithDifference:
                    raise ExecutionFailed(
                        message=('===============   work log [' + p_szWorkFile + '] does not exist. ' +
                                 ' T_WORK env does not exist too ============'),
                        continue_on_failure=True
                    )
                return False

            # 传递的不是绝对路径，是相对路径
            (m_ShortWorkFileName, m_WorkFileExtension) = os.path.splitext(p_szWorkFile)
            # 如果定义了T_WORK，则dif文件生成在T_WORK下, 否则生成在当前目录下
            logFilePath = os.environ["T_WORK"]
            m_DifFileName = m_ShortWorkFileName + '.dif'
            m_SucFileName = m_ShortWorkFileName + '.suc'
            m_xlogFileName = m_ShortWorkFileName + '.xlog'
            m_xdbFileName = m_ShortWorkFileName + '.xdb'
            m_DifFullFileName = os.path.join(logFilePath, m_DifFileName)
            m_xlogFullFileName = os.path.join(logFilePath, m_xlogFileName)
            m_SucFullFileName = os.path.join(logFilePath, m_SucFileName)
            m_xdbFullFileName = os.path.join(logFilePath, m_xdbFileName)
            m_szWorkFile = os.path.join(os.environ['T_WORK'], p_szWorkFile)

        # remove old file first
        if os.path.exists(m_DifFullFileName):
            os.remove(m_DifFullFileName)
        if os.path.exists(m_SucFullFileName):
            os.remove(m_SucFullFileName)
        if os.path.exists(m_xlogFullFileName):
            os.remove(m_xlogFullFileName)

        # check if work file exist
        if not os.path.isfile(m_szWorkFile):
            logger.write("  ===== Work file       [" + os.path.abspath(m_szWorkFile) + "] does not exist!")
            m_CompareResultFile = open(m_DifFullFileName, 'w')
            m_CompareResultFile.write(
                '===============   work log [' + p_szWorkFile + '] does not exist ============')
            m_CompareResultFile.close()
            if self.__BreakWithDifference:
                raise ExecutionFailed(
                    message=('===============   work log [' + p_szWorkFile + '] does not exist ============'),
                    continue_on_failure=True
                )
            return False

        m_ReferenceLog = p_szReferenceFile
        if not os.path.isfile(m_ReferenceLog):
            logger.write("  ===== Work file       [" + os.path.abspath(m_szWorkFile) + "]")
            logger.write("  ===== Ref  file       [" + os.path.abspath(m_ReferenceLog) + "]")
            logger.info('===============   reference log [' + m_ReferenceLog +
                        '] does not exist ============')
            m_CompareResultFile = open(m_DifFullFileName, 'w')
            m_CompareResultFile.write('===============   reference log [' + m_ReferenceLog +
                                      '] does not exist ============')
            m_CompareResultFile.close()
            if self.__BreakWithDifference:
                raise ExecutionFailed(
                    message=('===============   reference log [' + m_ReferenceLog + '] does not exist ============'),
                    continue_on_failure=True
                )
            return False

        # 如果定义了T_WORK，复制ref文件到WORK目录下，便于后续比对时候的查看
        try:
            if "T_WORK" in os.environ:
                m_BackupFilePath = os.environ["T_WORK"]
            else:
                m_BackupFilePath = os.getcwd()
            copyfile(os.path.abspath(m_ReferenceLog), os.path.join(m_BackupFilePath, os.path.basename(m_ReferenceLog)))
        except SameFileError:
            logger.info('Fail to backup ref file :: SameFileError [' + os.path.abspath(m_ReferenceLog) + "]")

        # compare file
        m_Comparer = POSIXCompare()
        try:
            (m_CompareResult, m_CompareResultList) = m_Comparer.compare_text_files(
                m_szWorkFile, m_ReferenceLog,
                self.__skipLines,
                self.__maskLines,
                self.__IgnoreEmptyLine,
                self.__compareWithMask,
                self.__compareIgnoreCase,
                self.__compareIgnoreTailOrHeadBlank,
                CompareWorkEncoding=self.__compareWorkEncoding,
                CompareRefEncoding=self.__compareRefEncoding,
                compareAlgorithm=self.__compareAlgorithm,
                compareDifflibThreshold=self.__compareDifflibThreshold
            )
        except DiffException as de:
            logger.info('Fatal Diff Exception:: ' + de.message)
            if self.__BreakWithDifference:
                raise ExecutionFailed(
                    message=('Fatal Diff Exception:: ' + de.message),
                    continue_on_failure=True
                )
            return False

        # 获得Robot的上下文信息
        # 记录所有的TAG信息，MetaData信息
        m_SuiteName = None
        m_TestName = None
        testTags = []
        suiteMetaData = {}
        if EXECUTION_CONTEXTS.current is not None:
            m_SuiteName = str(EXECUTION_CONTEXTS.current.suite)
            if hasattr(EXECUTION_CONTEXTS.current.test, "name"):
                m_TestName = str(EXECUTION_CONTEXTS.current.test.name)
            else:
                m_TestName = "--------"  # Setup Or TearDown
            if hasattr(EXECUTION_CONTEXTS.current.suite, "metadata"):
                suiteMetaData = dict(EXECUTION_CONTEXTS.current.suite.metadata)
            testTags = EXECUTION_CONTEXTS.current.variables.as_dict()["@{TEST_TAGS}"]

        # 读取xdb文件，如果存在（说明文件是用TestCli生成的）
        xdbScenarioElapsedResult = {}
        if os.path.exists(m_xdbFullFileName):
            xlogFileHandle = sqlite3.connect(m_xdbFullFileName)
            cursor = xlogFileHandle.cursor()
            try:
                cursor.execute("SELECT * FROM TestCli_Xlog")
                rs = cursor.fetchall()
                field_names = [i[0] for i in cursor.description]
                cursor.close()
                data = []
                for row in rs:
                    rowMap = {}
                    for i in range(0, len(row)):
                        rowMap[field_names[i]] = row[i]
                    data.append(rowMap)
                for row in data:
                    scenarioId = row["ScenarioId"]
                    if scenarioId is not None:
                        if scenarioId in xdbScenarioElapsedResult.keys():
                            xdbScenarioElapsedResult.update(
                                {
                                    scenarioId: row["Elapsed"] + xdbScenarioElapsedResult[scenarioId]
                                }
                            )
                        else:
                            xdbScenarioElapsedResult[scenarioId] = row["Elapsed"]

            except sqlite3.OperationalError:
                logger.warn("TestCli_Xlog does not exist in extend log.", html=True)
            xlogFileHandle.close()

        # 生成Scenario分析结果
        m_ScenarioStartPos = 0  # 当前Senario开始的位置
        m_ScenarioResults = {}
        m_ScenariosPos = {}

        # 首先记录下来每一个Senario的开始位置，结束位置
        m_nPos = 0
        m_ScenarioName = None
        m_ScenarioId = None
        while True:
            if m_nPos >= len(m_CompareResultList):
                break
            # Scenario定义
            # -- [Hint] setup:
            # -- [setup:]
            # -- [Hint] setup:end:
            # -- [setup:end]

            # -- [Hint] cleanup:
            # -- [cleanup:]
            # -- [Hint] cleanup:end:
            # -- [cleanup:end]

            # -- [Hint] scenario:xxxx:
            # -- [scenario:xxxx]
            # -- [Hint] scenario:id:xxxx:
            # -- [scenario:id:xxxx]
            # -- [Hint] scenario:end:
            # -- [scenario:end]

            matchObj1 = re.search(r"--(\s+)?\[Hint](\s+)?setup:", m_CompareResultList[m_nPos],
                                  re.IGNORECASE | re.DOTALL)
            matchObj2 = re.search(r"--(\s+)?\[(\s+)?setup:", m_CompareResultList[m_nPos],
                                  re.IGNORECASE | re.DOTALL)
            matchObj3 = re.search(r"--(\s+)?\[Hint](\s+)?cleanup:", m_CompareResultList[m_nPos],
                                  re.IGNORECASE | re.DOTALL)
            matchObj4 = re.search(r"--(\s+)?\[(\s+)?cleanup:", m_CompareResultList[m_nPos],
                                  re.IGNORECASE | re.DOTALL)
            if matchObj1 or matchObj2 or matchObj3 or matchObj4:
                # 遇到这些标记，则之前的Scenario结束，记录之前的信息
                if m_ScenarioId is not None:
                    m_ScenariosPos[m_ScenarioId] = {
                        "ScenarioStartPos": m_ScenarioStartPos,
                        "ScenarioEndPos": m_nPos,
                        "ScenarioId": m_ScenarioId,
                        "ScenarioName": m_ScenarioName,
                    }
                m_ScenarioStartPos = m_nPos + 1
                m_nPos = m_nPos + 1
                m_ScenarioName = None
                m_ScenarioId = None
                continue

            matchObj1 = re.search(r"--(\s+)?\[Hint](\s+)?scenario:end", m_CompareResultList[m_nPos],
                                  re.IGNORECASE | re.DOTALL)
            matchObj2 = re.search(r"--(\s+)?\[(\s+)?scenario:end", m_CompareResultList[m_nPos],
                                  re.IGNORECASE | re.DOTALL)
            if matchObj1 or matchObj2:
                # 当前场景结束，记录之前的信息
                if m_ScenarioId is None:
                    m_ScenarioId = str(random.randint(999990001, 999999999))
                    m_ScenarioName = "Unexpected Scenario End at Line: [" + m_CompareResultList[m_nPos] + "]"
                m_ScenariosPos[m_ScenarioId] = {
                    "ScenarioStartPos": m_ScenarioStartPos,
                    "ScenarioEndPos": m_nPos,
                    "ScenarioId": m_ScenarioId,
                    "ScenarioName": m_ScenarioName,
                }
                m_ScenarioStartPos = m_nPos + 1
                m_nPos = m_nPos + 1
                m_ScenarioName = None
                m_ScenarioId = None
                continue

            matchObj1 = re.search(r"--(\s+)?\[Hint](\s+)?Scenario:(.*)", m_CompareResultList[m_nPos],
                                  re.IGNORECASE | re.DOTALL)
            matchObj2 = re.search(r"--(\s+)?\[(\s+)?Scenario:(.*)]", m_CompareResultList[m_nPos],
                                  re.IGNORECASE | re.DOTALL)
            if matchObj1 or matchObj2:
                if m_ScenarioId is not None:
                    # 之前的Scenario有记录，只是忘了Scenario End
                    m_ScenariosPos[m_ScenarioId] = {
                        "ScenarioStartPos": m_ScenarioStartPos,
                        "ScenarioEndPos": m_nPos,
                        "ScenarioId": m_ScenarioId,
                        "ScenarioName": m_ScenarioName,
                    }
                m_SenarioAndId = ""
                if matchObj1:
                    m_SenarioAndId = matchObj1.group(3).strip()
                if matchObj2:
                    m_SenarioAndId = matchObj2.group(3).strip()
                if len(m_SenarioAndId.split(':')) >= 2:
                    # 如果有两个内容， 规则是:Scenario:Id:ScenarioName
                    m_ScenarioId = m_SenarioAndId.split(':')[0].strip()
                    m_ScenarioName = ":".join(m_SenarioAndId.split(':')[1:]).strip()
                    m_ScenarioStartPos = m_nPos
                    m_nPos = m_nPos + 1
                    continue
                else:
                    # 如果只有一个内容， 则scenarioId,scenarioName一样
                    m_ScenarioId = m_ScenarioName = m_SenarioAndId
                    m_nPos = m_nPos + 1
                    continue

            # 不是什么特殊内容，这里是标准文本
            m_nPos = m_nPos + 1

        # 最后一个Senario的情况记录下来
        if m_ScenarioId is not None:
            m_ScenariosPos[m_ScenarioId] = {
                "ScenarioStartPos": m_ScenarioStartPos,
                "ScenarioEndPos": len(m_CompareResultList),
                "ScenarioId": m_ScenarioId,
                "ScenarioName": m_ScenarioName,
            }

        # 遍历每一个Senario的情况
        for m_ScenarioId, m_Senario_Pos in m_ScenariosPos.items():
            m_StartPos = m_Senario_Pos['ScenarioStartPos']
            m_EndPos = m_Senario_Pos['ScenarioEndPos']
            m_ScenarioName = m_Senario_Pos['ScenarioName']
            bFoundDif = False
            m_DifStartPos = 0
            for m_nPos in range(m_StartPos, m_EndPos):
                if m_CompareResultList[m_nPos].startswith('-') or m_CompareResultList[m_nPos].startswith('+'):
                    m_DifStartPos = m_nPos
                    bFoundDif = True
                    break
            if m_ScenarioId in xdbScenarioElapsedResult.keys():
                elapsedTime = xdbScenarioElapsedResult[m_ScenarioId]
            else:
                elapsedTime = 0
            if not bFoundDif:
                m_ScenarioResults[m_ScenarioId] = \
                    {
                        "Status": "PASS",
                        "Name": m_ScenarioName,
                        "message": "",
                        "Id": m_ScenarioId,
                        "Elapsed": elapsedTime
                    }
            else:
                # 错误信息只记录前后20行信息,前5行，多余的不记录
                if m_DifStartPos - 5 > m_StartPos:
                    m_DifStartPos = m_DifStartPos - 5
                else:
                    m_DifStartPos = m_StartPos
                if m_DifStartPos + 20 < m_EndPos:
                    m_DifEndPos = m_DifStartPos + 20
                else:
                    m_DifEndPos = m_EndPos
                m_Message = "\n".join(m_CompareResultList[m_DifStartPos:m_DifEndPos])
                m_ScenarioResults[m_ScenarioId] = \
                    {
                        "Status": "FAIL",
                        "message": m_Message,
                        "Name": m_ScenarioName,
                        "Id": m_ScenarioId,
                        "Elapsed": elapsedTime
                    }

        # 如果没有设置任何Scenario，则将CaseName作为Scenario的名字，统一为一个Scenario
        if len(m_ScenarioResults) == 0:
            if m_CompareResult:
                m_ScenarioResults[m_TestName] = \
                    {
                        "Status": "PASS",
                        "message": "",
                        "Id": -1,
                        "Name": m_TestName,
                        "Elapsed": 0
                    }
            else:
                m_ScenarioResults[m_TestName] = \
                    {
                        "Status": "FAIL",
                        "message": "Test failed.",
                        "Id": -1,
                        "Name": m_TestName,
                        "Elapsed": 0
                    }

        # 遍历所有Scneario的结果，如果全部为SUCCESSFUL，则Case为成功，否则为失败
        m_CompareResult = True
        for m_LineItem in m_CompareResultList:
            if m_LineItem.startswith('-') or m_LineItem.startswith('+'):
                m_CompareResult = False
                break
        if m_CompareResult:
            for m_ScenarioResult in m_ScenarioResults.values():
                if m_ScenarioResult["Status"] == "FAIL":
                    m_CompareResult = False
                    break

        # Scenario的结果记录到xlog文件中
        m_xlogResults = {
            "ScenarioResults": m_ScenarioResults,
            "SuiteName": m_SuiteName,
            "CaseName": m_TestName,
            "CaseTags": testTags,
            "MetaData": suiteMetaData
        }
        with open(m_xlogFullFileName, 'w', encoding=self.__compareDifEncoding) as f:
            json.dump(obj=m_xlogResults, fp=f, indent=4, sort_keys=True, ensure_ascii=False)
        logger.write("======= Generate ext log file [" + m_xlogFullFileName + "]")

        # 生成比较的结果
        if m_CompareResult:
            # 比较完全没有问题
            logger.write("======= Succ file        [" + m_SucFullFileName + "] >>>>> ")
            logger.write("  ===== Work file        [" + os.path.abspath(m_szWorkFile) + "]")
            logger.write("  ===== Ref  file        [" + os.path.abspath(m_ReferenceLog) + "]")
            logger.write("  ===== Mask flag        [" + str(self.__compareWithMask) + "]")
            logger.write("  ===== BlankSpace flag  [" + str(self.__compareIgnoreTailOrHeadBlank) + "]")
            logger.write("  ===== Case flag        [" + str(self.__compareIgnoreCase) + "]")
            logger.write("  ===== Empty line flag  [" + str(self.__IgnoreEmptyLine) + "]")
            for row in self.__skipLines:
                logger.write("  ===== Skip line        [" + str(row) + "]")
            for row in self.__maskLines:
                logger.write("  ===== Mask line        [" + str(row) + "]")
            logger.write("======= Succ file [" + m_SucFullFileName + "] >>>>> ")
            m_CompareResultFile = open(m_SucFullFileName, 'w', encoding=self.__compareDifEncoding)
            print("M       SucFullFileName=" + m_SucFullFileName, file=m_CompareResultFile)
            print("M       WorkFullFileName=" + os.path.abspath(m_szWorkFile), file=m_CompareResultFile)
            print("M       RefFullFileName=" + os.path.abspath(m_ReferenceLog), file=m_CompareResultFile)
            print("M       MaskFlag=" + str(self.__compareWithMask), file=m_CompareResultFile)
            print("M       BlankSpaceFlag=" + str(self.__compareIgnoreTailOrHeadBlank), file=m_CompareResultFile)
            print("M       CaseFlag=" + str(self.__compareIgnoreCase), file=m_CompareResultFile)
            print("M       EmptyLineFlag=" + str(self.__IgnoreEmptyLine), file=m_CompareResultFile)
            for line in m_CompareResultList:
                print(line, file=m_CompareResultFile)
                if self.__EnableConsoleOutPut:
                    if line.startswith('-'):
                        logger.write('<font style="color:Black;background-color:#E0E0E0">' +
                                     html.escape(line[0:7]) + '</font>' +
                                     '<font style="color:white;background-color:Red">' +
                                     html.escape(line[7:]) + '</font>',
                                     html=True)
                    elif line.startswith('+'):
                        logger.write('<font style="color:Black;background-color:#E0E0E0">' +
                                     html.escape(line[0:7]) + '</font>' +
                                     '<font style="color:white;background-color:Green">' +
                                     html.escape(line[7:]) + '</font>',
                                     html=True)
                    elif line.startswith('S'):
                        logger.write('<font style="color:Black;background-color:#E0E0E0">' +
                                     html.escape(line) + '</font>',
                                     html=True)
                    else:
                        logger.write('<font style="color:Black;background-color:#E0E0E0">' +
                                     html.escape(line[0:7]) + '</font>' +
                                     '<font style="color:Black;background-color:white">' +
                                     html.escape(line[7:]) + '</font>',
                                     html=True)
            m_CompareResultFile.close()
            logger.write("======= Succ file  [" + m_SucFullFileName + "] <<<<< ")
        else:
            # 比较存在问题
            logger.write("======= Diff file        [" + m_DifFullFileName + "] >>>>> ")
            logger.write("  ===== Work file        [" + os.path.abspath(m_szWorkFile) + "]")
            logger.write("  ===== Ref  file        [" + os.path.abspath(m_ReferenceLog) + "]")
            if platform.system().lower() == 'windows':
                logger.write("  ===== Patch Command    [copy " + os.path.abspath(m_szWorkFile) + " " +
                             os.path.abspath(m_ReferenceLog) + "]")
            else:
                logger.write("  ===== Patch Command    [cp " + repr(os.path.abspath(m_szWorkFile)) + " " +
                             repr(os.path.abspath(m_ReferenceLog)) + "]")
            logger.write("  ===== EnableMask       [" + str(self.__compareWithMask) + "]")
            logger.write("  ===== IgnoreBlankSpace [" + str(self.__compareIgnoreTailOrHeadBlank) + "]")
            logger.write("  ===== CaseSensitive    [" + str(self.__compareIgnoreCase) + "]")
            logger.write("  ===== IgnoreEmptyLine  [" + str(self.__IgnoreEmptyLine) + "]")
            for row in self.__skipLines:
                logger.write("  ===== Skip line        [" + str(row) + "]")
            for row in self.__maskLines:
                logger.write("  ===== Mask line        [" + str(row) + "]")
            if "TEST_INCLUDEPRIORITIES" in os.environ:
                logger.write("  ===== IncludePriorities [" + str(os.environ["TEST_INCLUDEPRIORITIES"]) + "]")

            # 生成dif文件
            m_CompareResultFile = open(m_DifFullFileName, 'w', encoding=self.__compareDifEncoding)
            print("M       DifFullFileName=" + m_DifFullFileName, file=m_CompareResultFile)
            print("M       WorkFullFileName=" + os.path.abspath(m_szWorkFile), file=m_CompareResultFile)
            print("M       RefFullFileName=" + os.path.abspath(m_ReferenceLog), file=m_CompareResultFile)
            print("M       EnableMask=" + str(self.__compareWithMask), file=m_CompareResultFile)
            print("M       IgnoreBlankSpace=" + str(self.__compareIgnoreTailOrHeadBlank), file=m_CompareResultFile)
            print("M       CaseSensitive=" + str(self.__compareIgnoreCase), file=m_CompareResultFile)
            print("M       IgnoreEmptyLine=" + str(self.__IgnoreEmptyLine), file=m_CompareResultFile)
            for row in self.__skipLines:
                print("M       SkipLine=" + str(row), file=m_CompareResultFile)
            for row in self.__maskLines:
                print("M       MaskLine=" + str(row), file=m_CompareResultFile)

            for line in m_CompareResultList:
                print(line, file=m_CompareResultFile)
                if self.__EnableConsoleOutPut:
                    if line.startswith('-'):
                        logger.write('<font style="color:Black;background-color:#E0E0E0">' +
                                     html.escape(line[0:7]) + '</font>' +
                                     '<font style="color:white;background-color:Red">' +
                                     html.escape(line[7:]) + '</font>',
                                     html=True)
                    elif line.startswith('+'):
                        logger.write('<font style="color:Black;background-color:#E0E0E0">' +
                                     html.escape(line[0:7]) + '</font>' +
                                     '<font style="color:white;background-color:Green">' +
                                     html.escape(line[7:]) + '</font>',
                                     html=True)
                    elif line.startswith('S'):
                        logger.write('<font style="color:Black;background-color:#E0E0E0">' +
                                     html.escape(line) + '</font>',
                                     html=True)
                    else:
                        logger.write('<font style="color:Black;background-color:#E0E0E0">' +
                                     html.escape(line[0:7]) + '</font>' +
                                     '<font style="color:Black;background-color:white">' +
                                     html.escape(line[7:]) + '</font>',
                                     html=True)
            m_CompareResultFile.close()
            logger.write("======= Dif file [" + m_DifFullFileName + "] <<<<< ")

        # 如果比较失败，返回Robot执行失败的信息
        # 限制： Robot的ExecutionFailed不支持message中的中文字符
        if not m_CompareResult:
            logger.write("======= Diff file [" + m_DifFullFileName + "] <<<<< ")
            if self.__BreakWithDifference:
                m_szErrorMessage = ""
                for m_ScenarioName in m_ScenarioResults:
                    m_szErrorMessage = m_szErrorMessage + "===========>>>>>>>> Scenario: " + m_ScenarioName + "\n"
                    m_szErrorMessage = m_szErrorMessage + str(m_ScenarioResults[m_ScenarioName]["message"]) + "\n"
                raise ExecutionFailed(
                    message="Test failed. Please check dif file for more information.",
                    continue_on_failure=self.__BreakWithDifference
                )
            logger.write("return False. ")
            return False
        else:
            logger.write("return True. ")
            return True

    def Compare_Show_Config(self):
        for m_SkipLine in self.__skipLines:
            print("===> " + m_SkipLine)
