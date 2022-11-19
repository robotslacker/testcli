lexer grammar SQLLexer;

options { 
    caseInsensitive = true;
}

channels { HINT_CHANNEL, COMMENT_CHANNEL, SQLSTATEMENT_CHANNEL }

// 分割符号
CRLF              : '\n';
COMMA             : ',';
SEMICOLON         : ';';
COLON             : ':';
AT                : '@';
DOT               : '.';
SLASH             : '/';
BRACKET_OPEN      : '(';
BRACKET_CLOSE     : ')';
SQUARE_OPEN       : '[';
SQUARE_CLOSE      : ']';
DOUBLE_QUOTE      : '"';
SINGLE_QUOTE      : '\'';
ESCAPE            : '\\';
SPACE             : [ \t]+ ->channel(HIDDEN);

// 关键字
EXIT: 'EXIT';
QUIT: 'QUIT';
USE: 'USE';
API: 'API';
SQL: 'SQL';
CONNECT: 'CONNECT' -> pushMode(ConnectMode);
DISCONNECT: 'DISCONNECT';
SESSION: 'SESSION';
SAVE: 'SAVE';
RELEASE: 'RELEASE';
RESTORE: 'RESTORE';
SAVECONFIG: 'SAVECONFIG';
SHOW: 'SHOW';
START: 'START';
LOADMAP: 'LOADMAP';
WHENEVER_ERROR: 'WHENEVER_ERROR';
CONTINUE: 'CONTINUE';
SPOOL: 'SPOOL';
BEGIN: 'BEGIN';
END: 'END';
INTERNAL: '__INTERNAL__';
SET: 'SET';
LOOP: 'LOOP';
UNTIL: 'UNTIL';
INTERVAL: 'INTERVAL';
ASSERT: 'ASSERT';
SLEEP: 'SLEEP';
LOADDRIVER: 'LOADDRIVER';

// 回显示模式
ECHO_OPEN   : 'ECHO' .*? (CRLF | EOF) ->pushMode(EchoMode);

// 脚本模式
SCRIPT_OPEN : '> {%' ->pushMode(ScriptMode);

// 注释模式
COMMENT_OPEN: '//' .*? CRLF ->channel(HIDDEN);

// --提示
MINUS_MINUS_HINT   : '--' ' '* '[Hint]' .*? CRLF ->channel(HINT_CHANNEL);

// --SQL注释
MINUS_MINUS_COMMENT   : '--' .*? (CRLF | EOF) ->channel(COMMENT_CHANNEL);
HASH_COMMENT      : '#' ~'#' .*? CRLF ->channel(COMMENT_CHANNEL);

// SQL创建语句
SQL_CREATE: 'CREATE' -> mode(SQLStatementMode) ;
SQL_INSERT: 'INSERT' -> mode(SQLStatementMode) ;
SQL_UPDATE: 'UPDATE' -> mode(SQLStatementMode) ;
SQL_SELECT: 'SELECT' -> mode(SQLStatementMode) ;
SQL_DELETE: 'DELETE'  -> mode(SQLStatementMode) ;
SQL_REPLACE: 'REPLACE' -> mode(SQLStatementMode);
SQL_DECLARE: 'DECLARE' -> mode(SQLProcedureMode) ;
SQL_DROP:   'DROP' -> mode(SQLStatementMode) ;
SQL_CREATE_PROCEDURE: ('CREATE' | 'REPLACE' | ' '+ | 'OR')+ ('PROCEDURE'|'FUNCTION') ->mode(SQLProcedureMode);

INT : DIGIT+ ;
DECIMAL: DIGIT+ '.' DIGIT+ ;

// Fragments
fragment DIGIT: [0-9];
fragment ALPHA: [A-Z];
fragment HEX: [0-9A-F];

// 双引号字符串
fragment DoubleQuoteString: '"' (~'"' | '\\' ('\n' | .))* '"';
// 单引号字符串
fragment SingleQuoteString: '\'' (~'\'' | '\\' ('\r'? '\n' | .))* '\'';

// 通用字符串
String      
            : (OBS_TEXT | UNRESERVED | SUBDELIMS | PCTENCODED | DoubleQuoteString | SingleQuoteString)+
            ;

