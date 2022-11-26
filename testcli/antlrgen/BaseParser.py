# Generated from D:/Work/testcli/testcli/antlr\BaseParser.g4 by ANTLR 4.11.1
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,49,154,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,13,
        2,14,7,14,2,15,7,15,2,16,7,16,1,0,1,0,1,0,1,1,1,1,1,1,3,1,41,8,1,
        1,2,1,2,1,3,4,3,46,8,3,11,3,12,3,47,1,4,1,4,3,4,52,8,4,1,4,3,4,55,
        8,4,1,5,1,5,3,5,59,8,5,1,5,3,5,62,8,5,1,6,1,6,1,6,3,6,67,8,6,1,7,
        1,7,1,7,3,7,72,8,7,1,8,1,8,1,8,4,8,77,8,8,11,8,12,8,78,1,8,3,8,82,
        8,8,1,8,3,8,85,8,8,1,8,3,8,88,8,8,1,9,1,9,1,9,4,9,93,8,9,11,9,12,
        9,94,1,9,3,9,98,8,9,1,9,3,9,101,8,9,1,10,1,10,1,10,1,11,1,11,1,11,
        3,11,109,8,11,1,12,1,12,1,12,3,12,114,8,12,1,12,3,12,117,8,12,1,
        13,1,13,1,13,3,13,122,8,13,1,14,1,14,1,14,3,14,127,8,14,1,15,1,15,
        3,15,131,8,15,1,15,4,15,134,8,15,11,15,12,15,135,3,15,138,8,15,1,
        15,3,15,141,8,15,1,15,3,15,144,8,15,1,16,1,16,1,16,3,16,149,8,16,
        1,16,3,16,152,8,16,1,16,0,0,17,0,2,4,6,8,10,12,14,16,18,20,22,24,
        26,28,30,32,0,5,2,0,6,14,36,36,3,0,4,4,6,14,36,36,1,0,19,20,2,0,
        16,16,23,23,1,1,1,1,165,0,34,1,0,0,0,2,40,1,0,0,0,4,42,1,0,0,0,6,
        45,1,0,0,0,8,49,1,0,0,0,10,56,1,0,0,0,12,63,1,0,0,0,14,68,1,0,0,
        0,16,73,1,0,0,0,18,89,1,0,0,0,20,102,1,0,0,0,22,105,1,0,0,0,24,110,
        1,0,0,0,26,118,1,0,0,0,28,123,1,0,0,0,30,128,1,0,0,0,32,145,1,0,
        0,0,34,35,3,2,1,0,35,36,5,0,0,1,36,1,1,0,0,0,37,41,3,32,16,0,38,
        41,3,18,9,0,39,41,3,20,10,0,40,37,1,0,0,0,40,38,1,0,0,0,40,39,1,
        0,0,0,41,3,1,0,0,0,42,43,7,0,0,0,43,5,1,0,0,0,44,46,7,1,0,0,45,44,
        1,0,0,0,46,47,1,0,0,0,47,45,1,0,0,0,47,48,1,0,0,0,48,7,1,0,0,0,49,
        51,5,16,0,0,50,52,5,34,0,0,51,50,1,0,0,0,51,52,1,0,0,0,52,54,1,0,
        0,0,53,55,5,1,0,0,54,53,1,0,0,0,54,55,1,0,0,0,55,9,1,0,0,0,56,58,
        5,17,0,0,57,59,5,34,0,0,58,57,1,0,0,0,58,59,1,0,0,0,59,61,1,0,0,
        0,60,62,5,1,0,0,61,60,1,0,0,0,61,62,1,0,0,0,62,11,1,0,0,0,63,64,
        5,18,0,0,64,66,7,2,0,0,65,67,5,1,0,0,66,65,1,0,0,0,66,67,1,0,0,0,
        67,13,1,0,0,0,68,69,5,28,0,0,69,71,5,34,0,0,70,72,5,1,0,0,71,70,
        1,0,0,0,71,72,1,0,0,0,72,15,1,0,0,0,73,76,5,21,0,0,74,77,3,6,3,0,
        75,77,5,2,0,0,76,74,1,0,0,0,76,75,1,0,0,0,77,78,1,0,0,0,78,76,1,
        0,0,0,78,79,1,0,0,0,79,81,1,0,0,0,80,82,5,24,0,0,81,80,1,0,0,0,81,
        82,1,0,0,0,82,84,1,0,0,0,83,85,5,34,0,0,84,83,1,0,0,0,84,85,1,0,
        0,0,85,87,1,0,0,0,86,88,5,1,0,0,87,86,1,0,0,0,87,88,1,0,0,0,88,17,
        1,0,0,0,89,90,5,32,0,0,90,92,5,44,0,0,91,93,5,45,0,0,92,91,1,0,0,
        0,93,94,1,0,0,0,94,92,1,0,0,0,94,95,1,0,0,0,95,97,1,0,0,0,96,98,
        5,3,0,0,97,96,1,0,0,0,97,98,1,0,0,0,98,100,1,0,0,0,99,101,5,1,0,
        0,100,99,1,0,0,0,100,101,1,0,0,0,101,19,1,0,0,0,102,103,5,33,0,0,
        103,104,5,49,0,0,104,21,1,0,0,0,105,106,5,22,0,0,106,108,7,3,0,0,
        107,109,5,1,0,0,108,107,1,0,0,0,108,109,1,0,0,0,109,23,1,0,0,0,110,
        111,5,25,0,0,111,113,5,36,0,0,112,114,5,3,0,0,113,112,1,0,0,0,113,
        114,1,0,0,0,114,116,1,0,0,0,115,117,5,1,0,0,116,115,1,0,0,0,116,
        117,1,0,0,0,117,25,1,0,0,0,118,119,5,29,0,0,119,121,5,38,0,0,120,
        122,7,4,0,0,121,120,1,0,0,0,121,122,1,0,0,0,122,27,1,0,0,0,123,124,
        5,30,0,0,124,126,5,37,0,0,125,127,5,1,0,0,126,125,1,0,0,0,126,127,
        1,0,0,0,127,29,1,0,0,0,128,137,5,27,0,0,129,131,5,5,0,0,130,129,
        1,0,0,0,130,131,1,0,0,0,131,133,1,0,0,0,132,134,3,4,2,0,133,132,
        1,0,0,0,134,135,1,0,0,0,135,133,1,0,0,0,135,136,1,0,0,0,136,138,
        1,0,0,0,137,130,1,0,0,0,137,138,1,0,0,0,138,140,1,0,0,0,139,141,
        5,3,0,0,140,139,1,0,0,0,140,141,1,0,0,0,141,143,1,0,0,0,142,144,
        5,1,0,0,143,142,1,0,0,0,143,144,1,0,0,0,144,31,1,0,0,0,145,146,5,
        31,0,0,146,148,5,42,0,0,147,149,5,3,0,0,148,147,1,0,0,0,148,149,
        1,0,0,0,149,151,1,0,0,0,150,152,5,1,0,0,151,150,1,0,0,0,151,152,
        1,0,0,0,152,33,1,0,0,0,28,40,47,51,54,58,61,66,71,76,78,81,84,87,
        94,97,100,108,113,116,121,126,130,135,137,140,143,148,151
    ]

