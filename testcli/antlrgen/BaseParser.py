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
        4,1,83,206,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,13,
        2,14,7,14,2,15,7,15,2,16,7,16,2,17,7,17,2,18,7,18,2,19,7,19,1,0,
        1,0,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,1,53,8,1,1,2,1,2,1,
        3,4,3,58,8,3,11,3,12,3,59,1,4,1,4,3,4,64,8,4,1,4,3,4,67,8,4,1,5,
        1,5,3,5,71,8,5,1,5,3,5,74,8,5,1,6,1,6,1,6,3,6,79,8,6,1,7,1,7,1,7,
        3,7,84,8,7,1,8,1,8,1,8,1,8,5,8,90,8,8,10,8,12,8,93,9,8,1,8,3,8,96,
        8,8,1,8,3,8,99,8,8,1,8,3,8,102,8,8,1,8,3,8,105,8,8,1,9,1,9,1,9,4,
        9,110,8,9,11,9,12,9,111,1,9,3,9,115,8,9,1,9,3,9,118,8,9,1,10,1,10,
        1,10,3,10,123,8,10,1,10,3,10,126,8,10,1,11,1,11,1,11,1,12,1,12,1,
        12,1,12,1,12,3,12,136,8,12,1,12,1,12,3,12,140,8,12,1,12,3,12,143,
        8,12,1,12,3,12,146,8,12,1,13,1,13,1,13,3,13,151,8,13,1,13,3,13,154,
        8,13,1,14,1,14,3,14,158,8,14,1,14,3,14,161,8,14,1,15,1,15,1,15,1,
        15,3,15,167,8,15,1,15,3,15,170,8,15,1,16,1,16,1,16,3,16,175,8,16,
        1,16,3,16,178,8,16,1,17,1,17,1,17,3,17,183,8,17,1,18,1,18,1,18,3,
        18,188,8,18,1,19,1,19,3,19,192,8,19,1,19,5,19,195,8,19,10,19,12,
        19,198,9,19,1,19,3,19,201,8,19,1,19,3,19,204,8,19,1,19,0,0,20,0,
        2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,0,5,2,0,6,14,
        38,38,3,0,4,4,6,14,38,38,1,0,19,20,1,0,76,77,1,1,1,1,230,0,40,1,
        0,0,0,2,52,1,0,0,0,4,54,1,0,0,0,6,57,1,0,0,0,8,61,1,0,0,0,10,68,
        1,0,0,0,12,75,1,0,0,0,14,80,1,0,0,0,16,85,1,0,0,0,18,106,1,0,0,0,
        20,119,1,0,0,0,22,127,1,0,0,0,24,130,1,0,0,0,26,147,1,0,0,0,28,155,
        1,0,0,0,30,162,1,0,0,0,32,171,1,0,0,0,34,179,1,0,0,0,36,184,1,0,
        0,0,38,189,1,0,0,0,40,41,3,2,1,0,41,42,5,0,0,1,42,1,1,0,0,0,43,53,
        3,20,10,0,44,53,3,18,9,0,45,53,3,22,11,0,46,53,3,16,8,0,47,53,3,
        24,12,0,48,53,3,26,13,0,49,53,3,28,14,0,50,53,3,30,15,0,51,53,3,
        38,19,0,52,43,1,0,0,0,52,44,1,0,0,0,52,45,1,0,0,0,52,46,1,0,0,0,
        52,47,1,0,0,0,52,48,1,0,0,0,52,49,1,0,0,0,52,50,1,0,0,0,52,51,1,
        0,0,0,53,3,1,0,0,0,54,55,7,0,0,0,55,5,1,0,0,0,56,58,7,1,0,0,57,56,
        1,0,0,0,58,59,1,0,0,0,59,57,1,0,0,0,59,60,1,0,0,0,60,7,1,0,0,0,61,
        63,5,16,0,0,62,64,5,36,0,0,63,62,1,0,0,0,63,64,1,0,0,0,64,66,1,0,
        0,0,65,67,5,1,0,0,66,65,1,0,0,0,66,67,1,0,0,0,67,9,1,0,0,0,68,70,
        5,17,0,0,69,71,5,36,0,0,70,69,1,0,0,0,70,71,1,0,0,0,71,73,1,0,0,
        0,72,74,5,1,0,0,73,72,1,0,0,0,73,74,1,0,0,0,74,11,1,0,0,0,75,76,
        5,18,0,0,76,78,7,2,0,0,77,79,5,1,0,0,78,77,1,0,0,0,78,79,1,0,0,0,
        79,13,1,0,0,0,80,81,5,24,0,0,81,83,5,36,0,0,82,84,5,1,0,0,83,82,
        1,0,0,0,83,84,1,0,0,0,84,15,1,0,0,0,85,86,5,28,0,0,86,91,5,53,0,
        0,87,88,5,52,0,0,88,90,5,53,0,0,89,87,1,0,0,0,90,93,1,0,0,0,91,89,
        1,0,0,0,91,92,1,0,0,0,92,95,1,0,0,0,93,91,1,0,0,0,94,96,5,50,0,0,
        95,94,1,0,0,0,95,96,1,0,0,0,96,98,1,0,0,0,97,99,5,51,0,0,98,97,1,
        0,0,0,98,99,1,0,0,0,99,101,1,0,0,0,100,102,5,3,0,0,101,100,1,0,0,
        0,101,102,1,0,0,0,102,104,1,0,0,0,103,105,5,1,0,0,104,103,1,0,0,
        0,104,105,1,0,0,0,105,17,1,0,0,0,106,107,5,29,0,0,107,109,5,46,0,
        0,108,110,5,47,0,0,109,108,1,0,0,0,110,111,1,0,0,0,111,109,1,0,0,
        0,111,112,1,0,0,0,112,114,1,0,0,0,113,115,5,3,0,0,114,113,1,0,0,
        0,114,115,1,0,0,0,115,117,1,0,0,0,116,118,5,1,0,0,117,116,1,0,0,
        0,117,118,1,0,0,0,118,19,1,0,0,0,119,120,5,27,0,0,120,122,5,44,0,
        0,121,123,5,3,0,0,122,121,1,0,0,0,122,123,1,0,0,0,123,125,1,0,0,
        0,124,126,5,1,0,0,125,124,1,0,0,0,125,126,1,0,0,0,126,21,1,0,0,0,
        127,128,5,30,0,0,128,129,5,57,0,0,129,23,1,0,0,0,130,139,5,34,0,
        0,131,140,5,68,0,0,132,140,5,69,0,0,133,140,5,70,0,0,134,136,5,64,
        0,0,135,134,1,0,0,0,135,136,1,0,0,0,136,137,1,0,0,0,137,138,5,65,
        0,0,138,140,5,71,0,0,139,131,1,0,0,0,139,132,1,0,0,0,139,133,1,0,
        0,0,139,135,1,0,0,0,140,142,1,0,0,0,141,143,5,62,0,0,142,141,1,0,
        0,0,142,143,1,0,0,0,143,145,1,0,0,0,144,146,5,1,0,0,145,144,1,0,
        0,0,145,146,1,0,0,0,146,25,1,0,0,0,147,148,5,31,0,0,148,150,5,61,
        0,0,149,151,5,3,0,0,150,149,1,0,0,0,150,151,1,0,0,0,151,153,1,0,
        0,0,152,154,5,1,0,0,153,152,1,0,0,0,153,154,1,0,0,0,154,27,1,0,0,
        0,155,157,5,32,0,0,156,158,5,3,0,0,157,156,1,0,0,0,157,158,1,0,0,
        0,158,160,1,0,0,0,159,161,5,1,0,0,160,159,1,0,0,0,160,161,1,0,0,
        0,161,29,1,0,0,0,162,163,5,35,0,0,163,164,5,74,0,0,164,166,7,3,0,
        0,165,167,5,75,0,0,166,165,1,0,0,0,166,167,1,0,0,0,167,169,1,0,0,
        0,168,170,5,1,0,0,169,168,1,0,0,0,169,170,1,0,0,0,170,31,1,0,0,0,
        171,172,5,22,0,0,172,174,5,38,0,0,173,175,5,3,0,0,174,173,1,0,0,
        0,174,175,1,0,0,0,175,177,1,0,0,0,176,178,5,1,0,0,177,176,1,0,0,
        0,177,178,1,0,0,0,178,33,1,0,0,0,179,180,5,25,0,0,180,182,5,40,0,
        0,181,183,7,4,0,0,182,181,1,0,0,0,182,183,1,0,0,0,183,35,1,0,0,0,
        184,185,5,26,0,0,185,187,5,39,0,0,186,188,5,1,0,0,187,186,1,0,0,
        0,187,188,1,0,0,0,188,37,1,0,0,0,189,191,5,33,0,0,190,192,5,82,0,
        0,191,190,1,0,0,0,191,192,1,0,0,0,192,196,1,0,0,0,193,195,5,80,0,
        0,194,193,1,0,0,0,195,198,1,0,0,0,196,194,1,0,0,0,196,197,1,0,0,
        0,197,200,1,0,0,0,198,196,1,0,0,0,199,201,5,81,0,0,200,199,1,0,0,
        0,200,201,1,0,0,0,201,203,1,0,0,0,202,204,5,1,0,0,203,202,1,0,0,
        0,203,204,1,0,0,0,204,39,1,0,0,0,36,52,59,63,66,70,73,78,83,91,95,
        98,101,104,111,114,117,122,125,135,139,142,145,150,153,157,160,166,
        169,174,177,182,187,191,196,200,203
    ]

