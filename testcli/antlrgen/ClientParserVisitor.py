# Generated from C:/Work/testcli/testcli/antlr\ClientParser.g4 by ANTLR 4.10.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .ClientParser import ClientParser
else:
    from ClientParser import ClientParser

# This class defines a complete generic visitor for a parse tree produced by ClientParser.

class ClientParserVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by ClientParser#prog.
    def visitProg(self, ctx:ClientParser.ProgContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#command.
    def visitCommand(self, ctx:ClientParser.CommandContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#exit.
    def visitExit(self, ctx:ClientParser.ExitContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#quit.
    def visitQuit(self, ctx:ClientParser.QuitContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#use.
    def visitUse(self, ctx:ClientParser.UseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#sleep.
    def visitSleep(self, ctx:ClientParser.SleepContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#connect.
    def visitConnect(self, ctx:ClientParser.ConnectContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#connectlocal.
    def visitConnectlocal(self, ctx:ClientParser.ConnectlocalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#connectjdbc.
    def visitConnectjdbc(self, ctx:ClientParser.ConnectjdbcContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#connectUserInfo.
    def visitConnectUserInfo(self, ctx:ClientParser.ConnectUserInfoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#connectDriver.
    def visitConnectDriver(self, ctx:ClientParser.ConnectDriverContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#connectDriverSchema.
    def visitConnectDriverSchema(self, ctx:ClientParser.ConnectDriverSchemaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#connectDriverType.
    def visitConnectDriverType(self, ctx:ClientParser.ConnectDriverTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#connectHost.
    def visitConnectHost(self, ctx:ClientParser.ConnectHostContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#connectUser.
    def visitConnectUser(self, ctx:ClientParser.ConnectUserContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#connectPassword.
    def visitConnectPassword(self, ctx:ClientParser.ConnectPasswordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#connectPort.
    def visitConnectPort(self, ctx:ClientParser.ConnectPortContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#connectService.
    def visitConnectService(self, ctx:ClientParser.ConnectServiceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#connectlocalService.
    def visitConnectlocalService(self, ctx:ClientParser.ConnectlocalServiceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#connectParameterName.
    def visitConnectParameterName(self, ctx:ClientParser.ConnectParameterNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#connectParameterValue.
    def visitConnectParameterValue(self, ctx:ClientParser.ConnectParameterValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#connectParameter.
    def visitConnectParameter(self, ctx:ClientParser.ConnectParameterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#connectParameters.
    def visitConnectParameters(self, ctx:ClientParser.ConnectParametersContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#disconnect.
    def visitDisconnect(self, ctx:ClientParser.DisconnectContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#session.
    def visitSession(self, ctx:ClientParser.SessionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#singleExpression.
    def visitSingleExpression(self, ctx:ClientParser.SingleExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#expression.
    def visitExpression(self, ctx:ClientParser.ExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#start.
    def visitStart(self, ctx:ClientParser.StartContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#loadmap.
    def visitLoadmap(self, ctx:ClientParser.LoadmapContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#wheneverError.
    def visitWheneverError(self, ctx:ClientParser.WheneverErrorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#spool.
    def visitSpool(self, ctx:ClientParser.SpoolContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#echo.
    def visitEcho(self, ctx:ClientParser.EchoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#loadDriver.
    def visitLoadDriver(self, ctx:ClientParser.LoadDriverContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#internal.
    def visitInternal(self, ctx:ClientParser.InternalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#set.
    def visitSet(self, ctx:ClientParser.SetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#script.
    def visitScript(self, ctx:ClientParser.ScriptContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#http.
    def visitHttp(self, ctx:ClientParser.HttpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#httpMessage.
    def visitHttpMessage(self, ctx:ClientParser.HttpMessageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#httpRequestLine.
    def visitHttpRequestLine(self, ctx:ClientParser.HttpRequestLineContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#httpMethod.
    def visitHttpMethod(self, ctx:ClientParser.HttpMethodContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#httpRequestTarget.
    def visitHttpRequestTarget(self, ctx:ClientParser.HttpRequestTargetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#httpHeaderFields.
    def visitHttpHeaderFields(self, ctx:ClientParser.HttpHeaderFieldsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#httpHeaderField.
    def visitHttpHeaderField(self, ctx:ClientParser.HttpHeaderFieldContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#httpFieldName.
    def visitHttpFieldName(self, ctx:ClientParser.HttpFieldNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#httpFieldValue.
    def visitHttpFieldValue(self, ctx:ClientParser.HttpFieldValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#httpMessageBody.
    def visitHttpMessageBody(self, ctx:ClientParser.HttpMessageBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#httpMultipart.
    def visitHttpMultipart(self, ctx:ClientParser.HttpMultipartContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#httpMultipartBoundary.
    def visitHttpMultipartBoundary(self, ctx:ClientParser.HttpMultipartBoundaryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#httpBoundaryDelimiter.
    def visitHttpBoundaryDelimiter(self, ctx:ClientParser.HttpBoundaryDelimiterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#httpMessageBodyContent.
    def visitHttpMessageBodyContent(self, ctx:ClientParser.HttpMessageBodyContentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#httpMessageBodyOperate.
    def visitHttpMessageBodyOperate(self, ctx:ClientParser.HttpMessageBodyOperateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#httpMessageBodyOther.
    def visitHttpMessageBodyOther(self, ctx:ClientParser.HttpMessageBodyOtherContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#loopUntil.
    def visitLoopUntil(self, ctx:ClientParser.LoopUntilContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#loop.
    def visitLoop(self, ctx:ClientParser.LoopContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#loopPair.
    def visitLoopPair(self, ctx:ClientParser.LoopPairContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#assert.
    def visitAssert(self, ctx:ClientParser.AssertContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#sql.
    def visitSql(self, ctx:ClientParser.SqlContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#sqlCreate.
    def visitSqlCreate(self, ctx:ClientParser.SqlCreateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#sqlReplace.
    def visitSqlReplace(self, ctx:ClientParser.SqlReplaceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#sqlInsert.
    def visitSqlInsert(self, ctx:ClientParser.SqlInsertContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#sqlUpdate.
    def visitSqlUpdate(self, ctx:ClientParser.SqlUpdateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#sqlDelete.
    def visitSqlDelete(self, ctx:ClientParser.SqlDeleteContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#sqlSelect.
    def visitSqlSelect(self, ctx:ClientParser.SqlSelectContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#sqlDrop.
    def visitSqlDrop(self, ctx:ClientParser.SqlDropContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#sqlDeclare.
    def visitSqlDeclare(self, ctx:ClientParser.SqlDeclareContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ClientParser#sqlCreateProcedure.
    def visitSqlCreateProcedure(self, ctx:ClientParser.SqlCreateProcedureContext):
        return self.visitChildren(ctx)



del ClientParser