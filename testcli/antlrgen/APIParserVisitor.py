# Generated from APIParser.g4 by ANTLR 4.11.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .APIParser import APIParser
else:
    from APIParser import APIParser

# This class defines a complete generic visitor for a parse tree produced by APIParser.

class APIParserVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by APIParser#prog.
    def visitProg(self, ctx:APIParser.ProgContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#command.
    def visitCommand(self, ctx:APIParser.CommandContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#apiset.
    def visitApiset(self, ctx:APIParser.ApisetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#session.
    def visitSession(self, ctx:APIParser.SessionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#http.
    def visitHttp(self, ctx:APIParser.HttpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#httpMessage.
    def visitHttpMessage(self, ctx:APIParser.HttpMessageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#httpRequestLine.
    def visitHttpRequestLine(self, ctx:APIParser.HttpRequestLineContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#httpMethod.
    def visitHttpMethod(self, ctx:APIParser.HttpMethodContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#httpRequestTarget.
    def visitHttpRequestTarget(self, ctx:APIParser.HttpRequestTargetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#httpHeaderFields.
    def visitHttpHeaderFields(self, ctx:APIParser.HttpHeaderFieldsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#httpHeaderField.
    def visitHttpHeaderField(self, ctx:APIParser.HttpHeaderFieldContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#httpHeaderFieldName.
    def visitHttpHeaderFieldName(self, ctx:APIParser.HttpHeaderFieldNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#httpHeaderFieldValue.
    def visitHttpHeaderFieldValue(self, ctx:APIParser.HttpHeaderFieldValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#httpMessageBody.
    def visitHttpMessageBody(self, ctx:APIParser.HttpMessageBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#httpMultipart.
    def visitHttpMultipart(self, ctx:APIParser.HttpMultipartContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#httpMultipartBoundary.
    def visitHttpMultipartBoundary(self, ctx:APIParser.HttpMultipartBoundaryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#httpBoundaryDelimiter.
    def visitHttpBoundaryDelimiter(self, ctx:APIParser.HttpBoundaryDelimiterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#httpMessageBodyContent.
    def visitHttpMessageBodyContent(self, ctx:APIParser.HttpMessageBodyContentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#httpMessageBodyOperate.
    def visitHttpMessageBodyOperate(self, ctx:APIParser.HttpMessageBodyOperateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#httpMessageBodyOther.
    def visitHttpMessageBodyOther(self, ctx:APIParser.HttpMessageBodyOtherContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#baseCommand.
    def visitBaseCommand(self, ctx:APIParser.BaseCommandContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#exit.
    def visitExit(self, ctx:APIParser.ExitContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#quit.
    def visitQuit(self, ctx:APIParser.QuitContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#use.
    def visitUse(self, ctx:APIParser.UseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#sleep.
    def visitSleep(self, ctx:APIParser.SleepContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#start.
    def visitStart(self, ctx:APIParser.StartContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#load.
    def visitLoad(self, ctx:APIParser.LoadContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#assert.
    def visitAssert(self, ctx:APIParser.AssertContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#host.
    def visitHost(self, ctx:APIParser.HostContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#loop.
    def visitLoop(self, ctx:APIParser.LoopContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#if.
    def visitIf(self, ctx:APIParser.IfContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#endif.
    def visitEndif(self, ctx:APIParser.EndifContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#whenever.
    def visitWhenever(self, ctx:APIParser.WheneverContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#spool.
    def visitSpool(self, ctx:APIParser.SpoolContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#echo.
    def visitEcho(self, ctx:APIParser.EchoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#script.
    def visitScript(self, ctx:APIParser.ScriptContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#set.
    def visitSet(self, ctx:APIParser.SetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#ssh.
    def visitSsh(self, ctx:APIParser.SshContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#job.
    def visitJob(self, ctx:APIParser.JobContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#compare.
    def visitCompare(self, ctx:APIParser.CompareContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#data.
    def visitData(self, ctx:APIParser.DataContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#help.
    def visitHelp(self, ctx:APIParser.HelpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#monitor.
    def visitMonitor(self, ctx:APIParser.MonitorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#plugin.
    def visitPlugin(self, ctx:APIParser.PluginContext):
        return self.visitChildren(ctx)



del APIParser