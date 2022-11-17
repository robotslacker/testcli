# -*- coding: utf-8 -*-
import re
import copy
import os
import shlex
from .testcliexception import TestCliException


def APIFormatWithPrefix(p_szCommentSQLScript, p_szOutputPrefix=""):
    # 如果是完全空行的内容，则跳过
    if len(p_szCommentSQLScript) == 0:
        return None

    # 把所有的SQL换行, 第一行加入[API >]， 随后加入[   >]
    m_FormattedString = None
    m_CommentSQLLists = p_szCommentSQLScript.split('\n')
    if len(p_szCommentSQLScript) >= 1:
        # 如果原来的内容最后一个字符就是回车换行符，split函数会在后面补一个换行符，这里要去掉，否则前端显示就会多一个空格
        if p_szCommentSQLScript[-1] == "\n":
            del m_CommentSQLLists[-1]

    # 拼接字符串
    bSQLPrefix = 'API> '
    for pos in range(0, len(m_CommentSQLLists)):
        if pos == 0:
            m_FormattedString = p_szOutputPrefix + bSQLPrefix + m_CommentSQLLists[pos]
        else:
            m_FormattedString = \
                m_FormattedString + '\n' + p_szOutputPrefix + bSQLPrefix + m_CommentSQLLists[pos]
        if len(m_CommentSQLLists[pos].strip()) != 0:
            bSQLPrefix = '   > '
    return m_FormattedString


def APIAnalyze(apiCommandPlainText):
    """ 分析API语句，返回如下内容：
        APIFinished                     是否为完整API请求定义， True：完成， False：不完整，需要用户继续输入
        APISplitResults                 包含所有API信息的一个数组，每一个API作为一个元素
        APISplitResultsWithComments     包含注释信息的API语句信息，数组长度和APISplitResults相同
        APIHints                        API的其他各种标志信息，根据APISplitResultsWithComments中的注释内容解析获得

        注意： APISplitResults, APISplitResultsWithComments, APIHints 均为数组。且其长度要保持一致。
    """

    """
        1. 备份原有的语句， 然后在执行语句中去掉注释信息
            HTTP文件中支持注释。注释可以描述在请求之前，或者请求之后。注释描述可以在Header的描述中，也可以在请求体中被描述。
            注释必须从一行的开始（容许包含缩进的内容）。
            支持的注释为：
                //开头的语句
                #开头的语句           
    """
    # 处理逻辑
    # 1. 将所有的信息根据换行符分拆到数组中
    # 2. 将语句内容中的注释信息一律去掉
    #
    # 3. 依次将每行的内容进行API判断，按照完成SQL来进行分组。同时拼接其注释信息到其中
    # 4. 进行其他的处理
    # 5. 分析SQLHint信息
    # 6. 所有信息返回
    APICommands = apiCommandPlainText.split('\n')

    # API分析的结果， 这两个（包含注释，不包含注释）的数组长度相等，若只有注释，则API结果中为空白（不是空）
    APISplitResults = []
    # 包含注释的API语句分析结果
    APISplitResultsWithComments = []
    # API的辅助信息
    APIHints = []

    # 从APICommands中删除所有的注释信息，但不删除ECHO中的注释信息
    bInEchoSection = False          # 是否在ECHO语句内部
    echoMessages = None             # 回显信息

    apiRequest = None               # API请求命令
    apiRequestWithComment = None    # API请求命令(包含注释)
    APIHint = {}                    # API的辅助信息

    for pos in range(0, len(APICommands)):
        APIHint["Name"] = "NO-NAME"
        # 首先处理特殊的ECHO信息，ECHO中的信息不涉及注释
        # 对于ECHO信息，则回送的内容包含3段
        # ECHO <文件名>
        # .... 文件正文。 多行这里将会被折叠
        # ECHO OFF
        if bInEchoSection:
            # ECHO信息已经结束
            if re.match(r'echo\s+off', APICommands[pos], re.IGNORECASE):
                if echoMessages is not None:
                    APISplitResults.append(echoMessages)
                    APISplitResultsWithComments.append(echoMessages)
                APISplitResults.append(APICommands[pos])
                APISplitResultsWithComments.append(APICommands[pos])
                APIHints.append([])
                echoMessages = None
                bInEchoSection = False
                continue
            echoMessages = echoMessages + "\n" + APICommands[pos]
            continue

        # 如果当前是ECHO文件开头，进入ECHO模式
        if re.match(r'echo\s+.*', APICommands[pos], re.IGNORECASE):
            APISplitResults.append(APICommands[pos])
            APISplitResultsWithComments.append(APICommands[pos])
            APIHints.append([])
            bInEchoSection = True
            continue

        # 如果###开头，则表示为新的Request
        trimdCommand = str(APICommands[pos]).lstrip()
        if trimdCommand.startswith('###'):
            # 新的测试开始
            if apiRequest is not None:
                APISplitResults.append(apiRequest)
                APISplitResultsWithComments.append(apiRequestWithComment)
                APIHints.append(APIHint)
                apiRequest = None
                apiRequestWithComment = None
                APIHint = {}
            APIHint["Name"] = trimdCommand.replace("^#+", "")

        # 去掉注释内容
        # 注释内容，在APISplitResults会包含一个空行，APISplitResultsWithComments包含完整行
        # HTTP文件中支持注释。注释可以描述在请求之前，或者请求之后。注释描述可以在Header的描述中，也可以在请求体中被描述。
        # 注释必须从一行的开始（容许包含缩进的内容）。
        # 支持的注释为：
        #     //开头的语句
        #     #开头的语句
        if trimdCommand.startswith('#') or trimdCommand.startswith('//'):
            if apiRequestWithComment is not None:
                apiRequestWithComment = apiRequestWithComment + APICommands[pos]
            else:
                apiRequestWithComment = APICommands[pos]
            continue

        # 如果语句为Exit，Quit，SET，SPOOL, Session, Use 则为特殊的语句,直接标记结束当前API
        if trimdCommand.upper().startswith("EXIT") or \
                trimdCommand.upper().startswith("QUIT") or \
                trimdCommand.upper().startswith("SPOOL") or \
                trimdCommand.upper().startswith("SECTION") or \
                trimdCommand.upper().startswith("USE") or \
                trimdCommand.upper().startswith("SET"):
            # 之前的Case到此结束
            if apiRequest is not None:
                APISplitResults.append(apiRequest)
                APISplitResultsWithComments.append(apiRequestWithComment)
                APIHints.append(APIHint)
                apiRequest = None
                apiRequestWithComment = None
                APIHint = {}
            APISplitResults.append(APICommands[pos])
            APISplitResultsWithComments.append(APICommands[pos])
            APIHints.append(APIHint)
            continue

        # 正常的API语句
        if apiRequest is not None:
            apiRequest = apiRequest + APICommands[pos]
        else:
            apiRequest = APICommands[pos]
        if apiRequestWithComment is not None:
            apiRequestWithComment = apiRequestWithComment + APICommands[pos]
        else:
            apiRequestWithComment = APICommands[pos]

        # end For

    # 这里把最后一段API送回解析器
    if apiRequest is not None:
        APISplitResults.append(apiRequest)
        APISplitResultsWithComments.append(apiRequestWithComment)
        APIHints.append(APIHint)

    return True, APISplitResults, APISplitResultsWithComments, APIHints
