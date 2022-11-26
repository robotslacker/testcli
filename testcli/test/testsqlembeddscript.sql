connect /mem
create table aaa (id int);
insert into aaa values(10);
> {%
x=1
dbConn = sessionContext["dbConn"]
stmt = dbConn.createStatement()
rs = stmt.executeQuery("select id from aaa")
while rs.next():
    print("id=" + rs.getString(1))
sessionContext["status"] = "x=" + str(x)
%}
update aaa set id = 20;
select * from aaa;
> {%
x=x+3
dbConn = sessionContext["dbConn"]
stmt = dbConn.createStatement()
stmt.execute("update aaa set id=30")
print("x="+str(x))
sessionContext["status"] = "x=" + str(x)
%}
select * from aaa;

