# -*- coding: utf-8 -*-
import copy
import os
import re
import warnings
from collections import namedtuple
from difflib import SequenceMatcher
from ..common import rewriteStatement
from ..htmldiff.diffhtmlgenerate import diffHtmlGenerate

# 抑制在比对文件中出现的||,]]等的警告信息
warnings.simplefilter(action='ignore', category=FutureWarning)

# 默认的比较选项
compareDefaultOption = {
    "algorithm": "auto",      # Compare比较算法，有LCS和MYERS
    "output": "console",      # Compare结果输出的位置，默认为输出到控制台
    "mask": False,            # 比较中是否按照正则表达式的方式去比较
    "case": False,            # 比较中是否大小写敏感
    "igblank": False,         # 比较中是否忽略空格
    "trim": False,            # 比较中是否忽略行前行尾的空格
    "workEncoding": "utf-8",  # 工作文件的比对字符集
    "refEncoding": "utf-8",   # 参考文件的比对字符集
}
compareOption = copy.copy(compareDefaultOption)
compareMaskLines = {}        # 比对中进行掩码的内容信息
compareSkipLines = []        # 比对中需要忽略的信息


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
        if compareResult:
            # 文件完全相等
            compareDiffResult.clear()
            for nPos in range(0, len(x)):
                compareDiffResult.append(" {:>{}} ".format(linenox[nPos], 6) + x[nPos])
        return compareResult, compareDiffResult

    def compare_text(self,
                     lines1: list,
                     lines2: list,
                     skipLines: list = None,
                     maskLines: dict = None,
                     ignoreEmptyLine: bool = False,
                     CompareWithMask: bool = True,
                     CompareIgnoreCase: bool = False,
                     CompareIgnoreTailOrHeadBlank: bool = False,
                     compareAlgorithm: str = 'AUTO',
                     compareAlgorithmDiffLibThresHold: int = 1000):

        # 将比较文件加载到数组
        fileRawContent = lines1
        refFileRawContent = lines2
        workFileContent = lines1
        refFileContent = lines2

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
                for m_SQLMaskPattern, m_SQLMaskTarget in maskLines.items():
                    if re.search(m_SQLMaskPattern, refFileContent[m_nPos], re.IGNORECASE) is not None:
                        refFileContent[m_nPos] = \
                            re.sub(m_SQLMaskPattern, m_SQLMaskTarget, refFileContent[m_nPos], flags=re.IGNORECASE)
                m_nPos = m_nPos + 1
            m_nPos = 0
            while m_nPos < len(workFileContent):
                for m_SQLMaskPattern, m_SQLMaskTarget in maskLines.items():
                    if re.search(m_SQLMaskPattern, workFileContent[m_nPos], re.IGNORECASE) is not None:
                        workFileContent[m_nPos] = \
                            re.sub(m_SQLMaskPattern, m_SQLMaskTarget, workFileContent[m_nPos], flags=re.IGNORECASE)
                m_nPos = m_nPos + 1

        # 输出两个信息
        # 1：  Compare的结果是否存在dif，True/False
        # 2:   Compare的Dif列表. 注意：LCS算法是一个翻转的列表. MYERS算法里头是一个正序列表
        useCompareAlgorithm = compareAlgorithm.upper()
        if useCompareAlgorithm == "AUTO":
            if len(lineno1) > compareAlgorithmDiffLibThresHold or len(lineno2) > compareAlgorithmDiffLibThresHold:
                useCompareAlgorithm = "DIFFLIB"
            else:
                useCompareAlgorithm = "MYERS"
        if useCompareAlgorithm == "MYERS":
            (compareResult, compareResultList) = \
                    self.compareMyers(
                        workFileContent, refFileContent,
                        lineno1, lineno2,
                        p_compare_maskEnabled=CompareWithMask,
                        p_compare_ignoreCase=CompareIgnoreCase
                    )
        elif useCompareAlgorithm == "DIFFLIB":
            (compareResult, compareResultList) = \
                self.compareDiffLib(workFileContent, refFileContent, lineno1, lineno2)
        elif useCompareAlgorithm == "LCS":
            (compareResult, compareResultList) = \
                self.compareLCS(workFileContent, refFileContent,
                                lineno1, lineno2,
                                p_compare_maskEnabled=CompareWithMask,
                                p_compare_ignoreCase=CompareIgnoreCase)
            # 翻转数组
            compareResultList = compareResultList[::-1]
        else:
            raise DiffException("Unknown compare algorithm [" + str(useCompareAlgorithm) + "]")

        # 随后从数组中补充进入被Skip掉的内容
        workLastPos = 0  # 上次Work文件已经遍历到的位置
        refLastPos = 0  # 上次Ref文件已经遍历到的位置
        newCompareResultList = []
        # 从列表中反向开始遍历， Step=-1
        for row in compareResultList:
            if row.startswith('+'):
                # 当前日志没有，Reference中有的
                # 需要注意的是，Ref文件中被跳过的行不会补充进入dif文件
                lineno = int(row[1:7])
                appendLine = "+{:>{}} ".format(lineno, 6) + refFileRawContent[lineno - 1]
                if appendLine.endswith("\n"):
                    appendLine = appendLine[:-1]
                newCompareResultList.append(appendLine)
                refLastPos = lineno
                continue
            elif row.startswith('-'):
                # 当前日志有，但是Reference里头没有的
                lineno = int(row[1:7])
                # 补充填写那些已经被忽略规则略掉的内容，只填写LOG文件中的对应信息
                if lineno > (workLastPos + 1):
                    # 当前日志中存在，但是比较的过程中被Skip掉的内容，要首先补充进来
                    for m_nPos in range(workLastPos + 1, lineno):
                        appendLine = "S{:>{}} ".format(m_nPos, 6) + fileRawContent[m_nPos - 1]
                        if appendLine.endswith("\n"):
                            appendLine = appendLine[:-1]
                        newCompareResultList.append(appendLine)
                appendLine = "-{:>{}} ".format(lineno, 6) + fileRawContent[lineno - 1]
                if appendLine.endswith("\n"):
                    appendLine = appendLine[:-1]
                newCompareResultList.append(appendLine)
                workLastPos = lineno
                continue
            elif row.startswith(' '):
                # 两边都有的
                lineno = int(row[0:7])
                # 补充填写那些已经被忽略规则略掉的内容，只填写LOG文件中的对应信息
                if lineno > (workLastPos + 1):
                    # 当前日志中存在，但是比较的过程中被Skip掉的内容，要首先补充进来
                    for m_nPos in range(workLastPos + 1, lineno):
                        appendLine = "S{:>{}} ".format(m_nPos, 6) + fileRawContent[m_nPos - 1]
                        if appendLine.endswith("\n"):
                            appendLine = appendLine[:-1]
                        newCompareResultList.append(appendLine)
                # 完全一样的内容
                appendLine = " {:>{}} ".format(lineno, 6) + fileRawContent[lineno - 1]
                if appendLine.endswith("\n"):
                    appendLine = appendLine[:-1]
                newCompareResultList.append(appendLine)
                workLastPos = lineno
                refLastPos = refLastPos + 1
                continue
            else:
                raise DiffException("Missed line number. Bad compare result. [" + row + "]")

        return compareResult, newCompareResultList

    def compare_text_files(self, file1, file2,
                           skipLines: list = None,
                           maskLines: dict = None,
                           ignoreEmptyLine: bool = False,
                           CompareWithMask: bool = True,
                           CompareIgnoreCase: bool = False,
                           CompareIgnoreTailOrHeadBlank: bool = False,
                           CompareWorkEncoding: str = 'UTF-8',
                           CompareRefEncoding: str = 'UTF-8',
                           compareAlgorithm: str = 'AUTO',
                           compareAlgorithmDiffLibThresHold: int = 1000,
                           ):
        if not os.path.isfile(file1):
            raise DiffException('ERROR: File %s does not exist!' % file1)
        if not os.path.isfile(file2):
            raise DiffException('ERROR: File %s does not exist!' % file2)

        # 将比较文件加载到数组
        filefp1 = open(file1, mode='r', encoding=CompareWorkEncoding)
        filefp2 = open(file2, mode='r', encoding=CompareRefEncoding)

        fileLines1 = filefp1.readlines()
        fileLines2 = filefp2.readlines()
        compareResult, newCompareResultList = self.compare_text(
            lines1=fileLines1,
            lines2=fileLines2,
            skipLines=skipLines,
            maskLines=maskLines,
            ignoreEmptyLine=ignoreEmptyLine,
            CompareWithMask=CompareWithMask,
            CompareIgnoreCase=CompareIgnoreCase,
            CompareIgnoreTailOrHeadBlank=CompareIgnoreTailOrHeadBlank,
            compareAlgorithm=compareAlgorithm,
            compareAlgorithmDiffLibThresHold=compareAlgorithmDiffLibThresHold,
        )
        # 关闭打开的文件
        if filefp1:
            filefp1.close()
        if filefp2:
            filefp2.close()
        return compareResult, newCompareResultList


