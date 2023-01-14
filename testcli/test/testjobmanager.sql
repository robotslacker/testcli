_job jobmanager on;

_connect /meta
create table testtab(id int, col1 char(10));
insert into testtab values(10, 'Master');

_job create myjob script=testjobmanagerslave1.sql tag=test1;
_job create myjob script=testjobmanagerslave2.sql tag=test1;

_job start all;
_job wait all;
select * from testtab order by id;