class BaseParser ( Parser ):

    grammarFileName = "BaseParser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'\\n'", "','", "';'", "':'", "'@'", "'.'", 
                     "'/'", "'('", "')'", "'['", "']'", "'\"'", "'''", "'\\'", 
                     "<INVALID>", "'EXIT'", "'QUIT'", "'USE'", "'API'", 
                     "'SQL'", "'START'", "'WHENEVER_ERROR'", "'CONTINUE'", 
                     "'LOOP'", "'SPOOL'", "'END'", "'SET'", "'SLEEP'", "<INVALID>", 
                     "'> {%'", "'ASSERT'", "'_LOAD'", "'_HOST'", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "'{%'", "'%}'", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "'\"\"\"'" ]

    symbolicNames = [ "<INVALID>", "CRLF", "COMMA", "SEMICOLON", "COLON", 
                      "AT", "DOT", "SLASH", "BRACKET_OPEN", "BRACKET_CLOSE", 
                      "SQUARE_OPEN", "SQUARE_CLOSE", "DOUBLE_QUOTE", "SINGLE_QUOTE", 
                      "ESCAPE", "SPACE", "EXIT", "QUIT", "USE", "API", "SQL", 
                      "START", "WHENEVER_ERROR", "CONTINUE", "LOOP", "SPOOL", 
                      "END", "SET", "SLEEP", "ECHO_OPEN", "SCRIPT_OPEN", 
                      "ASSERT", "LOAD", "HOST", "INT", "DECIMAL", "String", 
                      "ScriptBlock", "EchoBlock", "ASSERT_SPACE", "ASSERT_OPEN", 
                      "ASSERT_CLOSE", "ASSERT_EXPRESSION", "LOAD_SPACE", 
                      "LOAD_OPTION", "LOAD_EXPRESSION", "LOAD_CRLF", "HOST_SPACE", 
                      "HOST_TAG", "HOST_BLOCK" ]

    RULE_prog = 0
    RULE_baseCommand = 1
    RULE_singleExpression = 2
    RULE_expression = 3
    RULE_exit = 4
    RULE_quit = 5
    RULE_use = 6
    RULE_sleep = 7
    RULE_start = 8
    RULE_load = 9
    RULE_host = 10
    RULE_wheneverError = 11
    RULE_spool = 12
    RULE_echo = 13
    RULE_script = 14
    RULE_set = 15
    RULE_assert = 16

    ruleNames =  [ "prog", "baseCommand", "singleExpression", "expression", 
                   "exit", "quit", "use", "sleep", "start", "load", "host", 
                   "wheneverError", "spool", "echo", "script", "set", "assert" ]

    EOF = Token.EOF
    CRLF=1
    COMMA=2
    SEMICOLON=3
    COLON=4
    AT=5
    DOT=6
    SLASH=7
    BRACKET_OPEN=8
    BRACKET_CLOSE=9
    SQUARE_OPEN=10
    SQUARE_CLOSE=11
    DOUBLE_QUOTE=12
    SINGLE_QUOTE=13
    ESCAPE=14
    SPACE=15
    EXIT=16
    QUIT=17
    USE=18
    API=19
    SQL=20
    START=21
    WHENEVER_ERROR=22
    CONTINUE=23
    LOOP=24
    SPOOL=25
    END=26
    SET=27
    SLEEP=28
    ECHO_OPEN=29
    SCRIPT_OPEN=30
    ASSERT=31
    LOAD=32
    HOST=33
    INT=34
    DECIMAL=35
    String=36
    ScriptBlock=37
    EchoBlock=38
    ASSERT_SPACE=39
    ASSERT_OPEN=40
    ASSERT_CLOSE=41
    ASSERT_EXPRESSION=42
    LOAD_SPACE=43
    LOAD_OPTION=44
    LOAD_EXPRESSION=45
    LOAD_CRLF=46
    HOST_SPACE=47
    HOST_TAG=48
    HOST_BLOCK=49

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.11.1")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class ProgContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def baseCommand(self):
            return self.getTypedRuleContext(BaseParser.BaseCommandContext,0)


        def EOF(self):
            return self.getToken(BaseParser.EOF, 0)

        def getRuleIndex(self):
            return BaseParser.RULE_prog

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitProg" ):
                return visitor.visitProg(self)
            else:
                return visitor.visitChildren(self)




    def prog(self):

        localctx = BaseParser.ProgContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_prog)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 34
            self.baseCommand()
            self.state = 35
            self.match(BaseParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class BaseCommandContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def assert_(self):
            return self.getTypedRuleContext(BaseParser.AssertContext,0)


        def load(self):
            return self.getTypedRuleContext(BaseParser.LoadContext,0)


        def host(self):
            return self.getTypedRuleContext(BaseParser.HostContext,0)


        def getRuleIndex(self):
            return BaseParser.RULE_baseCommand

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitBaseCommand" ):
                return visitor.visitBaseCommand(self)
            else:
                return visitor.visitChildren(self)




    def baseCommand(self):

        localctx = BaseParser.BaseCommandContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_baseCommand)
        try:
            self.state = 40
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [31]:
                self.enterOuterAlt(localctx, 1)
                self.state = 37
                self.assert_()
                pass
            elif token in [32]:
                self.enterOuterAlt(localctx, 2)
                self.state = 38
                self.load()
                pass
            elif token in [33]:
                self.enterOuterAlt(localctx, 3)
                self.state = 39
                self.host()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SingleExpressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def String(self):
            return self.getToken(BaseParser.String, 0)

        def DOT(self):
            return self.getToken(BaseParser.DOT, 0)

        def SLASH(self):
            return self.getToken(BaseParser.SLASH, 0)

        def BRACKET_OPEN(self):
            return self.getToken(BaseParser.BRACKET_OPEN, 0)

        def BRACKET_CLOSE(self):
            return self.getToken(BaseParser.BRACKET_CLOSE, 0)

        def ESCAPE(self):
            return self.getToken(BaseParser.ESCAPE, 0)

        def SQUARE_OPEN(self):
            return self.getToken(BaseParser.SQUARE_OPEN, 0)

        def SQUARE_CLOSE(self):
            return self.getToken(BaseParser.SQUARE_CLOSE, 0)

        def DOUBLE_QUOTE(self):
            return self.getToken(BaseParser.DOUBLE_QUOTE, 0)

        def SINGLE_QUOTE(self):
            return self.getToken(BaseParser.SINGLE_QUOTE, 0)

        def getRuleIndex(self):
            return BaseParser.RULE_singleExpression

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSingleExpression" ):
                return visitor.visitSingleExpression(self)
            else:
                return visitor.visitChildren(self)




    def singleExpression(self):

        localctx = BaseParser.SingleExpressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_singleExpression)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 42
            _la = self._input.LA(1)
            if not(((_la) & ~0x3f) == 0 and ((1 << _la) & 68719509440) != 0):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ExpressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def String(self, i:int=None):
            if i is None:
                return self.getTokens(BaseParser.String)
            else:
                return self.getToken(BaseParser.String, i)

        def DOT(self, i:int=None):
            if i is None:
                return self.getTokens(BaseParser.DOT)
            else:
                return self.getToken(BaseParser.DOT, i)

        def COLON(self, i:int=None):
            if i is None:
                return self.getTokens(BaseParser.COLON)
            else:
                return self.getToken(BaseParser.COLON, i)

        def SLASH(self, i:int=None):
            if i is None:
                return self.getTokens(BaseParser.SLASH)
            else:
                return self.getToken(BaseParser.SLASH, i)

        def BRACKET_OPEN(self, i:int=None):
            if i is None:
                return self.getTokens(BaseParser.BRACKET_OPEN)
            else:
                return self.getToken(BaseParser.BRACKET_OPEN, i)

        def BRACKET_CLOSE(self, i:int=None):
            if i is None:
                return self.getTokens(BaseParser.BRACKET_CLOSE)
            else:
                return self.getToken(BaseParser.BRACKET_CLOSE, i)

        def ESCAPE(self, i:int=None):
            if i is None:
                return self.getTokens(BaseParser.ESCAPE)
            else:
                return self.getToken(BaseParser.ESCAPE, i)

        def SQUARE_OPEN(self, i:int=None):
            if i is None:
                return self.getTokens(BaseParser.SQUARE_OPEN)
            else:
                return self.getToken(BaseParser.SQUARE_OPEN, i)

        def SQUARE_CLOSE(self, i:int=None):
            if i is None:
                return self.getTokens(BaseParser.SQUARE_CLOSE)
            else:
                return self.getToken(BaseParser.SQUARE_CLOSE, i)

        def DOUBLE_QUOTE(self, i:int=None):
            if i is None:
                return self.getTokens(BaseParser.DOUBLE_QUOTE)
            else:
                return self.getToken(BaseParser.DOUBLE_QUOTE, i)

        def SINGLE_QUOTE(self, i:int=None):
            if i is None:
                return self.getTokens(BaseParser.SINGLE_QUOTE)
            else:
                return self.getToken(BaseParser.SINGLE_QUOTE, i)

        def getRuleIndex(self):
            return BaseParser.RULE_expression

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitExpression" ):
                return visitor.visitExpression(self)
            else:
                return visitor.visitChildren(self)




    def expression(self):

        localctx = BaseParser.ExpressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_expression)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 45 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 44
                    _la = self._input.LA(1)
                    if not(((_la) & ~0x3f) == 0 and ((1 << _la) & 68719509456) != 0):
                        self._errHandler.recoverInline(self)
                    else:
                        self._errHandler.reportMatch(self)
                        self.consume()

                else:
                    raise NoViableAltException(self)
                self.state = 47 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,1,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ExitContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EXIT(self):
            return self.getToken(BaseParser.EXIT, 0)

        def INT(self):
            return self.getToken(BaseParser.INT, 0)

        def CRLF(self):
            return self.getToken(BaseParser.CRLF, 0)

        def getRuleIndex(self):
            return BaseParser.RULE_exit

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitExit" ):
                return visitor.visitExit(self)
            else:
                return visitor.visitChildren(self)




    def exit(self):

        localctx = BaseParser.ExitContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_exit)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 49
            self.match(BaseParser.EXIT)
            self.state = 51
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==34:
                self.state = 50
                self.match(BaseParser.INT)


            self.state = 54
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==1:
                self.state = 53
                self.match(BaseParser.CRLF)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class QuitContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def QUIT(self):
            return self.getToken(BaseParser.QUIT, 0)

        def INT(self):
            return self.getToken(BaseParser.INT, 0)

        def CRLF(self):
            return self.getToken(BaseParser.CRLF, 0)

        def getRuleIndex(self):
            return BaseParser.RULE_quit

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitQuit" ):
                return visitor.visitQuit(self)
            else:
                return visitor.visitChildren(self)




    def quit(self):

        localctx = BaseParser.QuitContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_quit)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 56
            self.match(BaseParser.QUIT)
            self.state = 58
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==34:
                self.state = 57
                self.match(BaseParser.INT)


            self.state = 61
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==1:
                self.state = 60
                self.match(BaseParser.CRLF)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class UseContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def USE(self):
            return self.getToken(BaseParser.USE, 0)

        def API(self):
            return self.getToken(BaseParser.API, 0)

        def SQL(self):
            return self.getToken(BaseParser.SQL, 0)

        def CRLF(self):
            return self.getToken(BaseParser.CRLF, 0)

        def getRuleIndex(self):
            return BaseParser.RULE_use

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitUse" ):
                return visitor.visitUse(self)
            else:
                return visitor.visitChildren(self)




    def use(self):

        localctx = BaseParser.UseContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_use)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 63
            self.match(BaseParser.USE)
            self.state = 64
            _la = self._input.LA(1)
            if not(_la==19 or _la==20):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 66
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==1:
                self.state = 65
                self.match(BaseParser.CRLF)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SleepContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def SLEEP(self):
            return self.getToken(BaseParser.SLEEP, 0)

        def INT(self):
            return self.getToken(BaseParser.INT, 0)

        def CRLF(self):
            return self.getToken(BaseParser.CRLF, 0)

        def getRuleIndex(self):
            return BaseParser.RULE_sleep

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSleep" ):
                return visitor.visitSleep(self)
            else:
                return visitor.visitChildren(self)




    def sleep(self):

        localctx = BaseParser.SleepContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_sleep)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 68
            self.match(BaseParser.SLEEP)
            self.state = 69
            self.match(BaseParser.INT)
            self.state = 71
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==1:
                self.state = 70
                self.match(BaseParser.CRLF)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StartContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def START(self):
            return self.getToken(BaseParser.START, 0)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BaseParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(BaseParser.ExpressionContext,i)


        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(BaseParser.COMMA)
            else:
                return self.getToken(BaseParser.COMMA, i)

        def LOOP(self):
            return self.getToken(BaseParser.LOOP, 0)

        def INT(self):
            return self.getToken(BaseParser.INT, 0)

        def CRLF(self):
            return self.getToken(BaseParser.CRLF, 0)

        def getRuleIndex(self):
            return BaseParser.RULE_start

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitStart" ):
                return visitor.visitStart(self)
            else:
                return visitor.visitChildren(self)




    def start(self):

        localctx = BaseParser.StartContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_start)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 73
            self.match(BaseParser.START)
            self.state = 76 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 76
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 36]:
                    self.state = 74
                    self.expression()
                    pass
                elif token in [2]:
                    self.state = 75
                    self.match(BaseParser.COMMA)
                    pass
                else:
                    raise NoViableAltException(self)

                self.state = 78 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (((_la) & ~0x3f) == 0 and ((1 << _la) & 68719509460) != 0):
                    break

            self.state = 81
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==24:
                self.state = 80
                self.match(BaseParser.LOOP)


            self.state = 84
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==34:
                self.state = 83
                self.match(BaseParser.INT)


            self.state = 87
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==1:
                self.state = 86
                self.match(BaseParser.CRLF)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LoadContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LOAD(self):
            return self.getToken(BaseParser.LOAD, 0)

        def LOAD_OPTION(self):
            return self.getToken(BaseParser.LOAD_OPTION, 0)

        def LOAD_EXPRESSION(self, i:int=None):
            if i is None:
                return self.getTokens(BaseParser.LOAD_EXPRESSION)
            else:
                return self.getToken(BaseParser.LOAD_EXPRESSION, i)

        def SEMICOLON(self):
            return self.getToken(BaseParser.SEMICOLON, 0)

        def CRLF(self):
            return self.getToken(BaseParser.CRLF, 0)

        def getRuleIndex(self):
            return BaseParser.RULE_load

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLoad" ):
                return visitor.visitLoad(self)
            else:
                return visitor.visitChildren(self)




    def load(self):

        localctx = BaseParser.LoadContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_load)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 89
            self.match(BaseParser.LOAD)
            self.state = 90
            self.match(BaseParser.LOAD_OPTION)
            self.state = 92 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 91
                self.match(BaseParser.LOAD_EXPRESSION)
                self.state = 94 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==45):
                    break

            self.state = 97
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==3:
                self.state = 96
                self.match(BaseParser.SEMICOLON)


            self.state = 100
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==1:
                self.state = 99
                self.match(BaseParser.CRLF)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class HostContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def HOST(self):
            return self.getToken(BaseParser.HOST, 0)

        def HOST_BLOCK(self):
            return self.getToken(BaseParser.HOST_BLOCK, 0)

        def getRuleIndex(self):
            return BaseParser.RULE_host

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitHost" ):
                return visitor.visitHost(self)
            else:
                return visitor.visitChildren(self)




    def host(self):

        localctx = BaseParser.HostContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_host)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 102
            self.match(BaseParser.HOST)
            self.state = 103
            self.match(BaseParser.HOST_BLOCK)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class WheneverErrorContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def WHENEVER_ERROR(self):
            return self.getToken(BaseParser.WHENEVER_ERROR, 0)

        def CONTINUE(self):
            return self.getToken(BaseParser.CONTINUE, 0)

        def EXIT(self):
            return self.getToken(BaseParser.EXIT, 0)

        def CRLF(self):
            return self.getToken(BaseParser.CRLF, 0)

        def getRuleIndex(self):
            return BaseParser.RULE_wheneverError

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitWheneverError" ):
                return visitor.visitWheneverError(self)
            else:
                return visitor.visitChildren(self)




    def wheneverError(self):

        localctx = BaseParser.WheneverErrorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_wheneverError)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 105
            self.match(BaseParser.WHENEVER_ERROR)
            self.state = 106
            _la = self._input.LA(1)
            if not(_la==16 or _la==23):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 108
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==1:
                self.state = 107
                self.match(BaseParser.CRLF)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SpoolContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def SPOOL(self):
            return self.getToken(BaseParser.SPOOL, 0)

        def String(self):
            return self.getToken(BaseParser.String, 0)

        def SEMICOLON(self):
            return self.getToken(BaseParser.SEMICOLON, 0)

        def CRLF(self):
            return self.getToken(BaseParser.CRLF, 0)

        def getRuleIndex(self):
            return BaseParser.RULE_spool

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSpool" ):
                return visitor.visitSpool(self)
            else:
                return visitor.visitChildren(self)




    def spool(self):

        localctx = BaseParser.SpoolContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_spool)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 110
            self.match(BaseParser.SPOOL)
            self.state = 111
            self.match(BaseParser.String)
            self.state = 113
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==3:
                self.state = 112
                self.match(BaseParser.SEMICOLON)


            self.state = 116
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==1:
                self.state = 115
                self.match(BaseParser.CRLF)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class EchoContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ECHO_OPEN(self):
            return self.getToken(BaseParser.ECHO_OPEN, 0)

        def EchoBlock(self):
            return self.getToken(BaseParser.EchoBlock, 0)

        def CRLF(self):
            return self.getToken(BaseParser.CRLF, 0)

        def EOF(self):
            return self.getToken(BaseParser.EOF, 0)

        def getRuleIndex(self):
            return BaseParser.RULE_echo

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitEcho" ):
                return visitor.visitEcho(self)
            else:
                return visitor.visitChildren(self)




    def echo(self):

        localctx = BaseParser.EchoContext(self, self._ctx, self.state)
        self.enterRule(localctx, 26, self.RULE_echo)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 118
            self.match(BaseParser.ECHO_OPEN)
            self.state = 119
            self.match(BaseParser.EchoBlock)
            self.state = 121
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,19,self._ctx)
            if la_ == 1:
                self.state = 120
                _la = self._input.LA(1)
                if not(_la==-1 or _la==1):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ScriptContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def SCRIPT_OPEN(self):
            return self.getToken(BaseParser.SCRIPT_OPEN, 0)

        def ScriptBlock(self):
            return self.getToken(BaseParser.ScriptBlock, 0)

        def CRLF(self):
            return self.getToken(BaseParser.CRLF, 0)

        def getRuleIndex(self):
            return BaseParser.RULE_script

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitScript" ):
                return visitor.visitScript(self)
            else:
                return visitor.visitChildren(self)




    def script(self):

        localctx = BaseParser.ScriptContext(self, self._ctx, self.state)
        self.enterRule(localctx, 28, self.RULE_script)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 123
            self.match(BaseParser.SCRIPT_OPEN)
            self.state = 124
            self.match(BaseParser.ScriptBlock)
            self.state = 126
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==1:
                self.state = 125
                self.match(BaseParser.CRLF)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SetContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def SET(self):
            return self.getToken(BaseParser.SET, 0)

        def SEMICOLON(self):
            return self.getToken(BaseParser.SEMICOLON, 0)

        def CRLF(self):
            return self.getToken(BaseParser.CRLF, 0)

        def AT(self):
            return self.getToken(BaseParser.AT, 0)

        def singleExpression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BaseParser.SingleExpressionContext)
            else:
                return self.getTypedRuleContext(BaseParser.SingleExpressionContext,i)


        def getRuleIndex(self):
            return BaseParser.RULE_set

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSet" ):
                return visitor.visitSet(self)
            else:
                return visitor.visitChildren(self)




    def set_(self):

        localctx = BaseParser.SetContext(self, self._ctx, self.state)
        self.enterRule(localctx, 30, self.RULE_set)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 128
            self.match(BaseParser.SET)
            self.state = 137
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if ((_la) & ~0x3f) == 0 and ((1 << _la) & 68719509472) != 0:
                self.state = 130
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==5:
                    self.state = 129
                    self.match(BaseParser.AT)


                self.state = 133 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 132
                    self.singleExpression()
                    self.state = 135 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (((_la) & ~0x3f) == 0 and ((1 << _la) & 68719509440) != 0):
                        break



            self.state = 140
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==3:
                self.state = 139
                self.match(BaseParser.SEMICOLON)


            self.state = 143
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==1:
                self.state = 142
                self.match(BaseParser.CRLF)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AssertContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ASSERT(self):
            return self.getToken(BaseParser.ASSERT, 0)

        def ASSERT_EXPRESSION(self):
            return self.getToken(BaseParser.ASSERT_EXPRESSION, 0)

        def SEMICOLON(self):
            return self.getToken(BaseParser.SEMICOLON, 0)

        def CRLF(self):
            return self.getToken(BaseParser.CRLF, 0)

        def getRuleIndex(self):
            return BaseParser.RULE_assert

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAssert" ):
                return visitor.visitAssert(self)
            else:
                return visitor.visitChildren(self)




    def assert_(self):

        localctx = BaseParser.AssertContext(self, self._ctx, self.state)
        self.enterRule(localctx, 32, self.RULE_assert)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 145
            self.match(BaseParser.ASSERT)
            self.state = 146
            self.match(BaseParser.ASSERT_EXPRESSION)
            self.state = 148
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==3:
                self.state = 147
                self.match(BaseParser.SEMICOLON)


            self.state = 151
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==1:
                self.state = 150
                self.match(BaseParser.CRLF)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





