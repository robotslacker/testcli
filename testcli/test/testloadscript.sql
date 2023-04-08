_load script testloadscript.py;
_connect /mem
create table aaa (id int);
insert into aaa values(10);
select * from aaa;

> {%
import copy
x=copy.copy(lastCommandResult)
%}

_assert {% x["rows"][0][0]==10 %};

> {%
sessionContext["status"] = fun(x["rows"][0][0])
%}

> {%
xx = cc()
sessionContext["status"] = xx.welcome("Boy.")
%}

