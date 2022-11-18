lexer grammar ClientLexer;

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

// HTTP 请求进入Http处理模式
HTTP_OPEN   : '###' .*? CRLF ->pushMode(HttpMode);

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
 * Http请求模式
 */
mode HttpMode;

HTTP_CRLF: CRLF->type(CRLF);
DIVIDE: '/';
SP: [ \t]+ -> channel (HIDDEN);

// 请求行 
HttpMethod
      : ('POST' 
      | 'GET' 
      | 'PUT' 
      | 'HEAD' 
      | 'DELETE' 
      | 'OPTIONS' 
      | 'TRACE')

      ->mode(HttpUriMode);

// HTTP 请求结束符号
HTTP_CLOSE
      : '###' ->popMode;

// 提示信息
HttpHint
      : ('//' ' '? '[Hint]'  .*? CRLF) ->channel(HINT_CHANNEL)
      ;

// 注释
HttpComment
      : ('//' .*? CRLF) ->channel(COMMENT_CHANNEL)
      ;

/**
 * 分割URI
 */
mode HttpUriMode;

   // URI_SP: [ \t]+ -> channel (HIDDEN);
   URI_CRLF: CRLF->type(CRLF),mode(HttpFieldMode);
   HttpRequestTarget:  'HTTP/' DIGIT+ '.' DIGIT+;
   TEXT : . -> more;

mode HttpFieldMode;
// 域名
HttpFieldName
      : String
      ;

// 域分割，进入域值模式
FIELD_COLON
      : ':' -> mode(FieldValueMode)
      ;

// 空行, 进入内容模式
FIELD_CRLF
      : '\n' ->skip, mode(HttpMessageBodyMode)  
      ;

/** 
 * 域值模式
 *    处理域值
 */
mode FieldValueMode;

HttpFieldValue
      :  ~[\r\n]+
      ;

HttpFieldValueEnd
      : '\n' -> mode(HttpFieldMode)
      ;

/** 
 * Http消息模式
 *   -- multipart boundary
 *   // 注释
 *   
 *   内容
 */
mode HttpMessageBodyMode;

BODY_SPACE
      : [ \t]+ -> type(String)
      ;

BODY_CRLF
      : '\n' ->type(CRLF)
      ;

// 进入 MultipartBoundary处理 FIXME 应该不
HttpMultipartBoundaryEnd
      : ('--' String '--' CRLF)
      ;

// 进入 MultipartBoundary处理
HttpMultipartBoundary
      : ('--' String CRLF) ->mode(HttpFieldMode)
      ;

// 提示信息
HttpMessageBodyHint
      : ('//' ' '? '[Hint]'  .*? CRLF) ->channel(HINT_CHANNEL)
      ;

// 注释
HttpMessageBodyComment
      : ('//' .*? CRLF) ->channel(COMMENT_CHANNEL)
      ;

// 处理操作
HttpMessageBodyOperate
      : ('>>'|'>!'|'>>!'|'>'|'<') .*? CRLF
      ;

// HTTP 请求结束符号
HttpMessageBodyEnd
      : '###' ->type(HTTP_CLOSE), mode(DEFAULT_MODE)
      ;

BODY_STRING
      : String->type(String)
      ;

// 其他视为内容字符
HttpMessageBodyChar
      : .->type(String)
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
