parser grammar APIParser;
import BaseParser;

options { 
    tokenVocab = APILexer;
    caseInsensitive = false;
}

prog: command EOF;


// 以下命令中除http外都是公用命令，即非APIParser特色命令
command:
      baseCommand
      | apiset
      | session
      | http
      | EOF
      ;

apiset
       : APISET
         (
            (APISET_PROXY APISET_EXPRESSION) |
            (APISET_HTTPSVERIFY (APISET_ON | APISET_OFF)) |
         ) (APISET_SEMICOLON)?
       ;

session
        : SESSION
        (
            (SESSION_SAVE SESSION_NAME) |
            (SESSION_RELEASE) |
            (SESSION_RESTORE SESSION_NAME) |
            (SESSION_SHOW SESSION_NAME?)
        ) SESSION_SEMICOLON?
        ;

/**
 * 17: API语句
 * HTTP 请求
 * 
 * HTTP-message = start-line *( header-field CRLF ) CRLF [ message-body] 
 */
http
        : HTTP_OPEN
          (CRLF)*
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
        : httpMethod httpRequestTarget
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
        : httpHeaderFieldName FIELD_COLON httpHeaderFieldValue
        ;

httpHeaderFieldName
        : HttpHeaderFieldName
        ;

httpHeaderFieldValue
        : HttpHeaderFieldValue HttpHeaderFieldValueEnd
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
