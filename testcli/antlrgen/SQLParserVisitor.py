# Generated from SQLParser.g4 by ANTLR 4.11.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .SQLParser import SQLParser
else:
    from SQLParser import SQLParser

# This class defines a complete generic visitor for a parse tree produced by SQLParser.

class SQLParserVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by SQLParser#prog.
    def visitProg(self, ctx:SQLParser.ProgContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#command.
    def visitCommand(self, ctx:SQLParser.CommandContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#connect.
    def visitConnect(self, ctx:SQLParser.ConnectContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#connectlocal.
    def visitConnectlocal(self, ctx:SQLParser.ConnectlocalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#connectjdbc.
    def visitConnectjdbc(self, ctx:SQLParser.ConnectjdbcContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#connectUserInfo.
    def visitConnectUserInfo(self, ctx:SQLParser.ConnectUserInfoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#connectDriver.
    def visitConnectDriver(self, ctx:SQLParser.ConnectDriverContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#connectDriverSchema.
    def visitConnectDriverSchema(self, ctx:SQLParser.ConnectDriverSchemaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#connectDriverType.
    def visitConnectDriverType(self, ctx:SQLParser.ConnectDriverTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#connectHost.
    def visitConnectHost(self, ctx:SQLParser.ConnectHostContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#connectUser.
    def visitConnectUser(self, ctx:SQLParser.ConnectUserContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#connectPassword.
    def visitConnectPassword(self, ctx:SQLParser.ConnectPasswordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#connectPort.
    def visitConnectPort(self, ctx:SQLParser.ConnectPortContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#connectService.
    def visitConnectService(self, ctx:SQLParser.ConnectServiceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#connectlocalService.
    def visitConnectlocalService(self, ctx:SQLParser.ConnectlocalServiceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#connectParameterName.
    def visitConnectParameterName(self, ctx:SQLParser.ConnectParameterNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#connectParameterValue.
    def visitConnectParameterValue(self, ctx:SQLParser.ConnectParameterValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#connectParameter.
    def visitConnectParameter(self, ctx:SQLParser.ConnectParameterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#connectParameters.
    def visitConnectParameters(self, ctx:SQLParser.ConnectParametersContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#disconnect.
    def visitDisconnect(self, ctx:SQLParser.DisconnectContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#session.
    def visitSession(self, ctx:SQLParser.SessionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#expression.
    def visitExpression(self, ctx:SQLParser.ExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#sql.
    def visitSql(self, ctx:SQLParser.SqlContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#sqlCreate.
    def visitSqlCreate(self, ctx:SQLParser.SqlCreateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#sqlReplace.
    def visitSqlReplace(self, ctx:SQLParser.SqlReplaceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#sqlInsert.
    def visitSqlInsert(self, ctx:SQLParser.SqlInsertContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#sqlUpdate.
    def visitSqlUpdate(self, ctx:SQLParser.SqlUpdateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#sqlDelete.
    def visitSqlDelete(self, ctx:SQLParser.SqlDeleteContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#sqlSelect.
    def visitSqlSelect(self, ctx:SQLParser.SqlSelectContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#sqlDrop.
    def visitSqlDrop(self, ctx:SQLParser.SqlDropContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#sqlDeclare.
    def visitSqlDeclare(self, ctx:SQLParser.SqlDeclareContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#sqlCreateProcedure.
    def visitSqlCreateProcedure(self, ctx:SQLParser.SqlCreateProcedureContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#baseCommand.
    def visitBaseCommand(self, ctx:SQLParser.BaseCommandContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#exit.
    def visitExit(self, ctx:SQLParser.ExitContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#quit.
    def visitQuit(self, ctx:SQLParser.QuitContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#use.
    def visitUse(self, ctx:SQLParser.UseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#sleep.
    def visitSleep(self, ctx:SQLParser.SleepContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#start.
    def visitStart(self, ctx:SQLParser.StartContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#load.
    def visitLoad(self, ctx:SQLParser.LoadContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#assert.
    def visitAssert(self, ctx:SQLParser.AssertContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#host.
    def visitHost(self, ctx:SQLParser.HostContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#loop.
    def visitLoop(self, ctx:SQLParser.LoopContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#if.
    def visitIf(self, ctx:SQLParser.IfContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#endif.
    def visitEndif(self, ctx:SQLParser.EndifContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#whenever.
    def visitWhenever(self, ctx:SQLParser.WheneverContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#spool.
    def visitSpool(self, ctx:SQLParser.SpoolContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#echo.
    def visitEcho(self, ctx:SQLParser.EchoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#script.
    def visitScript(self, ctx:SQLParser.ScriptContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#set.
    def visitSet(self, ctx:SQLParser.SetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#ssh.
    def visitSsh(self, ctx:SQLParser.SshContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#job.
    def visitJob(self, ctx:SQLParser.JobContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#compare.
    def visitCompare(self, ctx:SQLParser.CompareContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#data.
    def visitData(self, ctx:SQLParser.DataContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#help.
    def visitHelp(self, ctx:SQLParser.HelpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#monitor.
    def visitMonitor(self, ctx:SQLParser.MonitorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SQLParser#plugin.
    def visitPlugin(self, ctx:SQLParser.PluginContext):
        return self.visitChildren(ctx)



del SQLParser