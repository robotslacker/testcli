# -*- coding: utf-8 -*-
import json
from json import JSONDecodeError

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


def APIRequestStringFormatWithPrefix(commentAPIScript, outputPrefix=""):
    bAPIPrefix = 'API> '

    # 如果是完全空行的内容，则直接返回API前缀
    if len(commentAPIScript) == 0:
        return bAPIPrefix

    # 把所有的API换行, 第一行加入[API >]， 随后加入[   >]
    formattedString = None
    if len(commentAPIScript) >= 1:
        # 如果原来的内容最后一个字符就是回车换行符，要去掉，否则前端显示就会多一个空格
        if commentAPIScript[-1] == "\n":
            commentAPIScript = commentAPIScript[:-1]
    commentAPILists = commentAPIScript.split('\n')

    # 拼接字符串
    for pos in range(0, len(commentAPILists)):
        if pos == 0:
            formattedString = outputPrefix + bAPIPrefix + commentAPILists[pos]
        else:
            formattedString = \
                formattedString + '\n' + outputPrefix + bAPIPrefix + commentAPILists[pos]
        if len(commentAPILists[pos].strip()) != 0:
            bAPIPrefix = '   > '
    return formattedString


def APIRequestObjectFormatWithPrefix(headerPrefix, requestObject, outputPrefix):
    bAPIPrefix = 'API> '

    # 把所有的API换行, 第一行加入[API >]， 随后加入[   >]
    formattedString = outputPrefix + bAPIPrefix + headerPrefix

    # 打印Header信息
    if "httpRequestTarget" in requestObject:
        formattedString = formattedString + outputPrefix + '   > ' + \
                          requestObject["httpMethod"] + " " + requestObject["httpRequestTarget"]
    if "httpFields" in requestObject:
        fieldSigin = "?"
        for httpFieldName, httpFieldValue in requestObject["httpFields"].items():
            formattedString = (formattedString + "\n" + outputPrefix + '   >     ' +
                               fieldSigin + str(httpFieldName) + "=" + str(httpFieldValue))
            fieldSigin = "&"
    if "headers" in requestObject:
        for headerName, headerValue in requestObject["headers"].items():
            formattedString = (formattedString + "\n" + outputPrefix + '   > ' +
                               headerName + ": " + headerValue)
    if "contents" in requestObject:
        formattedString = formattedString + "\n" + outputPrefix + "   > "
        for content in requestObject["contents"]:
            if content == "\n":
                formattedString = formattedString + "\n" + outputPrefix + "   > \n"
                continue
            try:
                data = json.loads(content)
                data = json.dumps(obj=data,
                                  sort_keys=True,
                                  indent=4,
                                  separators=(',', ': '),
                                  ensure_ascii=False
                                  )
                for output in data.split('\n'):
                    formattedString = formattedString + "\n" + outputPrefix + '   > ' + output
            except JSONDecodeError:
                # 不是一个Json内容，直接打印好了. 但是去掉正文的最后无意义空行（仅仅是不打印）
                outputLines = content.split('\n')
                while True:
                    if len(outputLines) > 0:
                        if outputLines[-1] == "":
                            del outputLines[-1]
                        else:
                            break
                    else:
                        break
                for output in outputLines:
                    formattedString = formattedString + "\n" + outputPrefix + '   > ' + output

    if "operate" in requestObject and requestObject["operate"] is not None:
        if len(requestObject["operate"]) == 1:
            operate = requestObject["operate"][0]
            formattedString = formattedString.strip()
            formattedString = \
                formattedString + "\n" + outputPrefix + '   > ' + operate["operator"] + " " + operate["content"]
    return formattedString


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
    (isFinished, parsedObjects, errorCode, parseErrorMsg) = visitor.visit(tree)

    # API语句不可能只有一行，所有如果只有第一行，什么都无法判断，直接认定为not Finished (因为解析器可能因为找不到###头，报告其他错误）
    if apiCommandPlainText.startswith("###") and len(apiCommandPlainText.split('\n')) <= 1:
        isFinished = False

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
