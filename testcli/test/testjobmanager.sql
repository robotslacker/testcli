_connect /mem
create table testtab(id int, col1 char(10));
insert into testtab values(10, 'Master');

_job jobmanager on;
_job create myjob script testjobmanagerslave1.sql tag test1;
_job create myjob script testjobmanagerslave2.sql tag test1;

_job show all;
_job start all;
_job wait all;
select * from testtab order by id;
