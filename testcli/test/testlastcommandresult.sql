_use sql
_connect /mem
create table aaa (id int);
insert into aaa values(10);
select * from aaa;

> {%  x = lastCommandResult %}
_assert {%  x["errorCode"] == 0 %}
_assert {%  lastCommandResult["rows"][0][0] == 10 %}

_use api

> {% host="127.0.0.1" %}
> {% port=8000 %}
// [Hint] aa
### aaa
// @no-redirect
GET http://{{host}}:{{port}}/health
    ?requestId=1 HTTP/1.1
Accept: application/json
X-Language: zh_CN
Content-Type: application/json

###

_assert {%  lastCommandResult["status"] == 200 %}
_assert {%  str(lastCommandResult["data"]) == "{\'status\': \'OK\'}" %}
