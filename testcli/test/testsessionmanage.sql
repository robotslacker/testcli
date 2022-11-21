connect /mem
session show;

create table aaa (id int);
insert into aaa values(10);
select * from aaa;

session save session1;

connect /mem
create table aaa (id int);
insert into aaa values(20);
select * from aaa;

session save session2;

session show;

session restore session1;
select * from aaa;
session restore session2;
select * from aaa;

session release session1;
session release session2;

session show;
select * from aaa;


