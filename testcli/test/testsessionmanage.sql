_connect /mem
_session show;

create table aaa (id int);
insert into aaa values(10);
select * from aaa;

_session save session1;

_connect /mem
create table aaa (id int);
insert into aaa values(20);
select * from aaa;

_session save session2;

_session show;

_session restore session1;
select * from aaa;
_session restore session2;
select * from aaa;

_session release session1;
_session release session2;

_session show;
select * from aaa;