class BaseParser ( Parser ):

    grammarFileName = "BaseParser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'\\n'", "<INVALID>", "<INVALID>", "':'", 
                     "<INVALID>", "'.'", "'/'", "'('", "')'", "'['", "']'", 
                     "'\"'", "'''", "'\\'", "<INVALID>", "<INVALID>", "'QUIT'", 
                     "'USE'", "'API'", "'SQL'", "<INVALID>", "'SPOOL'", 
                     "<INVALID>", "'SLEEP'", "<INVALID>", "'> {%'", "'ASSERT'", 
                     "'_START'", "'_LOAD'", "'_HOST'", "'_IF'", "'_ENDIF'", 
                     "'_SET'", "'_LOOP'", "'_WHENEVER'", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "'LOOP'", "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "'\"\"\"'", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "'BEGIN'", "'UNTIL'", "<INVALID>", "<INVALID>", 
                     "'BREAK'", "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "'ERROR'" ]

    symbolicNames = [ "<INVALID>", "CRLF", "COMMA", "SEMICOLON", "COLON", 
                      "AT", "DOT", "SLASH", "BRACKET_OPEN", "BRACKET_CLOSE", 
                      "SQUARE_OPEN", "SQUARE_CLOSE", "DOUBLE_QUOTE", "SINGLE_QUOTE", 
                      "ESCAPE", "SPACE", "EXIT", "QUIT", "USE", "API", "SQL", 
                      "CONTINUE", "SPOOL", "END", "SLEEP", "ECHO_OPEN", 
                      "SCRIPT_OPEN", "ASSERT", "START", "LOAD", "HOST", 
                      "IF", "ENDIF", "SET", "LOOP", "WHENEVER", "INT", "DECIMAL", 
                      "String", "ScriptBlock", "EchoBlock", "ASSERT_SPACE", 
                      "ASSERT_OPEN", "ASSERT_CLOSE", "ASSERT_EXPRESSION", 
                      "LOAD_SPACE", "LOAD_OPTION", "LOAD_EXPRESSION", "LOAD_CRLF", 
                      "START_SPACE", "START_LOOP", "START_INT", "START_COMMA", 
                      "START_EXPRESSION", "START_CRLF", "HOST_SPACE", "HOST_TAG", 
                      "HOST_BLOCK", "IF_SPACE", "IF_OPEN", "IF_CLOSE", "IF_EXPRESSION", 
                      "LOOP_SEMICOLON", "LOOP_SPACE", "LOOP_BEGIN", "LOOP_UNTIL", 
                      "LOOP_OPEN", "LOOP_CLOSE", "LOOP_BREAK", "LOOP_END", 
                      "LOOP_CONTINUE", "LOOP_EXPRESSION", "LOOP_CRLF", "WHENEVER_SPACE", 
                      "WHENEVER_ERROR", "WHENEVER_SEMICOLON", "WHENEVER_CONTINUE", 
                      "WHENEVER_EXIT", "WHENEVER_CRLF", "SET_SPACE", "SET_EXPRESSION", 
                      "SET_SEMICOLON", "SET_AT", "SET_CRLF" ]

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
    RULE_assert = 10
    RULE_host = 11
    RULE_loop = 12
    RULE_if = 13
    RULE_endif = 14
    RULE_whenever = 15
    RULE_spool = 16
    RULE_echo = 17
    RULE_script = 18
    RULE_set = 19

    ruleNames =  [ "prog", "baseCommand", "singleExpression", "expression", 
                   "exit", "quit", "use", "sleep", "start", "load", "assert", 
                   "host", "loop", "if", "endif", "whenever", "spool", "echo", 
                   "script", "set" ]

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
    CONTINUE=21
    SPOOL=22
    END=23
    SLEEP=24
    ECHO_OPEN=25
    SCRIPT_OPEN=26
    ASSERT=27
    START=28
    LOAD=29
    HOST=30
    IF=31
    ENDIF=32
    SET=33
    LOOP=34
    WHENEVER=35
    INT=36
    DECIMAL=37
    String=38
    ScriptBlock=39
    EchoBlock=40
    ASSERT_SPACE=41
    ASSERT_OPEN=42
    ASSERT_CLOSE=43
    ASSERT_EXPRESSION=44
    LOAD_SPACE=45
    LOAD_OPTION=46
    LOAD_EXPRESSION=47
    LOAD_CRLF=48
    START_SPACE=49
    START_LOOP=50
    START_INT=51
    START_COMMA=52
    START_EXPRESSION=53
    START_CRLF=54
    HOST_SPACE=55
    HOST_TAG=56
    HOST_BLOCK=57
    IF_SPACE=58
    IF_OPEN=59
    IF_CLOSE=60
    IF_EXPRESSION=61
    LOOP_SEMICOLON=62
    LOOP_SPACE=63
    LOOP_BEGIN=64
    LOOP_UNTIL=65
    LOOP_OPEN=66
    LOOP_CLOSE=67
    LOOP_BREAK=68
    LOOP_END=69
    LOOP_CONTINUE=70
    LOOP_EXPRESSION=71
    LOOP_CRLF=72
    WHENEVER_SPACE=73
    WHENEVER_ERROR=74
    WHENEVER_SEMICOLON=75
    WHENEVER_CONTINUE=76
    WHENEVER_EXIT=77
    WHENEVER_CRLF=78
    SET_SPACE=79
    SET_EXPRESSION=80
    SET_SEMICOLON=81
    SET_AT=82
    SET_CRLF=83

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
            self.state = 40
            self.baseCommand()
            self.state = 41
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


        def start(self):
            return self.getTypedRuleContext(BaseParser.StartContext,0)


        def loop(self):
            return self.getTypedRuleContext(BaseParser.LoopContext,0)


        def if_(self):
            return self.getTypedRuleContext(BaseParser.IfContext,0)


        def endif(self):
            return self.getTypedRuleContext(BaseParser.EndifContext,0)


        def whenever(self):
            return self.getTypedRuleContext(BaseParser.WheneverContext,0)


        def set_(self):
            return self.getTypedRuleContext(BaseParser.SetContext,0)


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
            self.state = 52
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [27]:
                self.enterOuterAlt(localctx, 1)
                self.state = 43
                self.assert_()
                pass
            elif token in [29]:
                self.enterOuterAlt(localctx, 2)
                self.state = 44
                self.load()
                pass
            elif token in [30]:
                self.enterOuterAlt(localctx, 3)
                self.state = 45
                self.host()
                pass
            elif token in [28]:
                self.enterOuterAlt(localctx, 4)
                self.state = 46
                self.start()
                pass
            elif token in [34]:
                self.enterOuterAlt(localctx, 5)
                self.state = 47
                self.loop()
                pass
            elif token in [31]:
                self.enterOuterAlt(localctx, 6)
                self.state = 48
                self.if_()
                pass
            elif token in [32]:
                self.enterOuterAlt(localctx, 7)
                self.state = 49
                self.endif()
                pass
            elif token in [35]:
                self.enterOuterAlt(localctx, 8)
                self.state = 50
                self.whenever()
                pass
            elif token in [33]:
                self.enterOuterAlt(localctx, 9)
                self.state = 51
                self.set_()
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
            self.state = 54
            _la = self._input.LA(1)
            if not(((_la) & ~0x3f) == 0 and ((1 << _la) & 274877939648) != 0):
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
            self.state = 57 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 56
                _la = self._input.LA(1)
                if not(((_la) & ~0x3f) == 0 and ((1 << _la) & 274877939664) != 0):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 59 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (((_la) & ~0x3f) == 0 and ((1 << _la) & 274877939664) != 0):
                    break

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
            self.state = 61
            self.match(BaseParser.EXIT)
            self.state = 63
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==36:
                self.state = 62
                self.match(BaseParser.INT)


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
            self.state = 68
            self.match(BaseParser.QUIT)
            self.state = 70
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==36:
                self.state = 69
                self.match(BaseParser.INT)


            self.state = 73
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==1:
                self.state = 72
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
            self.state = 75
            self.match(BaseParser.USE)
            self.state = 76
            _la = self._input.LA(1)
            if not(_la==19 or _la==20):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 78
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==1:
                self.state = 77
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
            self.state = 80
            self.match(BaseParser.SLEEP)
            self.state = 81
            self.match(BaseParser.INT)
            self.state = 83
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==1:
                self.state = 82
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

        def START_EXPRESSION(self, i:int=None):
            if i is None:
                return self.getTokens(BaseParser.START_EXPRESSION)
            else:
                return self.getToken(BaseParser.START_EXPRESSION, i)

        def START_COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(BaseParser.START_COMMA)
            else:
                return self.getToken(BaseParser.START_COMMA, i)

        def START_LOOP(self):
            return self.getToken(BaseParser.START_LOOP, 0)

        def START_INT(self):
            return self.getToken(BaseParser.START_INT, 0)

        def SEMICOLON(self):
            return self.getToken(BaseParser.SEMICOLON, 0)

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
            self.state = 85
            self.match(BaseParser.START)
            self.state = 86
            self.match(BaseParser.START_EXPRESSION)
            self.state = 91
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==52:
                self.state = 87
                self.match(BaseParser.START_COMMA)
                self.state = 88
                self.match(BaseParser.START_EXPRESSION)
                self.state = 93
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 95
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==50:
                self.state = 94
                self.match(BaseParser.START_LOOP)


            self.state = 98
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==51:
                self.state = 97
                self.match(BaseParser.START_INT)


            self.state = 101
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==3:
                self.state = 100
                self.match(BaseParser.SEMICOLON)


            self.state = 104
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==1:
                self.state = 103
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
            self.state = 106
            self.match(BaseParser.LOAD)
            self.state = 107
            self.match(BaseParser.LOAD_OPTION)
            self.state = 109 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 108
                self.match(BaseParser.LOAD_EXPRESSION)
                self.state = 111 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==47):
                    break

            self.state = 114
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==3:
                self.state = 113
                self.match(BaseParser.SEMICOLON)


            self.state = 117
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==1:
                self.state = 116
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
        self.enterRule(localctx, 20, self.RULE_assert)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 119
            self.match(BaseParser.ASSERT)
            self.state = 120
            self.match(BaseParser.ASSERT_EXPRESSION)
            self.state = 122
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==3:
                self.state = 121
                self.match(BaseParser.SEMICOLON)


            self.state = 125
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==1:
                self.state = 124
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
        self.enterRule(localctx, 22, self.RULE_host)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 127
            self.match(BaseParser.HOST)
            self.state = 128
            self.match(BaseParser.HOST_BLOCK)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LoopContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LOOP(self):
            return self.getToken(BaseParser.LOOP, 0)

        def LOOP_BREAK(self):
            return self.getToken(BaseParser.LOOP_BREAK, 0)

        def LOOP_END(self):
            return self.getToken(BaseParser.LOOP_END, 0)

        def LOOP_CONTINUE(self):
            return self.getToken(BaseParser.LOOP_CONTINUE, 0)

        def LOOP_SEMICOLON(self):
            return self.getToken(BaseParser.LOOP_SEMICOLON, 0)

        def CRLF(self):
            return self.getToken(BaseParser.CRLF, 0)

        def LOOP_UNTIL(self):
            return self.getToken(BaseParser.LOOP_UNTIL, 0)

        def LOOP_EXPRESSION(self):
            return self.getToken(BaseParser.LOOP_EXPRESSION, 0)

        def LOOP_BEGIN(self):
            return self.getToken(BaseParser.LOOP_BEGIN, 0)

        def getRuleIndex(self):
            return BaseParser.RULE_loop

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLoop" ):
                return visitor.visitLoop(self)
            else:
                return visitor.visitChildren(self)




    def loop(self):

        localctx = BaseParser.LoopContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_loop)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 130
            self.match(BaseParser.LOOP)
            self.state = 139
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [68]:
                self.state = 131
                self.match(BaseParser.LOOP_BREAK)
                pass
            elif token in [69]:
                self.state = 132
                self.match(BaseParser.LOOP_END)
                pass
            elif token in [70]:
                self.state = 133
                self.match(BaseParser.LOOP_CONTINUE)
                pass
            elif token in [64, 65]:
                self.state = 135
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==64:
                    self.state = 134
                    self.match(BaseParser.LOOP_BEGIN)


                self.state = 137
                self.match(BaseParser.LOOP_UNTIL)
                self.state = 138
                self.match(BaseParser.LOOP_EXPRESSION)
                pass
            else:
                raise NoViableAltException(self)

            self.state = 142
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==62:
                self.state = 141
                self.match(BaseParser.LOOP_SEMICOLON)


            self.state = 145
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==1:
                self.state = 144
                self.match(BaseParser.CRLF)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class IfContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IF(self):
            return self.getToken(BaseParser.IF, 0)

        def IF_EXPRESSION(self):
            return self.getToken(BaseParser.IF_EXPRESSION, 0)

        def SEMICOLON(self):
            return self.getToken(BaseParser.SEMICOLON, 0)

        def CRLF(self):
            return self.getToken(BaseParser.CRLF, 0)

        def getRuleIndex(self):
            return BaseParser.RULE_if

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitIf" ):
                return visitor.visitIf(self)
            else:
                return visitor.visitChildren(self)




    def if_(self):

        localctx = BaseParser.IfContext(self, self._ctx, self.state)
        self.enterRule(localctx, 26, self.RULE_if)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 147
            self.match(BaseParser.IF)
            self.state = 148
            self.match(BaseParser.IF_EXPRESSION)
            self.state = 150
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==3:
                self.state = 149
                self.match(BaseParser.SEMICOLON)


            self.state = 153
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==1:
                self.state = 152
                self.match(BaseParser.CRLF)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class EndifContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ENDIF(self):
            return self.getToken(BaseParser.ENDIF, 0)

        def SEMICOLON(self):
            return self.getToken(BaseParser.SEMICOLON, 0)

        def CRLF(self):
            return self.getToken(BaseParser.CRLF, 0)

        def getRuleIndex(self):
            return BaseParser.RULE_endif

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitEndif" ):
                return visitor.visitEndif(self)
            else:
                return visitor.visitChildren(self)




    def endif(self):

        localctx = BaseParser.EndifContext(self, self._ctx, self.state)
        self.enterRule(localctx, 28, self.RULE_endif)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 155
            self.match(BaseParser.ENDIF)
            self.state = 157
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==3:
                self.state = 156
                self.match(BaseParser.SEMICOLON)


            self.state = 160
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==1:
                self.state = 159
                self.match(BaseParser.CRLF)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class WheneverContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def WHENEVER(self):
            return self.getToken(BaseParser.WHENEVER, 0)

        def WHENEVER_ERROR(self):
            return self.getToken(BaseParser.WHENEVER_ERROR, 0)

        def WHENEVER_CONTINUE(self):
            return self.getToken(BaseParser.WHENEVER_CONTINUE, 0)

        def WHENEVER_EXIT(self):
            return self.getToken(BaseParser.WHENEVER_EXIT, 0)

        def WHENEVER_SEMICOLON(self):
            return self.getToken(BaseParser.WHENEVER_SEMICOLON, 0)

        def CRLF(self):
            return self.getToken(BaseParser.CRLF, 0)

        def getRuleIndex(self):
            return BaseParser.RULE_whenever

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitWhenever" ):
                return visitor.visitWhenever(self)
            else:
                return visitor.visitChildren(self)




    def whenever(self):

        localctx = BaseParser.WheneverContext(self, self._ctx, self.state)
        self.enterRule(localctx, 30, self.RULE_whenever)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 162
            self.match(BaseParser.WHENEVER)
            self.state = 163
            self.match(BaseParser.WHENEVER_ERROR)
            self.state = 164
            _la = self._input.LA(1)
            if not(_la==76 or _la==77):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 166
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==75:
                self.state = 165
                self.match(BaseParser.WHENEVER_SEMICOLON)


            self.state = 169
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==1:
                self.state = 168
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
        self.enterRule(localctx, 32, self.RULE_spool)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 171
            self.match(BaseParser.SPOOL)
            self.state = 172
            self.match(BaseParser.String)
            self.state = 174
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==3:
                self.state = 173
                self.match(BaseParser.SEMICOLON)


            self.state = 177
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==1:
                self.state = 176
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
        self.enterRule(localctx, 34, self.RULE_echo)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 179
            self.match(BaseParser.ECHO_OPEN)
            self.state = 180
            self.match(BaseParser.EchoBlock)
            self.state = 182
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,30,self._ctx)
            if la_ == 1:
                self.state = 181
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
        self.enterRule(localctx, 36, self.RULE_script)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 184
            self.match(BaseParser.SCRIPT_OPEN)
            self.state = 185
            self.match(BaseParser.ScriptBlock)
            self.state = 187
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==1:
                self.state = 186
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

        def SET_AT(self):
            return self.getToken(BaseParser.SET_AT, 0)

        def SET_EXPRESSION(self, i:int=None):
            if i is None:
                return self.getTokens(BaseParser.SET_EXPRESSION)
            else:
                return self.getToken(BaseParser.SET_EXPRESSION, i)

        def SET_SEMICOLON(self):
            return self.getToken(BaseParser.SET_SEMICOLON, 0)

        def CRLF(self):
            return self.getToken(BaseParser.CRLF, 0)

        def getRuleIndex(self):
            return BaseParser.RULE_set

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSet" ):
                return visitor.visitSet(self)
            else:
                return visitor.visitChildren(self)




    def set_(self):

        localctx = BaseParser.SetContext(self, self._ctx, self.state)
        self.enterRule(localctx, 38, self.RULE_set)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 189
            self.match(BaseParser.SET)
            self.state = 191
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==82:
                self.state = 190
                self.match(BaseParser.SET_AT)


            self.state = 196
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==80:
                self.state = 193
                self.match(BaseParser.SET_EXPRESSION)
                self.state = 198
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 200
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==81:
                self.state = 199
                self.match(BaseParser.SET_SEMICOLON)


            self.state = 203
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==1:
                self.state = 202
                self.match(BaseParser.CRLF)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





