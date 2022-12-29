_connect /mem
_load map testsqlmapping

-- 在sqlmapping的作用下，这里的TABA应该被替换成TAB1
create table {{TABA}}
(
    id  int
);

insert into {{TABA}} values(3);
insert into {{TABA}} values(4);

-- [Order]
select * from {{TABA}};

