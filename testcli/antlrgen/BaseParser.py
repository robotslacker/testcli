# Generated from BaseParser.g4 by ANTLR 4.11.1
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
        4,1,84,212,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,13,
        2,14,7,14,2,15,7,15,2,16,7,16,2,17,7,17,1,0,1,0,1,0,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,1,56,8,1,1,
        2,1,2,3,2,60,8,2,1,2,3,2,63,8,2,1,2,3,2,66,8,2,1,3,1,3,3,3,70,8,
        3,1,3,3,3,73,8,3,1,3,3,3,76,8,3,1,4,1,4,1,4,3,4,81,8,4,1,4,3,4,84,
        8,4,1,5,1,5,1,5,3,5,89,8,5,1,5,3,5,92,8,5,1,6,1,6,1,6,1,6,5,6,98,
        8,6,10,6,12,6,101,9,6,1,6,3,6,104,8,6,1,6,3,6,107,8,6,1,6,3,6,110,
        8,6,1,6,3,6,113,8,6,1,7,1,7,1,7,4,7,118,8,7,11,7,12,7,119,1,7,3,
        7,123,8,7,1,7,3,7,126,8,7,1,8,1,8,1,8,3,8,131,8,8,1,8,3,8,134,8,
        8,1,9,1,9,1,9,1,10,1,10,1,10,1,10,1,10,1,10,1,10,3,10,146,8,10,1,
        10,3,10,149,8,10,1,10,3,10,152,8,10,1,11,1,11,1,11,3,11,157,8,11,
        1,11,3,11,160,8,11,1,12,1,12,3,12,164,8,12,1,12,3,12,167,8,12,1,
        13,1,13,1,13,1,13,3,13,173,8,13,1,13,3,13,176,8,13,1,14,1,14,1,14,
        3,14,181,8,14,1,14,3,14,184,8,14,1,15,1,15,1,15,3,15,189,8,15,1,
        16,1,16,1,16,3,16,194,8,16,1,17,1,17,3,17,198,8,17,1,17,5,17,201,
        8,17,10,17,12,17,204,9,17,1,17,3,17,207,8,17,1,17,3,17,210,8,17,
        1,17,0,0,18,0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,0,3,
        1,0,80,81,1,0,72,73,1,1,1,1,247,0,36,1,0,0,0,2,55,1,0,0,0,4,57,1,
        0,0,0,6,67,1,0,0,0,8,77,1,0,0,0,10,85,1,0,0,0,12,93,1,0,0,0,14,114,
        1,0,0,0,16,127,1,0,0,0,18,135,1,0,0,0,20,138,1,0,0,0,22,153,1,0,
        0,0,24,161,1,0,0,0,26,168,1,0,0,0,28,177,1,0,0,0,30,185,1,0,0,0,
        32,190,1,0,0,0,34,195,1,0,0,0,36,37,3,2,1,0,37,38,5,0,0,1,38,1,1,
        0,0,0,39,56,3,16,8,0,40,56,3,14,7,0,41,56,3,18,9,0,42,56,3,12,6,
        0,43,56,3,20,10,0,44,56,3,22,11,0,45,56,3,24,12,0,46,56,3,26,13,
        0,47,56,3,34,17,0,48,56,3,8,4,0,49,56,3,4,2,0,50,56,3,6,3,0,51,56,
        3,10,5,0,52,56,3,28,14,0,53,56,3,32,16,0,54,56,3,30,15,0,55,39,1,
        0,0,0,55,40,1,0,0,0,55,41,1,0,0,0,55,42,1,0,0,0,55,43,1,0,0,0,55,
        44,1,0,0,0,55,45,1,0,0,0,55,46,1,0,0,0,55,47,1,0,0,0,55,48,1,0,0,
        0,55,49,1,0,0,0,55,50,1,0,0,0,55,51,1,0,0,0,55,52,1,0,0,0,55,53,
        1,0,0,0,55,54,1,0,0,0,56,3,1,0,0,0,57,59,5,16,0,0,58,60,5,32,0,0,
        59,58,1,0,0,0,59,60,1,0,0,0,60,62,1,0,0,0,61,63,5,3,0,0,62,61,1,
        0,0,0,62,63,1,0,0,0,63,65,1,0,0,0,64,66,5,1,0,0,65,64,1,0,0,0,65,
        66,1,0,0,0,66,5,1,0,0,0,67,69,5,17,0,0,68,70,5,32,0,0,69,68,1,0,
        0,0,69,70,1,0,0,0,70,72,1,0,0,0,71,73,5,3,0,0,72,71,1,0,0,0,72,73,
        1,0,0,0,73,75,1,0,0,0,74,76,5,1,0,0,75,74,1,0,0,0,75,76,1,0,0,0,
        76,7,1,0,0,0,77,78,5,20,0,0,78,80,7,0,0,0,79,81,5,83,0,0,80,79,1,
        0,0,0,80,81,1,0,0,0,81,83,1,0,0,0,82,84,5,1,0,0,83,82,1,0,0,0,83,
        84,1,0,0,0,84,9,1,0,0,0,85,86,5,19,0,0,86,88,5,32,0,0,87,89,5,3,
        0,0,88,87,1,0,0,0,88,89,1,0,0,0,89,91,1,0,0,0,90,92,5,1,0,0,91,90,
        1,0,0,0,91,92,1,0,0,0,92,11,1,0,0,0,93,94,5,24,0,0,94,99,5,49,0,
        0,95,96,5,48,0,0,96,98,5,49,0,0,97,95,1,0,0,0,98,101,1,0,0,0,99,
        97,1,0,0,0,99,100,1,0,0,0,100,103,1,0,0,0,101,99,1,0,0,0,102,104,
        5,46,0,0,103,102,1,0,0,0,103,104,1,0,0,0,104,106,1,0,0,0,105,107,
        5,47,0,0,106,105,1,0,0,0,106,107,1,0,0,0,107,109,1,0,0,0,108,110,
        5,3,0,0,109,108,1,0,0,0,109,110,1,0,0,0,110,112,1,0,0,0,111,113,
        5,1,0,0,112,111,1,0,0,0,112,113,1,0,0,0,113,13,1,0,0,0,114,115,5,
        25,0,0,115,117,5,42,0,0,116,118,5,43,0,0,117,116,1,0,0,0,118,119,
        1,0,0,0,119,117,1,0,0,0,119,120,1,0,0,0,120,122,1,0,0,0,121,123,
        5,3,0,0,122,121,1,0,0,0,122,123,1,0,0,0,123,125,1,0,0,0,124,126,
        5,1,0,0,125,124,1,0,0,0,125,126,1,0,0,0,126,15,1,0,0,0,127,128,5,
        23,0,0,128,130,5,40,0,0,129,131,5,3,0,0,130,129,1,0,0,0,130,131,
        1,0,0,0,131,133,1,0,0,0,132,134,5,1,0,0,133,132,1,0,0,0,133,134,
        1,0,0,0,134,17,1,0,0,0,135,136,5,26,0,0,136,137,5,53,0,0,137,19,
        1,0,0,0,138,145,5,30,0,0,139,146,5,64,0,0,140,146,5,65,0,0,141,146,
        5,66,0,0,142,143,5,60,0,0,143,144,5,61,0,0,144,146,5,67,0,0,145,
        139,1,0,0,0,145,140,1,0,0,0,145,141,1,0,0,0,145,142,1,0,0,0,146,
        148,1,0,0,0,147,149,5,58,0,0,148,147,1,0,0,0,148,149,1,0,0,0,149,
        151,1,0,0,0,150,152,5,1,0,0,151,150,1,0,0,0,151,152,1,0,0,0,152,
        21,1,0,0,0,153,154,5,27,0,0,154,156,5,57,0,0,155,157,5,3,0,0,156,
        155,1,0,0,0,156,157,1,0,0,0,157,159,1,0,0,0,158,160,5,1,0,0,159,
        158,1,0,0,0,159,160,1,0,0,0,160,23,1,0,0,0,161,163,5,28,0,0,162,
        164,5,3,0,0,163,162,1,0,0,0,163,164,1,0,0,0,164,166,1,0,0,0,165,
        167,5,1,0,0,166,165,1,0,0,0,166,167,1,0,0,0,167,25,1,0,0,0,168,169,
        5,31,0,0,169,170,5,70,0,0,170,172,7,1,0,0,171,173,5,71,0,0,172,171,
        1,0,0,0,172,173,1,0,0,0,173,175,1,0,0,0,174,176,5,1,0,0,175,174,
        1,0,0,0,175,176,1,0,0,0,176,27,1,0,0,0,177,178,5,18,0,0,178,180,
        5,34,0,0,179,181,5,3,0,0,180,179,1,0,0,0,180,181,1,0,0,0,181,183,
        1,0,0,0,182,184,5,1,0,0,183,182,1,0,0,0,183,184,1,0,0,0,184,29,1,
        0,0,0,185,186,5,21,0,0,186,188,5,36,0,0,187,189,7,2,0,0,188,187,
        1,0,0,0,188,189,1,0,0,0,189,31,1,0,0,0,190,191,5,22,0,0,191,193,
        5,35,0,0,192,194,5,1,0,0,193,192,1,0,0,0,193,194,1,0,0,0,194,33,
        1,0,0,0,195,197,5,29,0,0,196,198,5,78,0,0,197,196,1,0,0,0,197,198,
        1,0,0,0,198,202,1,0,0,0,199,201,5,76,0,0,200,199,1,0,0,0,201,204,
        1,0,0,0,202,200,1,0,0,0,202,203,1,0,0,0,203,206,1,0,0,0,204,202,
        1,0,0,0,205,207,5,77,0,0,206,205,1,0,0,0,206,207,1,0,0,0,207,209,
        1,0,0,0,208,210,5,1,0,0,209,208,1,0,0,0,209,210,1,0,0,0,210,35,1,
        0,0,0,38,55,59,62,65,69,72,75,80,83,88,91,99,103,106,109,112,119,
        122,125,130,133,145,148,151,156,159,163,166,172,175,180,183,188,
        193,197,202,206,209
    ]

