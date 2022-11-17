import sys
import os
from antlr4 import *
from antlr4 import InputStream
import json

from antlrgen.ClientLexer import ClientLexer
from antlrgen.ClientParser import ClientParser
from ClientVisitor import ClientVisitor
from antlr4.error.ErrorListener import ErrorListener

"""
词法、语法分析错误监听器
"""


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


"""
分析函数
    script: 分析脚步
    defaultNameSpace: 名字空间
                    None 默认全部分析
                    SQL 分析SQL语句
                    API 分析HTTP请求
"""


def parse(script, defaultNameSpace=None):
    stream = InputStream(script)
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
    result = visitor.visit(tree)

    return result


"""
    语法树输出辅助函数
"""


def beautify_lisp_string(in_string):
    indent_size = 3
    add_indent = ' ' * indent_size
    out_string = in_string[0]  # no indent for 1st (
    indent = ''
    for i in range(1, len(in_string)):
        if in_string[i] == '(' and in_string[i + 1] != ' ':
            indent += add_indent
            out_string += "\n" + indent + '('
        elif in_string[i] == ')':
            out_string += ')'
            if len(indent) > 0:
                indent = indent.replace(add_indent, '', 1)
        else:
            out_string += in_string[i]
    return out_string


if __name__ == '__main__':
    defaultNameSpace = "SQL"

    isFinished, parsedObjects, originScripts, hints, errorCode, errorMsg = \
        parse("set xxx yyy zzz ddd ", defaultNameSpace=defaultNameSpace)
    print("isFInsished = " + str(isFinished))
    if isFinished:
        parsedLenth = len(parsedObjects)
        for i in range(0, len(parsedObjects)):
            print(">>>parsed:")
            print(json.dumps(parsedObjects[i]))
            print(">>>origin:")
            print(originScripts[i])
            print(">>>hints:")
            print(hints[i])
            print(">>>errorCode:")
            print(errorCode[i])
            print(">>>errorMsg:")
            print(errorMsg[i])
            print()
            print()

    # files = os.listdir("./test")
    # for root, dirs, files in os.walk("./test"):
    #     for file in files:
    #         filename, extension = os.path.splitext(file)
    #         if extension.endswith(".sql"):
    #             defaultNameSpace = "SQL"
    #         elif extension.endswith(".api"):
    #             defaultNameSpace = "API"
    #         else:
    #             continue
    #         print("=====================================================")
    #         print("Parse " + defaultNameSpace + " file " + file + "...")
    #         f = open(file=os.path.join(root, file), mode='r', encoding="UTF-8")
    #         script = f.read()
    #         lines = script.split("\n")
    #
    #         command = None
    #
    #         for pos in range(0, len(lines)):
    #             # if command is None:
    #             #     command = lines[pos]
    #             #     if lines[pos].strip().startswith("--"):
    #             #         continue
    #             # else:
    #             #     command = command + "\n" + lines[pos]
    #             #     if lines[pos].strip().startswith("--"):
    #             #         continue
    #             command = lines[pos]
    #             print(">>>>>>>>>>>>>>> ")
    #             print(">>>command:[" + str(command) + "]")
    #             isFinished, parsedObjects, originScripts, hints, errorCode, errorMsg = \
    #                 parse(command, defaultNameSpace=defaultNameSpace)
    #             print("isFInsished = " + str(isFinished))
    #             if isFinished:
    #                 parsedLenth = len(parsedObjects)
    #                 for i in range(0, len(parsedObjects)):
    #                     print(">>>parsed:")
    #                     print(json.dumps(parsedObjects[i]))
    #                     print(">>>origin:")
    #                     print(originScripts[i])
    #                     print(">>>hints:")
    #                     print(hints[i])
    #                     print(">>>errorCode:")
    #                     print(errorCode[i])
    #                     print(">>>errorMsg:")
    #                     print(errorMsg[i])
    #                     print()
    #                     print()
    #                 # 语句已经结束
    #                 command = None
    #             else:
    #                 # 语句还没有结束，循环等待
    #                 if pos == (len(lines) - 1):
    #                     parsedLenth = len(parsedObjects)
    #                     for i in range(0, len(parsedObjects)):
    #                         print(">>>parsed:")
    #                         print(json.dumps(parsedObjects[i]))
    #                         print(">>>origin:")
    #                         print(originScripts[i])
    #                         print(">>>hints:")
    #                         print(hints[i])
    #                         print(">>>errorCode:")
    #                         print(errorCode[i])
    #                         print(">>>errorMsg:")
    #                         print(errorMsg[i])
    #                         print()
    #                         print()
    #                 continue
