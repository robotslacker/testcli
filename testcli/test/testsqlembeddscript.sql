connect /mem
create table aaa (id int);
insert into aaa values(10);
> {%
x=1
dbConn = SessionContext["dbConn"]
stmt = dbConn.createStatement()
rs = stmt.executeQuery("select id from aaa")
while rs.next():
    print("id=" + rs.getString(1))
SessionContext["status"] = "x=" + str(x)
%}
update aaa set id = 20;
select * from aaa;
> {%
x=x+3
dbConn = SessionContext["dbConn"]
stmt = dbConn.createStatement()
stmt.execute("update aaa set id=30")
print("x="+str(x))
SessionContext["status"] = "x=" + str(x)
%}
select * from aaa;

