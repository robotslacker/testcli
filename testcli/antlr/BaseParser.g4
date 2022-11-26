parser grammar BaseParser;

options {
    tokenVocab = BaseLexer;
    caseInsensitive = false;
}

prog: baseCommand EOF;

baseCommand:
      assert
      | load
      ;

//baseCommand:
//      exit
//      | quit
//      | use
//      | sleep
//      | start
//      | wheneverError
//      | spool
//      | set
//      | script
//      | echo
//      | assert
//      | EOF
//      ;

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

// Exit
exit    : EXIT INT? CRLF? ;

// quit
quit    : QUIT INT? CRLF?;

// use
use     : USE (API|SQL) CRLF?;

// sleep
sleep   : SLEEP INT CRLF?;

start
        : START (expression | ',')+ LOOP? INT? CRLF?
        ;

load    : LOAD LOAD_OPTION (LOAD_EXPRESSION)+ (SEMICOLON)? CRLF?;

//
wheneverError
        :   WHENEVER_ERROR (CONTINUE|EXIT) CRLF?
        ;
//
spool   : SPOOL String (SEMICOLON)? CRLF?;

// 12: 回显指定的文件
echo
        :   ECHO_OPEN
            EchoBlock
            (CRLF | EOF)?
        ;

// 17：内嵌脚本
script
        :   SCRIPT_OPEN
            ScriptBlock
            CRLF?
        ;

// 16：SET 语句
set
        : SET ((AT)?singleExpression+)? (SEMICOLON)? CRLF?
        ;

// 21：ASSERT判断
assert  : ASSERT ASSERT_EXPRESSION (SEMICOLON)? CRLF?;
