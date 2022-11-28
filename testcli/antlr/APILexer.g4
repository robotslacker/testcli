lexer grammar APILexer;
import BaseLexer;

options { 
    caseInsensitive = true;
}

channels { HINT_CHANNEL, COMMENT_CHANNEL }

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
    CRLF->type(CRLF),mode(HttpHeaderFieldMode);
HttpRequestTarget:
    .*? 'HTTP/' DIGIT+ '.' DIGIT+ '\n' ->mode(HttpHeaderFieldMode);
TEXT :
    . -> more;

mode HttpHeaderFieldMode;

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
      : '\n' ->skip, mode(HttpMessageBodyMode)  
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

// 进入 MultipartBoundary处理 FIXME 应该不
HttpMultipartBoundaryEnd
      : ('--' String '--' CRLF)
      ;

// 进入 MultipartBoundary处理
HttpMultipartBoundary
      : ('--' String CRLF) ->mode(HttpHeaderFieldMode)
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