def executeCompareRequest(cls, requestObject, commandScriptFile: str):
    global compareOption
    global compareDefaultOption
    global compareMaskLines
    global compareSkipLines

    action = str(requestObject["action"])
    if action == "set":
        if len(requestObject["compareOptions"]) == 0:
            # 如果Compare Set后面没有跟任何参数，则将当前Compare的配置打印出来
            currentCompareSettings = []
            for key, value in compareOption.items():
                currentCompareSettings.append(
                    [str(key), str(value), str(compareDefaultOption[key])])
            yield {
                "type": "result",
                "title": "Current compare settings:",
                "rows": currentCompareSettings,
                "headers": ["Option", "Current value", "Default value"],
                "columnTypes": None,
                "status": None
            }
            currentSkipSettings = []
            for skipline in compareSkipLines:
                currentSkipSettings.append([skipline])
            if len(currentSkipSettings) != 0:
                yield {
                    "type": "result",
                    "title": "Skiplines:",
                    "rows": currentSkipSettings,
                    "headers": ["SkipPattern"],
                    "columnTypes": None,
                    "status": None
                }
            currentMaskSettings = []
            for key, value in compareMaskLines.items():
                currentMaskSettings.append([str(key), str(value)])
            if len(currentMaskSettings) != 0:
                yield {
                    "type": "result",
                    "title": "Masklines:",
                    "rows": currentMaskSettings,
                    "headers": ["SourcePattern", "TargetPattern"],
                    "columnTypes": None,
                    "status": None
                }
        else:  # compareOptions不为空，即命令中指定了选项
            # 设置Compare的选项
            for key, value in requestObject["compareOptions"].items():
                if key in compareOption:
                    compareOption[key] = value
                else:
                    yield {
                        "type": "error",
                        "message": "unknown compare option [" + str(key) + "]"
                    }
            yield {
                "type": "result",
                "title": None,
                "rows": None,
                "headers": None,
                "columnTypes": None,
                "status": None
            }

    if action == "reset":
        compareOption = copy.copy(compareDefaultOption)
        compareMaskLines = {}
        compareSkipLines = []
        yield {
            "type": "result",
            "title": None,
            "rows": None,
            "headers": None,
            "columnTypes": None,
            "status": None
        }

    if action == "skip":
        source = str(requestObject["source"])
        if source not in compareSkipLines:
            compareSkipLines.append(source)
        yield {
            "type": "result",
            "title": None,
            "rows": None,
            "headers": None,
            "columnTypes": None,
            "status": None
        }

    if action == "noskip":
        source = str(requestObject["source"])
        if source in compareSkipLines:
            compareSkipLines.remove(source)
        yield {
            "type": "result",
            "title": None,
            "rows": None,
            "headers": None,
            "columnTypes": None,
            "status": None
        }

    if action == "mask":
        source = str(requestObject["source"])
        target = str(requestObject["target"])
        if source not in compareMaskLines.keys():
            compareMaskLines[source] = target
        yield {
            "type": "result",
            "title": None,
            "rows": None,
            "headers": None,
            "columnTypes": None,
            "status": None
        }

    if action == "nomask":
        source = str(requestObject["source"])
        if source in compareMaskLines.keys():
            del compareMaskLines[source]
        yield {
            "type": "result",
            "title": None,
            "rows": None,
            "headers": None,
            "columnTypes": None,
            "status": None
        }

    if action == "compare":
        # 设置当前命令的比较选项，不一定和默认或者基础设置的选项相同
        currentCompareOption = copy.copy(compareOption)
        for key, value in requestObject["compareOptions"].items():
            if key in currentCompareOption:
                currentCompareOption[key] = value
        targetFile = str(requestObject["targetFile"])
        referenceFile = str(requestObject["referenceFile"])

        # 处理targetFile和referenceFile的变量替换
        targetFile = rewriteStatement(cls=cls, statement=targetFile, commandScriptFile=commandScriptFile)
        referenceFile = rewriteStatement(cls=cls, statement=referenceFile, commandScriptFile=commandScriptFile)
        compareHandler = POSIXCompare()
        try:
            compareResult, compareReport = \
                compareHandler.compare_text_files(
                    file1=targetFile,
                    file2=referenceFile,
                    CompareWithMask=currentCompareOption["mask"],
                    CompareIgnoreCase=not currentCompareOption["case"],
                    CompareIgnoreTailOrHeadBlank=not currentCompareOption["trim"],
                    compareAlgorithm=currentCompareOption["algorithm"],
                    ignoreEmptyLine=currentCompareOption["igblank"],
                    skipLines=compareSkipLines,
                    maskLines=compareMaskLines,
                    CompareWorkEncoding=currentCompareOption["workEncoding"],
                    CompareRefEncoding=currentCompareOption["refEncoding"],
                    compareAlgorithmDiffLibThresHold=cls.testOptions.get("COMPARE_DIFFLIB_THRESHOLD")
                )
            if compareResult:
                yield {
                    "type": "result",
                    "title": None,
                    "rows": None,
                    "headers": None,
                    "columnTypes": None,
                    "status": "Compare successful."
                }
            else:
                compareOutput = []
                if "console" in compareOption["output"]:
                    # 如果要求输出到控制台，则显示比对结果到控制台上
                    for line in compareReport:
                        if line.startswith("-") or line.startswith("+"):
                            tag = line[0]
                            workLineno = ""
                            refLineno = ""
                            if tag == "-":
                                workLineno = line[1:7]
                            if tag == "+":
                                refLineno = line[1:7]
                            compareOutput.append([tag, workLineno, refLineno, line[8:]])
                if "diffFile" in compareOption["output"]:
                    # 如果要求输出到文件，则将比对结果写入文件中
                    baseTargetFile = os.path.splitext(targetFile)[0]
                    diffFile = os.path.join(os.path.dirname(os.path.abspath(targetFile)), baseTargetFile + ".dif")
                    fp = open(file=diffFile, mode="w", encoding="UTF-8")
                    for line in compareReport:
                        fp.write(line + "\n")
                    fp.close()
                if "htmlFile" in compareOption["output"]:
                    # 如果要求输出到HTML文件，则将比对结果转换为HTML格式化再输出
                    diffhtmlGenerate = diffHtmlGenerate()
                    htmlResult = diffhtmlGenerate.generateHtmlFromDif(
                        workFile=targetFile,
                        refFile=referenceFile,
                        diffLines=compareReport
                    )
                    baseTargetFile = os.path.splitext(targetFile)[0]
                    diffFile = os.path.join(os.path.dirname(os.path.abspath(targetFile)), baseTargetFile + ".html")
                    fp = open(file=diffFile, mode="w", encoding="UTF-8")
                    for line in htmlResult:
                        fp.write(line + "\n")
                    fp.close()
                yield {
                    "type": "result",
                    "title": None,
                    "rows": compareOutput,
                    "headers": ["#", "work line#", "ref line#", "content"],
                    "columnTypes": None,
                    "status": "Compare failed."
                }
        except DiffException as de:
            yield {
                "type": "error",
                "message": str(de.message)
            }
