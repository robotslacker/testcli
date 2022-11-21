# -*- coding: utf-8 -*-
import os
import re
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
                           compareAlgorithm='MYERS'):
        if not os.path.isfile(file1):
            raise DiffException('ERROR: %s is not a file' % file1)
        if not os.path.isfile(file2):
            raise DiffException('ERROR: %s is not a file' % file2)

        # 将比较文件加载到数组
        fileRaw = open(file1, mode='r', encoding=CompareWorkEncoding)
        refFileRaw = open(file2, mode='r', encoding=CompareRefEncoding)
        workFile = open(file1, mode='r', encoding=CompareWorkEncoding)
        refFile = open(file2, mode='r', encoding=CompareRefEncoding)
        fileRawContent = fileRaw.readlines()
        refFileRawContent = refFileRaw.readlines()
        workFileContent = workFile.readlines()
        refFileContent = refFile.readlines()

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
                        if re.search(m_SQLMaskPattern, refFileContent[m_nPos], re.IGNORECASE) is not None:
                            refFileContent[m_nPos] = \
                                re.sub(m_SQLMaskPattern, m_SQLMaskTarget, refFileContent[m_nPos], flags=re.IGNORECASE)
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
                        if re.search(m_SQLMaskPattern, workFileContent[m_nPos], re.IGNORECASE) is not None:
                            workFileContent[m_nPos] = \
                                re.sub(m_SQLMaskPattern, m_SQLMaskTarget, workFileContent[m_nPos], flags=re.IGNORECASE)
                    else:
                        print("LogMask Hint Error, missed =>: [" + pattern + "]")
                m_nPos = m_nPos + 1

        # 输出两个信息
        # 1：  Compare的结果是否存在dif，True/False
        # 2:   Compare的Dif列表. 注意：LCS算法是一个翻转的列表. MYERS算法里头是一个正序列表
        if compareAlgorithm == "MYERS":
            (m_CompareResult, m_CompareResultList) = self.compareMyers(workFileContent, refFileContent, lineno1,
                                                                       lineno2,
                                                                       p_compare_maskEnabled=CompareWithMask,
                                                                       p_compare_ignoreCase=CompareIgnoreCase)
        else:
            (m_CompareResult, m_CompareResultList) = self.compareLCS(workFileContent, refFileContent, lineno1, lineno2,
                                                                     p_compare_maskEnabled=CompareWithMask,
                                                                     p_compare_ignoreCase=CompareIgnoreCase)
            # 翻转数组
            m_CompareResultList = m_CompareResultList[::-1]
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
                # 关闭打开的文件
                if fileRaw:
                    fileRaw.close()
                if refFileRaw:
                    refFileRaw.close()
                if workFile:
                    workFile.close()
                if refFile:
                    refFile.close()
                raise DiffException("Missed line number. Bad compare result. [" + row + "]")

        # 关闭打开的文件
        if fileRaw:
            fileRaw.close()
        if refFileRaw:
            refFileRaw.close()
        if workFile:
            workFile.close()
        if refFile:
            refFile.close()
        return m_CompareResult, m_NewCompareResultList
