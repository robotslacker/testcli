# Generated from D:/Work/testcli/testcli/antlr\APIParser.g4 by ANTLR 4.10.1
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


    # Visit a parse tree produced by APIParser#connect.
    def visitConnect(self, ctx:APIParser.ConnectContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#connectlocal.
    def visitConnectlocal(self, ctx:APIParser.ConnectlocalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#connectjdbc.
    def visitConnectjdbc(self, ctx:APIParser.ConnectjdbcContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#connectUserInfo.
    def visitConnectUserInfo(self, ctx:APIParser.ConnectUserInfoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#connectDriver.
    def visitConnectDriver(self, ctx:APIParser.ConnectDriverContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#connectDriverSchema.
    def visitConnectDriverSchema(self, ctx:APIParser.ConnectDriverSchemaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#connectDriverType.
    def visitConnectDriverType(self, ctx:APIParser.ConnectDriverTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#connectHost.
    def visitConnectHost(self, ctx:APIParser.ConnectHostContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#connectUser.
    def visitConnectUser(self, ctx:APIParser.ConnectUserContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#connectPassword.
    def visitConnectPassword(self, ctx:APIParser.ConnectPasswordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#connectPort.
    def visitConnectPort(self, ctx:APIParser.ConnectPortContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#connectService.
    def visitConnectService(self, ctx:APIParser.ConnectServiceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#connectlocalService.
    def visitConnectlocalService(self, ctx:APIParser.ConnectlocalServiceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#connectParameterName.
    def visitConnectParameterName(self, ctx:APIParser.ConnectParameterNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#connectParameterValue.
    def visitConnectParameterValue(self, ctx:APIParser.ConnectParameterValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#connectParameter.
    def visitConnectParameter(self, ctx:APIParser.ConnectParameterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#connectParameters.
    def visitConnectParameters(self, ctx:APIParser.ConnectParametersContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#disconnect.
    def visitDisconnect(self, ctx:APIParser.DisconnectContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#session.
    def visitSession(self, ctx:APIParser.SessionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#singleExpression.
    def visitSingleExpression(self, ctx:APIParser.SingleExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#expression.
    def visitExpression(self, ctx:APIParser.ExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#start.
    def visitStart(self, ctx:APIParser.StartContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#loadmap.
    def visitLoadmap(self, ctx:APIParser.LoadmapContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#wheneverError.
    def visitWheneverError(self, ctx:APIParser.WheneverErrorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#spool.
    def visitSpool(self, ctx:APIParser.SpoolContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#echo.
    def visitEcho(self, ctx:APIParser.EchoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#loadDriver.
    def visitLoadDriver(self, ctx:APIParser.LoadDriverContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#internal.
    def visitInternal(self, ctx:APIParser.InternalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#set.
    def visitSet(self, ctx:APIParser.SetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#script.
    def visitScript(self, ctx:APIParser.ScriptContext):
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


    # Visit a parse tree produced by APIParser#httpFieldName.
    def visitHttpFieldName(self, ctx:APIParser.HttpFieldNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#httpFieldValue.
    def visitHttpFieldValue(self, ctx:APIParser.HttpFieldValueContext):
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


    # Visit a parse tree produced by APIParser#loopUntil.
    def visitLoopUntil(self, ctx:APIParser.LoopUntilContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#loop.
    def visitLoop(self, ctx:APIParser.LoopContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#loopPair.
    def visitLoopPair(self, ctx:APIParser.LoopPairContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#assert.
    def visitAssert(self, ctx:APIParser.AssertContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#sql.
    def visitSql(self, ctx:APIParser.SqlContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#sqlCreate.
    def visitSqlCreate(self, ctx:APIParser.SqlCreateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#sqlReplace.
    def visitSqlReplace(self, ctx:APIParser.SqlReplaceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#sqlInsert.
    def visitSqlInsert(self, ctx:APIParser.SqlInsertContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#sqlUpdate.
    def visitSqlUpdate(self, ctx:APIParser.SqlUpdateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#sqlDelete.
    def visitSqlDelete(self, ctx:APIParser.SqlDeleteContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#sqlSelect.
    def visitSqlSelect(self, ctx:APIParser.SqlSelectContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#sqlDrop.
    def visitSqlDrop(self, ctx:APIParser.SqlDropContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#sqlDeclare.
    def visitSqlDeclare(self, ctx:APIParser.SqlDeclareContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by APIParser#sqlCreateProcedure.
    def visitSqlCreateProcedure(self, ctx:APIParser.SqlCreateProcedureContext):
        return self.visitChildren(ctx)



del APIParser