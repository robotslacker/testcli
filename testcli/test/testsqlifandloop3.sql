_use sql;
_connect /MEM
create  table test_singleloop(num int);
insert into test_singleloop values(1);
insert into test_singleloop values(2);
_LOOP 2 UNTIL {% len(lastCommandResult["rows"]) == 3 %}  INTERVAL 3;
select * from test_singleloop order by 1;

_ASSERT {% 9> lastCommandResult["elapsed"] > 6 %}
