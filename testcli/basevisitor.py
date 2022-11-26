# -*- coding: utf-8 -*-
from antlr4.Token import Token
import re

from .antlrgen.BaseParser import BaseParser
from .antlrgen.BaseParserVisitor import BaseParserVisitor
from .antlrgen.BaseLexer import BaseLexer


class BaseVisitor(BaseParserVisitor):
    def __init__(self, tokens):
        # 词法符号表
        self.tokens = tokens
        # 解析是否正常完成
        self.isFinished = True
        # 返回去掉了注释信息的解析结果
        self.parsedObject = None
        # 包含了所有注释信息的原语句（格式保持不变，包括空行，换行符号等)
        self.originScripts = None
        # 有意义的注释信息(即用-- [Hint] 开头的SQL语句, 或者用# [Hint]|// [Hint] 开头的API语句), 一个语句有多个注释信息的，用数组返回
        self.hints = []
        # 如果成功，返回0； 如果失败，返回-1；
        self.errorCode = 0
        # 如果成功，返回空；如果失败，返回解析的错误提示信息
        self.errorMsg = ""

    """
        功能：返回分析上下文分词索引
             提示计入
        参数：
             ctx: 上下文
        返回：
            start: 开始索引号
            end: 结束索引号
    """

    @staticmethod
    def getSourceInterval(ctx):
        start, end = ctx.getSourceInterval()
        while start > 0:
            token = ctx.parser._input.tokens[start - 1]
            if token.channel != BaseLexer.HINT_CHANNEL:
                break
            start -= 1
        return start, end

    """
        功能：返回指定通道文本
        参数：
            tokens 分词数组
            channel 分词通道
        返回：
            分词数组指定通道的分词文本
    """

    @staticmethod
    def getText(tokens, channel=Token.DEFAULT_CHANNEL):
        # 返回单一通道的信息
        return ''.join(token.text if token.channel == channel else '' for token in tokens)

    """
        功能：返回全部文本
        参数：
            tokens 分词数组
        返回：
            指定分词数组的文本
    """

    @staticmethod
    def getSource(tokens):
        # 返回单一通道的信息
        return ''.join(token.text for token in tokens)

    """
        功能：返回提示文本
        参数：
            tokens 分词数组
        返回：
            指定分词数组中提示分词文本
    """

    def visitProg(self, ctx: BaseParser.ProgContext):
        self.visitChildren(ctx)
        return self.isFinished, self.parsedObject, self.originScripts, self.hints, self.errorCode, self.errorMsg

    def visitBaseCommand(self, ctx: BaseParser.BaseCommandContext):
        return self.visitChildren(ctx)

    def visitAssert(self, ctx: BaseParser.AssertContext):
        parsedObject = {'name': 'ASSERT'}

        if ctx.ASSERT_EXPRESSION() is not None:
            expression = str(ctx.ASSERT_EXPRESSION().getText()).strip()
            if expression.startswith('{%'):
                expression = expression[2:]
            if expression.endswith('%}'):
                expression = expression[:-2]
            parsedObject.update({'expression': expression})
        else:
            parsedObject.update({'expression': ""})

        # 获取源文件
        start, end = self.getSourceInterval(ctx)
        tokens = ctx.parser._input.tokens[start:end+1]
        originScript = self.getSource(tokens)

        # 获取提示信息
        hint = []

        # 获取错误代码
        errorCode = 0
        errorMsg = None
        if ctx.exception is not None:
            errorCode = -1
            errorMsg = ctx.exception.message

        self.originScripts = originScript
        self.parsedObject = parsedObject
        self.hints = hint
        self.errorCode = errorCode
        self.errorMsg = errorMsg
        return parsedObject, originScript, hint, errorCode, errorMsg
