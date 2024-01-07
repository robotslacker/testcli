_CONNECT /MEM
SELECT 1+2 FROM DUAL;SELECT 3+4 FROM DUAL;
> {%
selectstr="select 1+2 from dual;select 3+5 from dual;"
%}
{{selectstr}}
/

