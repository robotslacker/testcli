_connect /mem
_if {% 3==2 %}
select 1+2 from dual;
_endif
select 1+2 from dual;
_if {% 4==4 %}
select 1+2 from dual;
_endif
select 3+4 from dual;

_connect /mem
create table aaa (id int);
insert into aaa values(10);
> {% i=0 %}
_loop Begin UNTIL {% i==3 %}
> {% i=i+1 %}
update aaa set id = id + 1;
_loop end;

select * from aaa;

