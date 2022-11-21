# -*- coding: utf-8 -*-
from antlr4 import InputStream
from antlr4 import CommonTokenStream
from antlr4.error.ErrorListener import ErrorListener
from .antlrgen.APILexer import APILexer
from .antlrgen.APIParser import APIParser
from .apivisitor import APIVisitor


class APIClientErrorListener(ErrorListener):
    # 自定义错误输出记录
    def __init__(self):
        super().__init__()
        self.errorCode = 0
        self.isFinished = True
        self.errorMsg = ""

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        if str(msg).find("expecting") != -1:
            self.isFinished = False
            self.errorCode = 1
            self.errorMsg = str(msg)
        else:
            self.errorCode = 1
            self.errorMsg = "line{}:{}  {} ".format(str(line), str(column), msg)
        super().syntaxError(recognizer, offendingSymbol, line, column, msg, e)


def APIFormatWithPrefix(p_szCommentSQLScript, p_szOutputPrefix=""):
    bAPIPrefix = 'API> '

    # 如果是完全空行的内容，则直接返回SQL前缀
    if len(p_szCommentSQLScript) == 0:
        return bAPIPrefix

    # 把所有的SQL换行, 第一行加入[API >]， 随后加入[   >]
    m_FormattedString = None
    m_CommentSQLLists = p_szCommentSQLScript.split('\n')
    if len(p_szCommentSQLScript) >= 1:
        # 如果原来的内容最后一个字符就是回车换行符，split函数会在后面补一个换行符，这里要去掉，否则前端显示就会多一个空格
        if p_szCommentSQLScript[-1] == "\n":
            del m_CommentSQLLists[-1]

    # 拼接字符串
    for pos in range(0, len(m_CommentSQLLists)):
        if pos == 0:
            m_FormattedString = p_szOutputPrefix + bAPIPrefix + m_CommentSQLLists[pos]
        else:
            m_FormattedString = \
                m_FormattedString + '\n' + p_szOutputPrefix + bAPIPrefix + m_CommentSQLLists[pos]
        if len(m_CommentSQLLists[pos].strip()) != 0:
            bAPIPrefix = '   > '
    return m_FormattedString


def APIAnalyze(apiCommandPlainText: str, defaultNameSpace: str = "API"):
    """ 分析API语句，返回如下内容：
        MulitLineAPIHint                该API是否为完整API， True：完成， False：不完整，需要用户继续输入
        APISplitResults                 包含所有API信息的一个数组，每一个API作为一个元素
        APISplitResultsWithComments     包含注释信息的SQL语句信息，数组长度和APISplitResults相同
        APIHints                        SQL的其他各种标志信息，根据APISplitResultsWithComments中的注释内容解析获得
    """
    # 去除语句的可能前导换行或者空格
    apiCommandPlainText = apiCommandPlainText.strip()

    # 调用Antlr进行语法解析，并自定义错误监听
    stream = InputStream(apiCommandPlainText)
    lexer = APILexer(stream)
    lexer.removeErrorListeners()
    lexer_listener = APIClientErrorListener()
    lexer.addErrorListener(lexer_listener)

    token = CommonTokenStream(lexer)
    parser = APIParser(token)
    parser.removeErrorListeners()
    parser_listener = APIClientErrorListener()
    parser.addErrorListener(parser_listener)
    tree = parser.prog()

    visitor = APIVisitor(token, defaultNameSpace)
    (isFinished, parsedObjects, originScripts, hints, errorCode, errorMsg) = visitor.visit(tree)

    # API语句不可能只有一行，所有如果只有第一行，什么都无法判断，直接认定为not Finished (因为解析器可能因为找不到###头，报告其他错误）
    if apiCommandPlainText.startswith("###") and len(apiCommandPlainText.split('\n')) <= 1:
        isFinished = False

    # 词法和语法解析，任何一个失败，都认为失败
    if not lexer_listener.isFinished:
        isFinished = False
    if not parser_listener.isFinished:
        isFinished = False

    if lexer_listener.errorCode != 0:
        errorCode = lexer_listener.errorCode
        errorMsg = lexer_listener.errorMsg
    if parser_listener.errorCode != 0:
        errorCode = parser_listener.errorCode
        errorMsg = parser_listener.errorMsg
    return isFinished, parsedObjects, originScripts, hints, errorCode, errorMsg
