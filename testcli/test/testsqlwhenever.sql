_connect /mem;
_whenever error continue;
select 1+2 from dual;
select a from aaa;
select 3+4 from dual;

_whenever error exit 3;
select 1+2 from dual;
select a from aaa;
-- 如下的语句不应该被执行，应该会直接退出，退出码为3
select 1+2 from dual;