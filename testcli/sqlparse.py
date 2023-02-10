# -*- coding: utf-8 -*-
from antlr4 import InputStream
from antlr4 import CommonTokenStream
from antlr4.error.ErrorListener import ErrorListener
from .antlrgen.SQLLexer import SQLLexer
from .antlrgen.SQLParser import SQLParser
from .sqlvisitor import SQLVisitor


class SQLClientErrorListener(ErrorListener):
    # 自定义错误输出记录
    def __init__(self):
        super().__init__()
        self.errorCode = 0
        self.isFinished = True
        self.errorMsg = ""

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        if str(msg).startswith("missing SQL_END"):
            self.isFinished = False
            self.errorCode = 1
            self.errorMsg = str(msg)
        else:
            self.errorCode = 1
            self.errorMsg = "line{}:{}  {} ".format(str(line), str(column), msg)
        super().syntaxError(recognizer, offendingSymbol, line, column, msg, e)


def SQLFormatWithPrefix(p_szCommentSQLScript, p_szOutputPrefix=""):
    bSQLPrefix = 'SQL> '

    # 如果是完全空行的内容，则直接返回SQL前缀
    if len(p_szCommentSQLScript) == 0:
        return bSQLPrefix

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
    # 去除语句的可能前导换行或者空格
    sqlCommandPlainText = sqlCommandPlainText.strip()

    # 调用Antlr进行语法解析，并自定义错误监听
    stream = InputStream(sqlCommandPlainText)
    lexer = SQLLexer(stream)
    lexer.removeErrorListeners()
    lexer_listener = SQLClientErrorListener()
    lexer.addErrorListener(lexer_listener)

    token = CommonTokenStream(lexer)
    parser = SQLParser(token)
    parser.removeErrorListeners()
    parser_listener = SQLClientErrorListener()
    parser.addErrorListener(parser_listener)
    tree = parser.prog()

    visitor = SQLVisitor(token, defaultNameSpace)
    (isFinished, parsedObjects, errorCode, parseErrorMsg) = visitor.visit(tree)

    # 词法和语法解析，任何一个失败，都认为失败
    if not lexer_listener.isFinished:
        isFinished = False
    if not parser_listener.isFinished:
        isFinished = False

    errorMsg = None
    if lexer_listener.errorCode != 0:
        errorCode = lexer_listener.errorCode
        errorMsg = lexer_listener.errorMsg
    if parser_listener.errorCode != 0:
        errorCode = parser_listener.errorCode
        errorMsg = parser_listener.errorMsg
    if parseErrorMsg is not None and len(str(parseErrorMsg).strip()) != 0:
        if errorMsg is not None:
            # 如果访问器有错误信息，则直接记录访问器的错误消息
            errorMsg = parseErrorMsg + " < " + errorMsg
        else:
            errorMsg = parseErrorMsg
    return isFinished, parsedObjects, errorCode, errorMsg
