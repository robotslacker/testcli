_connect /mem
create table aaa (id int);

> {% i=1 %}
_loop Begin UNTIL {% i>=10 %}
insert into aaa values(10);
select * from aaa;
_IF {% len(lastCommandResult["rows"]) == 3 %}
    _LOOP BREAK
_ENDIF
> {% i=i+1 %}
_loop end;
select * from aaa order by 1;