parser grammar APIParser;

options { 
    tokenVocab = APILexer;
    caseInsensitive = false;
}

prog: command EOF;

command:
      exit
      | quit
      | use
      | sleep
      | start
      | wheneverError
      | spool
      | set
      | internal
      | script
      | http
      | echo
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
        : SPOOL String CRLF?
        ;

// 12: 回显指定的文件 
echo
        :   ECHO_OPEN
            EchoBlock
            (CRLF | EOF)?
        ;

// 15：执行内部语句
internal 
        : INTERNAL expression+ CRLF?
        ;

// 16：SET 语句
set 
        : SET (singleExpression+)? (SEMICOLON)? CRLF?
        ;

// 17：内嵌脚本
script
        :   SCRIPT_OPEN
            ScriptBlock
            CRLF?
        ;


/**
 * 17: API语句
 * HTTP 请求
 * 
 * HTTP-message = start-line *( header-field CRLF ) CRLF [ message-body] 
 */
http
        : HTTP_OPEN
          httpMessage
          (HTTP_CLOSE | EOF)
        ;

httpMessage
        : httpRequestLine
          httpHeaderFields
          httpMessageBody?
          ;

/*
 * HTTP请求头 
 * httpRequestTarget 包含 HttpVersion 
 */
httpRequestLine
        : httpMethod httpRequestTarget CRLF
        ;

httpMethod
        : HttpMethod
        ;

httpRequestTarget
        : HttpRequestTarget
        ;

/**
 * HTTP请求域
 */ 
httpHeaderFields
        : httpHeaderField*
        ;

httpHeaderField
        : httpFieldName FIELD_COLON httpFieldValue 
        ;

httpFieldName
        : HttpFieldName
        ;

httpFieldValue
        : HttpFieldValue HttpFieldValueEnd 
        ;

/**
 * Http MessageBody
 * 内容或者Multipart boundary
 */
httpMessageBody
        : (httpMultipart | httpMessageBodyContent)+
        ;

httpMultipart
        : httpMultipartBoundary+ HttpMultipartBoundaryEnd
        ;

// multipart boundary 处理
httpMultipartBoundary
        : httpBoundaryDelimiter  
          httpHeaderFields
          httpMessageBodyContent
        ;

httpBoundaryDelimiter
        : HttpMultipartBoundary 
        ;

// 内容
httpMessageBodyContent
        : (httpMessageBodyOperate | httpMessageBodyOther)+
        ;

httpMessageBodyOperate
        : HttpMessageBodyOperate
        ;

httpMessageBodyOther
        : (String | CRLF)+
        ;
