-- [Hint] scenario:123:test1
_connect /mem
select 1+5 from dual;
_sleep 15
-- [Hint] scenario:end

-- [Hint] scenario:346:test2
_connect /mem
select 1+5 from dual;
_sleep 15
-- [Hint] scenario:end

-- [Hint] scenario:test3
_connect /mem
select 1+5 from dual;
_sleep 15
-- [Hint] scenario:end
