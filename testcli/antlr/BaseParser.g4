parser grammar BaseParser;

options {
    tokenVocab = BaseLexer;
    caseInsensitive = false;
}

prog: baseCommand EOF;

baseCommand:
      assert
      | load
      | host
      | start
      | loop
      | if
      | endif
      | whenever
      | set
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

start   : START START_EXPRESSION (START_COMMA START_EXPRESSION)* START_LOOP? START_INT? SEMICOLON? CRLF?;

// 加载数据库驱动，映射文件，插件等
load    : LOAD LOAD_OPTION (LOAD_EXPRESSION)+ SEMICOLON? CRLF?;

// ASSERT判断
assert  : ASSERT ASSERT_EXPRESSION (SEMICOLON)? CRLF?;

// 执行主机操作系统命令
host    : HOST HOST_BLOCK;

// 循环处理操作
loop    : LOOP
          (LOOP_BREAK | LOOP_END | LOOP_CONTINUE | LOOP_BEGIN LOOP_UNTIL LOOP_EXPRESSION)) (LOOP_SEMICOLON)? CRLF?
        ;

// IF条件表达式
if      : IF IF_EXPRESSION SEMICOLON? CRLF?;
endif   : ENDIF SEMICOLON? CRLF?;

// 错误处理操作
whenever:   WHENEVER WHENEVER_ERROR (WHENEVER_CONTINUE|WHENEVER_EXIT) WHENEVER_SEMICOLON? CRLF?;

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
set     : SET (SET_AT)?(SET_EXPRESSION)* (SET_SEMICOLON)? CRLF?;

