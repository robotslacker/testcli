_load plugin testplugin.py;
_connect /mem
create table aaa (id int);
insert into aaa values(10);
select * from aaa;

> {% x=lastCommandResult %}

_assert {% x["rows"][0][0]==10 %};

> {%
sessionContext["status"] = fun(x["rows"][0][0])
%}

> {%
xx = cc()
sessionContext["status"] = xx.welcome("Boy.")
%}

