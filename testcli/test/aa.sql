connect /mem
create table aaa (id int);
insert into aaa values(10);
> {% i=0 %}
_loop Begin UNTIL {% i==3 %}
> {% i=i+1 %}
update aaa set id = id + 1;
sleep 1
_loop end;

select * from aaa;