fragment OBS_TEXT: '\u00ff' ..'\uffff';

fragment UNRESERVED
            : ALPHA | DIGIT | '-' | '.' | '_' | '~'
            ;

fragment SUBDELIMS   
            : '!' | '$' | '&' | '(' | ')' | '*' | '+' | '='
            ;

fragment PCTENCODED
            : '%' HEX HEX
            ;

/**
 * 链接模式
 */
mode ConnectMode;

CONNECT_SPACE
            : [ \t]+ -> channel (HIDDEN) 
            ;

CONNECT_CRLF
            : '\n' ->type(CRLF), popMode
            ;

CONNECT_AT  
            : '@'
            ;

CONNECT_SLASH
            : '/'
            ;

CONNECT_COLON
            : ':'
            ;

CONNECT_QUESTION
            : '?'
            ;

CONNECT_POUND
            : '#'
            ;

CONNECT_OR
            : '|'
            ;

CONNECT_DASH
            : '//'
            ;

CONNECT_EQUAL
            : '='
            ;

CONNECT_PARA_AND
            : '&'
            ;

JDBC: 'JDBC';

IPV4
            : DIGIT+ '.' DIGIT+ '.' DIGIT+ '.' DIGIT+ 
            ;

CONNECT_PORT
            : CONNECT_COLON DIGIT+
            ;

fragment CONNECT_DOUBLEQUOTE
            : '"' (~'"' | '\\' ('\r'? '\n' | .))* '"'
            ;

fragment CONNECT_SINGLEQUOTE
            : '\'' (~'\'' | '\\' ('\r'? '\n' | .))* '\''
            ;

CONNECT_STRING
            : (OBS_TEXT | UNRESERVED | PCTENCODED | CONNECT_DOUBLEQUOTE | CONNECT_SINGLEQUOTE)+
            ;



/**
 * 脚本模式
 */   
mode ScriptMode;

ScriptBlock
      : .*? ('%}'| EOF) -> popMode
      ;

/** 
 * 回显模式
 */
mode EchoMode;

EchoBlock: 
      .*? 'ECHO' (' ' | '\t')+ 'OFF' -> popMode
      ;

/**
 * 注释模式
 */
mode CommentMode;

COMMENT_CRLF
      : '\n' ->type(CRLF), popMode
      ;

CommentString
      : ~('\n')+
      ;


/**
 * 提示模式
 */
mode HintMode;

HINT_SP
      : [ \t]+ -> channel (HIDDEN)
      ;

HINT
      : 'HINT'
      ;

HINT_SQUARE_OPEN
      : '[' ->type(SQUARE_OPEN)
      ;

HINT_SQUARE_CLOSE
      : ']' ->type(SQUARE_CLOSE)
      ;

HINT_CLOSE
      : '\n' -> popMode
      ;

HINT_STRING
      : String
      ;

HintMore
      : . -> type(HINT_STRING)
      ;

/**
 * SQL语句
 */
mode SQLStatementMode;

SQL_CRLF
            : '\n' -> channel(SQLSTATEMENT_CHANNEL)
            ;

SQL_SPACE
            : [ \t]+ -> channel(SQLSTATEMENT_CHANNEL)
            ;

SQL_SLASH_END
            : '\n' '/' ->type(SQL_END), mode(DEFAULT_MODE)
            ;

SQL_END
            : ';' ->mode(DEFAULT_MODE)
            ;

SQL_STRING
            : String ->channel(SQLSTATEMENT_CHANNEL)
            ;

SQL_SINGLE
            : SingleQuoteString ->channel(SQLSTATEMENT_CHANNEL)
            ;

SQL_OTHER
            : . -> channel(SQLSTATEMENT_CHANNEL)
            ;

mode SQLProcedureMode;

SQL_PROCEDURE_CRLF
            : '\n' ->channel(SQLSTATEMENT_CHANNEL)
            ;

SQL_SLASH
            : '\n' '/'->mode(DEFAULT_MODE)
            ;

SQL_PROCEDURE_SLASH
            : '/' ->channel(SQLSTATEMENT_CHANNEL)
            ;

SQLProcedureStatement
            : ~('\n'|'/')+ -> channel(SQLSTATEMENT_CHANNEL)
            ;