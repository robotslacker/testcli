_use sql;
_connect /mem

create table aaa(name varchar(20), age int);
insert into aaa values('张三', 10);
insert into aaa values('李四', 20);
insert into aaa values('张飞', 30);

select * from aaa order by 1;

--[Hint] LogMask  张.*=>王五
select * from aaa order by 1,2;

--[Hint] LogFilter  .*张.*
select * from aaa order by 1,2;

