_connect /mem
_load map testsqlmapping

-- 在sqlmapping的作用下，这里的TABA应该被替换成TAB1
create table {{TABA}} ( id  int);
create table {{TABB}} ( id  int);
create table {{M123}} ( id  int);

insert into {{TABA}} values(3);
insert into {{TABB}} values(4);
insert into {{M123}} values(5);

select * from {{TABA}};
select * from {{TABB}};
select * from {{M123}};

drop table {{TABA}} ;
drop table {{TABB}} ;
drop table {{M123}} ;

create table ${TABA} ( id  int);
create table ${TABB} ( id  int);
create table ${M123} ( id  int);

insert into ${TABA} values(3);
insert into ${TABB} values(4);
insert into ${M123} values(5);

select * from ${TABA};
select * from ${TABB};
select * from ${M123};

drop table ${TABA} ;
drop table ${TABB} ;
drop table ${M123} ;
