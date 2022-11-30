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
      | use
      | exit
      | quit
      | sleep
      | spool
      | script
      | echo
      ;

// Exit
exit    : EXIT INT? SEMICOLON? CRLF?;

// quit
quit    : QUIT INT? SEMICOLON? CRLF?;

// use
use     : USE (USE_API|USE_SQL) (USE_SEMICOLON)? CRLF?;

// sleep
sleep   : SLEEP INT SEMICOLON? CRLF?;

start   : START START_EXPRESSION (START_COMMA START_EXPRESSION)* START_LOOP? START_INT? SEMICOLON? CRLF?;

// 加载数据库驱动，映射文件，插件等
load    : LOAD LOAD_OPTION (LOAD_EXPRESSION)+ SEMICOLON? CRLF?;

// ASSERT判断
assert  : ASSERT ASSERT_EXPRESSION (SEMICOLON)? CRLF?;

// 执行主机操作系统命令
host    : HOST HOST_BLOCK;

// 循环处理操作
loop    : LOOP
          (LOOP_BREAK | LOOP_END | LOOP_CONTINUE | LOOP_BEGIN LOOP_UNTIL LOOP_EXPRESSION) (LOOP_SEMICOLON)? CRLF?
        ;

// IF条件表达式
if      : IF IF_EXPRESSION SEMICOLON? CRLF?;
endif   : ENDIF SEMICOLON? CRLF?;

// 错误处理操作
whenever:   WHENEVER WHENEVER_ERROR (WHENEVER_CONTINUE|(WHENEVER_EXIT WHENEVER_EXITCODE)) WHENEVER_SEMICOLON? CRLF?;

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

