parser grammar TestParser;

options {
    tokenVocab = TextLexer;
    caseInsensitive = false;
}


prog: commands EOF;

commands: command+;

command:
      connect
      ;

// connect
connect
     : (connectjdbc | connectlocal)
     ;

connectlocal
     : CONNECT connectService
     ;

connectjdbc
        : CONNECT (connectUserInfo (CONNECT_AT)?)
          (connectDriver CONNECT_COLON connectDriverSchema CONNECT_COLON (connectDriverType CONNECT_COLON)? CONNECT_DASH
          connectHost (CONNECT_COLON connectPort)? (CONNECT_SLASH | CONNECT_COLON) connectService)?
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
        : CONNECT_STRING
        ;

connectService
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
