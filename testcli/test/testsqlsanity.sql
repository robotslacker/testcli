connect /mem
create table aaa (id int);
insert into aaa values(10);
insert into aaa values(6);
-- [Hint] Order
select * from aaa;
drop table xxx;
delete from aaa where id =6;

select 1 from dual;


