_connect /mem

_job timer timer1;
insert into testtab values(20,'slave1');
commit;

