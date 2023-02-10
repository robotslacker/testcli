_connect /mem
create table aaa (id int);
insert into aaa values(10);
select * from aaa;
rollback;
select * from aaa;
_set autocommit true;
delete from aaa;
insert into aaa values(20);
select * from aaa;
rollback;
select * from aaa;
_set autocommit false;
delete from aaa;
insert into aaa values(30);
select * from aaa;
rollback;
select * from aaa;
