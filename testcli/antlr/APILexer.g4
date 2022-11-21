lexer grammar APILexer;

options { 
    caseInsensitive = true;
}

channels { HINT_CHANNEL, COMMENT_CHANNEL }

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
SHOW: 'SHOW';
START: 'START';
WHENEVER_ERROR: 'WHENEVER_ERROR';
CONTINUE: 'CONTINUE';
SPOOL: 'SPOOL';
BEGIN: 'BEGIN';
END: 'END';
INTERNAL: '__INTERNAL__';
SET: 'SET';
LOOP: 'LOOP';
ASSERT: 'ASSERT';
SLEEP: 'SLEEP';
LOADMAP: 'LOADMAP';

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
URI_CRLF:
    CRLF->type(CRLF),mode(HttpFieldMode);
HttpRequestTarget:
    'HTTP/' DIGIT+ '.' DIGIT+;
TEXT :
    . -> more;

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

