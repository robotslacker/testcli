connect /mem
> {%
dbConn = SessionContext["dbConn"]
stmt = dbConn.createStatement()
rs = stmt.executeQuery("select 1+2 from dual")
while rs.next():
    print("111=" + rs.getString(1))
%}
