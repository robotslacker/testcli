parser grammar SQLParser;
import BaseParser;

options { 
    tokenVocab = SQLLexer;
    caseInsensitive = false;
}

prog: command EOF;


command:
      baseCommand
      | disconnect
      | session
      | connect
      | sql
      | EOF
      ;

// connect
connect
     : (connectjdbc | connectlocal) (CONNECT_SEMICOLON)?
     ;

connectlocal
     : CONNECT CONNECT_SLASH connectlocalService
     ;

connectjdbc
        : CONNECT (connectUserInfo (CONNECT_AT)?)?
          (connectDriver CONNECT_COLON connectDriverSchema CONNECT_COLON (connectDriverType CONNECT_COLON)? CONNECT_DASH
          (connectHost (CONNECT_COLON connectPort)?)? ((CONNECT_SLASH | CONNECT_COLON) (connectService)?)? )?
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
        (IPV4 | IPV6 | CONNECT_STRING)
        ;

connectUser
        : CONNECT_STRING
        ;

connectPassword
        : CONNECT_STRING
        ;

connectPort
        : CONNECT_STRING
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
        : SESSION
        (
               SESSION_SAVE|
               SESSION_RELEASE|
               SESSION_RESTORE|
               SESSION_SAVEURL|
               SESSION_SHOW
        ) SESSION_NAME? SESSION_END? CRLF?
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

sqlDeclare
        : (SQL_DECLARE | SQL_BEGIN)
          SQL_SLASH CRLF?
        ;

sqlCreateProcedure
        : SQL_CREATE_PROCEDURE 
          SQL_SLASH CRLF?
        ;