class BaseParser ( Parser ):

    grammarFileName = "BaseParser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'\\n'", "<INVALID>", "<INVALID>", "':'", 
                     "<INVALID>", "'.'", "'/'", "'('", "')'", "'['", "']'", 
                     "'\"'", "'''", "'\\'", "<INVALID>", "'_EXIT'", "'_QUIT'", 
                     "'_SPOOL'", "'_SLEEP'", "'_USE'", "<INVALID>", "'> {%'", 
                     "'_ASSERT'", "'_START'", "'_LOAD'", "'_HOST'", "'_IF'", 
                     "'_ENDIF'", "'_SET'", "'_LOOP'", "'_WHENEVER'", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "'LOOP'", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "'\"\"\"'", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "'BEGIN'", "'UNTIL'", "<INVALID>", 
                     "<INVALID>", "'BREAK'", "'END'", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "'ERROR'", "<INVALID>", "<INVALID>", 
                     "'EXIT'", "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "'API'", "'SQL'" ]

    symbolicNames = [ "<INVALID>", "CRLF", "COMMA", "SEMICOLON", "COLON", 
                      "AT", "DOT", "SLASH", "BRACKET_OPEN", "BRACKET_CLOSE", 
                      "SQUARE_OPEN", "SQUARE_CLOSE", "DOUBLE_QUOTE", "SINGLE_QUOTE", 
                      "ESCAPE", "SPACE", "EXIT", "QUIT", "SPOOL", "SLEEP", 
                      "USE", "ECHO_OPEN", "SCRIPT_OPEN", "ASSERT", "START", 
                      "LOAD", "HOST", "IF", "ENDIF", "SET", "LOOP", "WHENEVER", 
                      "INT", "DECIMAL", "String", "ScriptBlock", "EchoBlock", 
                      "ASSERT_SPACE", "ASSERT_OPEN", "ASSERT_CLOSE", "ASSERT_EXPRESSION", 
                      "LOAD_SPACE", "LOAD_OPTION", "LOAD_EXPRESSION", "LOAD_CRLF", 
                      "START_SPACE", "START_LOOP", "START_INT", "START_COMMA", 
                      "START_EXPRESSION", "START_CRLF", "HOST_SPACE", "HOST_TAG", 
                      "HOST_BLOCK", "IF_SPACE", "IF_OPEN", "IF_CLOSE", "IF_EXPRESSION", 
                      "LOOP_SEMICOLON", "LOOP_SPACE", "LOOP_BEGIN", "LOOP_UNTIL", 
                      "LOOP_OPEN", "LOOP_CLOSE", "LOOP_BREAK", "LOOP_END", 
                      "LOOP_CONTINUE", "LOOP_EXPRESSION", "LOOP_CRLF", "WHENEVER_SPACE", 
                      "WHENEVER_ERROR", "WHENEVER_SEMICOLON", "WHENEVER_CONTINUE", 
                      "WHENEVER_EXIT", "WHENEVER_CRLF", "SET_SPACE", "SET_EXPRESSION", 
                      "SET_SEMICOLON", "SET_AT", "SET_CRLF", "USE_API", 
                      "USE_SQL", "USE_SPACE", "USE_SEMICOLON", "USE_CRLF" ]

    RULE_prog = 0
    RULE_baseCommand = 1
    RULE_exit = 2
    RULE_quit = 3
    RULE_use = 4
    RULE_sleep = 5
    RULE_start = 6
    RULE_load = 7
    RULE_assert = 8
    RULE_host = 9
    RULE_loop = 10
    RULE_if = 11
    RULE_endif = 12
    RULE_whenever = 13
    RULE_spool = 14
    RULE_echo = 15
    RULE_script = 16
    RULE_set = 17

    ruleNames =  [ "prog", "baseCommand", "exit", "quit", "use", "sleep", 
                   "start", "load", "assert", "host", "loop", "if", "endif", 
                   "whenever", "spool", "echo", "script", "set" ]

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
    SPOOL=18
    SLEEP=19
    USE=20
    ECHO_OPEN=21
    SCRIPT_OPEN=22
    ASSERT=23
    START=24
    LOAD=25
    HOST=26
    IF=27
    ENDIF=28
    SET=29
    LOOP=30
    WHENEVER=31
    INT=32
    DECIMAL=33
    String=34
    ScriptBlock=35
    EchoBlock=36
    ASSERT_SPACE=37
    ASSERT_OPEN=38
    ASSERT_CLOSE=39
    ASSERT_EXPRESSION=40
    LOAD_SPACE=41
    LOAD_OPTION=42
    LOAD_EXPRESSION=43
    LOAD_CRLF=44
    START_SPACE=45
    START_LOOP=46
    START_INT=47
    START_COMMA=48
    START_EXPRESSION=49
    START_CRLF=50
    HOST_SPACE=51
    HOST_TAG=52
    HOST_BLOCK=53
    IF_SPACE=54
    IF_OPEN=55
    IF_CLOSE=56
    IF_EXPRESSION=57
    LOOP_SEMICOLON=58
    LOOP_SPACE=59
    LOOP_BEGIN=60
    LOOP_UNTIL=61
    LOOP_OPEN=62
    LOOP_CLOSE=63
    LOOP_BREAK=64
    LOOP_END=65
    LOOP_CONTINUE=66
    LOOP_EXPRESSION=67
    LOOP_CRLF=68
    WHENEVER_SPACE=69
    WHENEVER_ERROR=70
    WHENEVER_SEMICOLON=71
    WHENEVER_CONTINUE=72
    WHENEVER_EXIT=73
    WHENEVER_CRLF=74
    SET_SPACE=75
    SET_EXPRESSION=76
    SET_SEMICOLON=77
    SET_AT=78
    SET_CRLF=79
    USE_API=80
    USE_SQL=81
    USE_SPACE=82
    USE_SEMICOLON=83
    USE_CRLF=84

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
            self.state = 36
            self.baseCommand()
            self.state = 37
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


        def use(self):
            return self.getTypedRuleContext(BaseParser.UseContext,0)


        def exit(self):
            return self.getTypedRuleContext(BaseParser.ExitContext,0)


        def quit(self):
            return self.getTypedRuleContext(BaseParser.QuitContext,0)


        def sleep(self):
            return self.getTypedRuleContext(BaseParser.SleepContext,0)


        def spool(self):
            return self.getTypedRuleContext(BaseParser.SpoolContext,0)


        def script(self):
            return self.getTypedRuleContext(BaseParser.ScriptContext,0)


        def echo(self):
            return self.getTypedRuleContext(BaseParser.EchoContext,0)


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
            self.state = 55
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [23]:
                self.enterOuterAlt(localctx, 1)
                self.state = 39
                self.assert_()
                pass
            elif token in [25]:
                self.enterOuterAlt(localctx, 2)
                self.state = 40
                self.load()
                pass
            elif token in [26]:
                self.enterOuterAlt(localctx, 3)
                self.state = 41
                self.host()
                pass
            elif token in [24]:
                self.enterOuterAlt(localctx, 4)
                self.state = 42
                self.start()
                pass
            elif token in [30]:
                self.enterOuterAlt(localctx, 5)
                self.state = 43
                self.loop()
                pass
            elif token in [27]:
                self.enterOuterAlt(localctx, 6)
                self.state = 44
                self.if_()
                pass
            elif token in [28]:
                self.enterOuterAlt(localctx, 7)
                self.state = 45
                self.endif()
                pass
            elif token in [31]:
                self.enterOuterAlt(localctx, 8)
                self.state = 46
                self.whenever()
                pass
            elif token in [29]:
                self.enterOuterAlt(localctx, 9)
                self.state = 47
                self.set_()
                pass
            elif token in [20]:
                self.enterOuterAlt(localctx, 10)
                self.state = 48
                self.use()
                pass
            elif token in [16]:
                self.enterOuterAlt(localctx, 11)
                self.state = 49
                self.exit()
                pass
            elif token in [17]:
                self.enterOuterAlt(localctx, 12)
                self.state = 50
                self.quit()
                pass
            elif token in [19]:
                self.enterOuterAlt(localctx, 13)
                self.state = 51
                self.sleep()
                pass
            elif token in [18]:
                self.enterOuterAlt(localctx, 14)
                self.state = 52
                self.spool()
                pass
            elif token in [22]:
                self.enterOuterAlt(localctx, 15)
                self.state = 53
                self.script()
                pass
            elif token in [21]:
                self.enterOuterAlt(localctx, 16)
                self.state = 54
                self.echo()
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


    class ExitContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EXIT(self):
            return self.getToken(BaseParser.EXIT, 0)

        def INT(self):
            return self.getToken(BaseParser.INT, 0)

        def SEMICOLON(self):
            return self.getToken(BaseParser.SEMICOLON, 0)

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
        self.enterRule(localctx, 4, self.RULE_exit)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 57
            self.match(BaseParser.EXIT)
            self.state = 59
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==32:
                self.state = 58
                self.match(BaseParser.INT)


            self.state = 62
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==3:
                self.state = 61
                self.match(BaseParser.SEMICOLON)


            self.state = 65
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==1:
                self.state = 64
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

        def SEMICOLON(self):
            return self.getToken(BaseParser.SEMICOLON, 0)

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
        self.enterRule(localctx, 6, self.RULE_quit)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 67
            self.match(BaseParser.QUIT)
            self.state = 69
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==32:
                self.state = 68
                self.match(BaseParser.INT)


            self.state = 72
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==3:
                self.state = 71
                self.match(BaseParser.SEMICOLON)


            self.state = 75
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==1:
                self.state = 74
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

        def USE_API(self):
            return self.getToken(BaseParser.USE_API, 0)

        def USE_SQL(self):
            return self.getToken(BaseParser.USE_SQL, 0)

        def USE_SEMICOLON(self):
            return self.getToken(BaseParser.USE_SEMICOLON, 0)

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
        self.enterRule(localctx, 8, self.RULE_use)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 77
            self.match(BaseParser.USE)
            self.state = 78
            _la = self._input.LA(1)
            if not(_la==80 or _la==81):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 80
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==83:
                self.state = 79
                self.match(BaseParser.USE_SEMICOLON)


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


    class SleepContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def SLEEP(self):
            return self.getToken(BaseParser.SLEEP, 0)

        def INT(self):
            return self.getToken(BaseParser.INT, 0)

        def SEMICOLON(self):
            return self.getToken(BaseParser.SEMICOLON, 0)

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
        self.enterRule(localctx, 10, self.RULE_sleep)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 85
            self.match(BaseParser.SLEEP)
            self.state = 86
            self.match(BaseParser.INT)
            self.state = 88
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==3:
                self.state = 87
                self.match(BaseParser.SEMICOLON)


            self.state = 91
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==1:
                self.state = 90
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
        self.enterRule(localctx, 12, self.RULE_start)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 93
            self.match(BaseParser.START)
            self.state = 94
            self.match(BaseParser.START_EXPRESSION)
            self.state = 99
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==48:
                self.state = 95
                self.match(BaseParser.START_COMMA)
                self.state = 96
                self.match(BaseParser.START_EXPRESSION)
                self.state = 101
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 103
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==46:
                self.state = 102
                self.match(BaseParser.START_LOOP)


            self.state = 106
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==47:
                self.state = 105
                self.match(BaseParser.START_INT)


            self.state = 109
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==3:
                self.state = 108
                self.match(BaseParser.SEMICOLON)


            self.state = 112
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==1:
                self.state = 111
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
        self.enterRule(localctx, 14, self.RULE_load)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 114
            self.match(BaseParser.LOAD)
            self.state = 115
            self.match(BaseParser.LOAD_OPTION)
            self.state = 117 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 116
                self.match(BaseParser.LOAD_EXPRESSION)
                self.state = 119 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==43):
                    break

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
        self.enterRule(localctx, 16, self.RULE_assert)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 127
            self.match(BaseParser.ASSERT)
            self.state = 128
            self.match(BaseParser.ASSERT_EXPRESSION)
            self.state = 130
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==3:
                self.state = 129
                self.match(BaseParser.SEMICOLON)


            self.state = 133
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==1:
                self.state = 132
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
        self.enterRule(localctx, 18, self.RULE_host)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 135
            self.match(BaseParser.HOST)
            self.state = 136
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

        def LOOP_BEGIN(self):
            return self.getToken(BaseParser.LOOP_BEGIN, 0)

        def LOOP_UNTIL(self):
            return self.getToken(BaseParser.LOOP_UNTIL, 0)

        def LOOP_EXPRESSION(self):
            return self.getToken(BaseParser.LOOP_EXPRESSION, 0)

        def LOOP_SEMICOLON(self):
            return self.getToken(BaseParser.LOOP_SEMICOLON, 0)

        def CRLF(self):
            return self.getToken(BaseParser.CRLF, 0)

        def getRuleIndex(self):
            return BaseParser.RULE_loop

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLoop" ):
                return visitor.visitLoop(self)
            else:
                return visitor.visitChildren(self)




    def loop(self):

        localctx = BaseParser.LoopContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_loop)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 138
            self.match(BaseParser.LOOP)
            self.state = 145
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [64]:
                self.state = 139
                self.match(BaseParser.LOOP_BREAK)
                pass
            elif token in [65]:
                self.state = 140
                self.match(BaseParser.LOOP_END)
                pass
            elif token in [66]:
                self.state = 141
                self.match(BaseParser.LOOP_CONTINUE)
                pass
            elif token in [60]:
                self.state = 142
                self.match(BaseParser.LOOP_BEGIN)
                self.state = 143
                self.match(BaseParser.LOOP_UNTIL)
                self.state = 144
                self.match(BaseParser.LOOP_EXPRESSION)
                pass
            else:
                raise NoViableAltException(self)

            self.state = 148
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==58:
                self.state = 147
                self.match(BaseParser.LOOP_SEMICOLON)


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
        self.enterRule(localctx, 22, self.RULE_if)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 153
            self.match(BaseParser.IF)
            self.state = 154
            self.match(BaseParser.IF_EXPRESSION)
            self.state = 156
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==3:
                self.state = 155
                self.match(BaseParser.SEMICOLON)


            self.state = 159
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==1:
                self.state = 158
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
        self.enterRule(localctx, 24, self.RULE_endif)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 161
            self.match(BaseParser.ENDIF)
            self.state = 163
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==3:
                self.state = 162
                self.match(BaseParser.SEMICOLON)


            self.state = 166
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==1:
                self.state = 165
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
        self.enterRule(localctx, 26, self.RULE_whenever)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 168
            self.match(BaseParser.WHENEVER)
            self.state = 169
            self.match(BaseParser.WHENEVER_ERROR)
            self.state = 170
            _la = self._input.LA(1)
            if not(_la==72 or _la==73):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 172
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==71:
                self.state = 171
                self.match(BaseParser.WHENEVER_SEMICOLON)


            self.state = 175
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==1:
                self.state = 174
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
        self.enterRule(localctx, 28, self.RULE_spool)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 177
            self.match(BaseParser.SPOOL)
            self.state = 178
            self.match(BaseParser.String)
            self.state = 180
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==3:
                self.state = 179
                self.match(BaseParser.SEMICOLON)


            self.state = 183
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==1:
                self.state = 182
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
        self.enterRule(localctx, 30, self.RULE_echo)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 185
            self.match(BaseParser.ECHO_OPEN)
            self.state = 186
            self.match(BaseParser.EchoBlock)
            self.state = 188
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,32,self._ctx)
            if la_ == 1:
                self.state = 187
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
        self.enterRule(localctx, 32, self.RULE_script)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 190
            self.match(BaseParser.SCRIPT_OPEN)
            self.state = 191
            self.match(BaseParser.ScriptBlock)
            self.state = 193
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==1:
                self.state = 192
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
        self.enterRule(localctx, 34, self.RULE_set)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 195
            self.match(BaseParser.SET)
            self.state = 197
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==78:
                self.state = 196
                self.match(BaseParser.SET_AT)


            self.state = 202
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==76:
                self.state = 199
                self.match(BaseParser.SET_EXPRESSION)
                self.state = 204
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 206
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==77:
                self.state = 205
                self.match(BaseParser.SET_SEMICOLON)


            self.state = 209
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==1:
                self.state = 208
                self.match(BaseParser.CRLF)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





