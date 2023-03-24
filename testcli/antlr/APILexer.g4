lexer grammar APILexer;
import BaseLexer;

options { 
    caseInsensitive = true;
}

channels { COMMENT_CHANNEL }

// HTTP 请求进入Http处理模式
HTTP_OPEN   : '###' .*? CRLF ->pushMode(HttpMode);

// 注释
COMMENT1     :  '//' .*? (CRLF | EOF) ->channel(HIDDEN);
COMMENT2     :  '--' .*? (CRLF | EOF) ->channel(HIDDEN);

// 设置系统参数
APISET       : 'SET' -> pushMode(APISetMode);

// HTTP会话管理
SESSION: '_SESSION' -> pushMode(SessionMode);

// Http请求模式
mode HttpMode;
HTTP_COMMENT: '//' .*? CRLF ->channel(COMMENT_CHANNEL);
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

/**
 * 分割URI
 */
mode HttpUriMode;
URI_SPACE:
    [ \t]+;
URI_CRLF:
    CRLF->type(CRLF),mode(HttpHeaderFieldMode);
HttpRequestTarget:
    .*? 'HTTP/' DIGIT+ '.' DIGIT+ URI_SPACE? '\n' ->mode(HttpHeaderFieldMode);
TEXT :
    . -> more;

mode HttpHeaderFieldMode;
HeaderField_SPACE:
    [ \t]+  ->channel(HIDDEN);

// 域名
HttpHeaderFieldName
     : (OBS_TEXT | UNRESERVED | SUBDELIMS | PCTENCODED | DoubleQuoteString | SingleQuoteString | '?')+
     ;

// 域分割，进入域值模式
FIELD_COLON
      : ':' -> mode(FieldValueMode)
      ;

// 空行, 进入内容模式
FIELD_CRLF
      : HeaderField_SPACE? '\n' ->skip, mode(HttpMessageBodyMode)
      ;

/** 
 * 域值模式
 *    处理域值
 */
mode FieldValueMode;

HttpHeaderFieldValue
      :  ~[\r\n]+
      ;

HttpHeaderFieldValueEnd
      : '\n' -> mode(HttpHeaderFieldMode)
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

// 进入 MultipartBoundary处理
HttpMultipartBoundaryEnd
      : ('--' String '--' CRLF)
      ;

// 进入 MultipartBoundary处理
HttpMultipartBoundary
      : ('--' String CRLF) ->mode(HttpHeaderFieldMode)
      ;

// 注释
HttpMessageBodyComment
      : ('//' .*? CRLF) ->channel(HIDDEN)
      ;

// 处理操作
HttpMessageBodyOperate
      : ('>>'|'>'|'<') .*? CRLF
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

mode APISetMode;
APISET_SPACE           : [ \t]+ -> channel (HIDDEN);
APISET_PROXY           : 'PROXY';
APISET_HTTPSVERIFY     : 'HTTPS_VERIFY';
APISET_ON              : 'ON';
APISET_OFF             : 'OFF';
APISET_EXPRESSION      : (OBS_TEXT | UNRESERVED | SUBDELIMS | PCTENCODED | DoubleQuoteString | SingleQuoteString | ':' | '/' | '\\' | '@' | '{' | '}' | '%')+;
APISET_SEMICOLON       : ';';
APISET_CRLF            : CRLF -> popMode;

mode SessionMode;
SESSION_SPACE          : [ \t]+ -> channel(HIDDEN);
SESSION_SAVE           : 'SAVE';
SESSION_RELEASE        : 'RELEASE';
SESSION_RESTORE        : 'RESTORE';
SESSION_SHOW           : 'SHOW';
SESSION_NAME           : (OBS_TEXT | UNRESERVED | SUBDELIMS | PCTENCODED | DoubleQuoteString | SingleQuoteString | ':' | '/' | '\\' | '@' | '{' | '}' | '%')+;
SESSION_SEMICOLON      : ';';
SESSION_CRLF           : CRLF -> popMode;
