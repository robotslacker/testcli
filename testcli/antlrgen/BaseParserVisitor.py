# Generated from BaseParser.g4 by ANTLR 4.11.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .BaseParser import BaseParser
else:
    from BaseParser import BaseParser

# This class defines a complete generic visitor for a parse tree produced by BaseParser.

class BaseParserVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by BaseParser#prog.
    def visitProg(self, ctx:BaseParser.ProgContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by BaseParser#baseCommand.
    def visitBaseCommand(self, ctx:BaseParser.BaseCommandContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by BaseParser#exit.
    def visitExit(self, ctx:BaseParser.ExitContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by BaseParser#quit.
    def visitQuit(self, ctx:BaseParser.QuitContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by BaseParser#use.
    def visitUse(self, ctx:BaseParser.UseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by BaseParser#sleep.
    def visitSleep(self, ctx:BaseParser.SleepContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by BaseParser#start.
    def visitStart(self, ctx:BaseParser.StartContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by BaseParser#load.
    def visitLoad(self, ctx:BaseParser.LoadContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by BaseParser#assert.
    def visitAssert(self, ctx:BaseParser.AssertContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by BaseParser#host.
    def visitHost(self, ctx:BaseParser.HostContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by BaseParser#loop.
    def visitLoop(self, ctx:BaseParser.LoopContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by BaseParser#if.
    def visitIf(self, ctx:BaseParser.IfContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by BaseParser#endif.
    def visitEndif(self, ctx:BaseParser.EndifContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by BaseParser#whenever.
    def visitWhenever(self, ctx:BaseParser.WheneverContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by BaseParser#spool.
    def visitSpool(self, ctx:BaseParser.SpoolContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by BaseParser#echo.
    def visitEcho(self, ctx:BaseParser.EchoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by BaseParser#script.
    def visitScript(self, ctx:BaseParser.ScriptContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by BaseParser#set.
    def visitSet(self, ctx:BaseParser.SetContext):
        return self.visitChildren(ctx)



del BaseParser