parser grammar SQLParser;

options { 
    tokenVocab = SQLLexer;
    caseInsensitive = false;
}

prog: command EOF;

command:
      exit
      | quit
      | use
      | sleep
      | connect
      | disconnect
      | session
      | start
      | loadmap
      | wheneverError
      | spool
      | loadDriver
      | set
      | internal
      | script
      | loop
      | echo
      | loopUntil
      | assert
      | sql
      | EOF
      ;

// Exit 
exit: 
    EXIT INT? CRLF?
    ;
    
// quit
quit: 
    QUIT INT? CRLF?
    ;

// use 
use:  
    USE (API|SQL) CRLF?
    ;

// sleep
sleep
        : SLEEP INT CRLF?
        ;

// connect 
connect
     : (connectjdbc | connectlocal)
     ;

connectlocal
     : CONNECT CONNECT_SLASH connectlocalService
     ;

connectjdbc
        : CONNECT (connectUserInfo (CONNECT_AT)?)
          (connectDriver CONNECT_COLON connectDriverSchema CONNECT_COLON (connectDriverType CONNECT_COLON)? CONNECT_DASH
          connectHost (connectPort)? (CONNECT_SLASH | CONNECT_COLON) connectService)?
          (CONNECT_QUESTION connectParameters)?
        ;

connectUserInfo
        :  connectUser (CONNECT_SLASH connectPassword)?
        ;

connectDriver
       :  JDBC
       ;

connectDriverSchema
       : CONNECT_STRING
       ;

connectDriverType
       : CONNECT_STRING
       ;

connectHost:
        (IPV4 | CONNECT_STRING)
        ;

connectUser
        : CONNECT_STRING
        ;

connectPassword
        : CONNECT_STRING
        ;

connectPort
        : CONNECT_PORT
        ;

connectService
        : CONNECT_STRING (CONNECT_COLON CONNECT_STRING)?
        ;

connectlocalService
        : CONNECT_STRING
        ;

connectParameterName
        : CONNECT_STRING
        ;

connectParameterValue
        : CONNECT_STRING
        ;

connectParameter
        : connectParameterName CONNECT_EQUAL connectParameterValue
        ;

connectParameters
        : connectParameter ((CONNECT_PARA_AND connectParameter)+)?
        ;
        
// disconnect
disconnect
        : DISCONNECT (expression|INT)* CRLF?
        ;

session
        : SESSION (SESSION_SAVE|SESSION_RELEASE|SESSION_RESTORE|SESSION_SAVEURL|SESSION_SHOW) SESSION_NAME SESSION_END?
        ;

singleExpression
        : (String 
        | DOT 
        | SLASH 
        | BRACKET_OPEN 
        | BRACKET_CLOSE
        | ESCAPE
        | SQUARE_OPEN 
        | SQUARE_CLOSE 
        | DOUBLE_QUOTE 
        | SINGLE_QUOTE )
        ;

expression
        : (String
        | DOT
        | COLON
        | SLASH
        | BRACKET_OPEN
        | BRACKET_CLOSE
        | ESCAPE
        | SQUARE_OPEN
        | SQUARE_CLOSE
        | DOUBLE_QUOTE
        | SINGLE_QUOTE )+
        ;

// 执行脚本， START script1,script2,script3 [LOOP <INT>]
start
        : START (expression | ',')+ LOOP? INT? CRLF?
        ;

// 
loadmap
        : LOADMAP (expression | ',')+  CRLF?
        ;
        
//
wheneverError
        :   WHENEVER_ERROR (CONTINUE|EXIT) CRLF?
        ;
//
spool
        : SPOOL String (SEMICOLON)? CRLF?
        ;

// 12: 回显指定的文件 
echo
        :   ECHO_OPEN
            EchoBlock
            (CRLF | EOF)?
        ;

// 13： 加载驱动程序
loadDriver
        : LOADDRIVER (expression | ',')*  CRLF?
        ;

// 14：执行SQL语句

// 15：执行内部语句
internal 
        : INTERNAL expression+ CRLF?
        ;

// 16：SET 语句
set 
        : SET ((AT)?singleExpression+)? (SEMICOLON)? CRLF?
        ;

// 17：内嵌脚本
script
        :   SCRIPT_OPEN
            ScriptBlock
            CRLF?
        ;


// 20：循环,条件判断
loopUntil
        : LOOP 'BEGIN' UNTIL expression INTERVAL INT CRLF?
          LOOP END CRLF?
        ;

loop    : LOOP 'BEGIN' loopPair (COMMA loopPair)* CRLF?
          LOOP END CRLF
        ;

loopPair
        : String COLON expression
        ;

// 21：ASSERT判断
assert
        : ASSERT ASSERT_EXPRESSION (SEMICOLON)? CRLF?
        ;

// 
sql 
        : sqlCreate
        | sqlReplace
        | sqlInsert
        | sqlUpdate
        | sqlDelete
        | sqlSelect
        | sqlDeclare
        | sqlDrop
        | sqlCommitRollback
        | sqlCreateProcedure
        | CRLF
        ;

sqlCreate
        : SQL_CREATE SQL_END CRLF?
        ;

sqlReplace
        : SQL_REPLACE SQL_END CRLF?
        ;

sqlInsert
        : SQL_INSERT SQL_END CRLF?
        ;

sqlUpdate
        : SQL_UPDATE SQL_END CRLF?
        ;

sqlDelete
        : SQL_DELETE SQL_END CRLF?
        ;

sqlSelect
        : SQL_SELECT SQL_END CRLF?
        ;

sqlDrop
        : SQL_DROP SQL_END CRLF?
        ;

sqlCommitRollback
        : (SQL_COMMIT | SQL_ROLLBACK) SQL_END? CRLF?
        ;

sqlDeclare
        : (SQL_DECLARE | SQL_BEGIN)
          SQL_SLASH CRLF?
        ;

sqlCreateProcedure
        : SQL_CREATE_PROCEDURE 
          SQL_SLASH CRLF?
        ;
