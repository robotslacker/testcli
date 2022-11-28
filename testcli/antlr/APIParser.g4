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
      | http
      | EOF
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
        : (singleExpression )+
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
