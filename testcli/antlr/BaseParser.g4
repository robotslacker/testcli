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
      | ssh
      | job
      | compare
      | data
      | help
      ;

// Exit
exit    : EXIT INT? SEMICOLON? CRLF?;

// quit
quit    : QUIT INT? SEMICOLON? CRLF?;

// use
use     : USE (USE_API|USE_SQL) (USE_SEMICOLON)? CRLF?;

// sleep
sleep   : SLEEP INT SEMICOLON? CRLF?;

start   : START (START_EXPRESSION)+ SEMICOLON? CRLF?;

// 加载数据库驱动，映射文件，插件等
load    :
        LOAD
        (
          (LOAD_PLUGIN LOAD_EXPRESSION) |
          (LOAD_MAP LOAD_EXPRESSION) |
          (LOAD_JDBCDRIVER
            (
              (LOAD_JDBCCLASS LOAD_EQUAL LOAD_EXPRESSION) |
              (LOAD_JDBCFILE LOAD_EQUAL LOAD_EXPRESSION) |
              (LOAD_JDBCNAME LOAD_EQUAL LOAD_EXPRESSION) |
              (LOAD_JDBCPROP LOAD_EQUAL LOAD_EXPRESSION) |
              (LOAD_JDBCURL LOAD_EQUAL LOAD_EXPRESSION)
            )*
          )
        ) SEMICOLON? CRLF?;

// ASSERT判断
assert  : ASSERT ASSERT_EXPRESSION ((ASSERT_COMMA)? ASSERT_NAME)? (ASSERT_SEMICOLON)? CRLF?;

// 执行主机操作系统命令
host    : HOST HOST_EXPRESSION (SEMICOLON)? CRLF?;

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

// 回显指定的文件
echo
        :   ECHO_OPEN
            EchoBlock
            (CRLF | EOF)?
        ;

// 内嵌脚本
script
        :   SCRIPT_OPEN
            ScriptBlock
            CRLF?
        ;

// SET 语句
set     : SET (SET_EXPRESSION)* (SET_SEMICOLON)? CRLF?;

// SSH 远程连接
ssh     :
           SSH
           (
            (SSH_CONNECT SSH_EXPRESSION SSH_WITH SSH_USER SSH_EXPRESSION SSH_KEYFILE SSH_EXPRESSION) |
            (SSH_CONNECT SSH_EXPRESSION SSH_WITH SSH_USER SSH_EXPRESSION (SSH_PASSWORD SSH_EXPRESSION)?) |
            (SSH_EXECUTE (SSH_EXPRESSION)+) |
            (SSH_DISCONNECT) |
            (SSH_SAVE SSH_EXPRESSION) |
            (SSH_RESTORE SSH_EXPRESSION) |
              (
              SFTP (
                     (SFTP_CHMOD SSH_EXPRESSION SSH_INT) |
                     (SFTP_GETCWD) |
                     (SFTP_CHDIR SSH_EXPRESSION) |
                     (SFTP_CHOWN SSH_EXPRESSION SSH_INT SSH_INT) |
                     (SFTP_MKDIR SSH_EXPRESSION SSH_INT) |
                     (SFTP_GET SSH_EXPRESSION SSH_EXPRESSION) |
                     (SFTP_PUT SSH_EXPRESSION SSH_EXPRESSION) |
                     (SFTP_REMOVE SSH_EXPRESSION) |
                     (SFTP_RENAME SSH_EXPRESSION SSH_EXPRESSION) |
                     (SFTP_LISTDIR SSH_EXPRESSION) |
                     (SFTP_TRUNCATE SSH_EXPRESSION SSH_INT)
                   )
              )
           )
           (SSH_SEMICOLON)? CRLF?;

// JOB 并发作业控制
job      :
           JOB
           (
             (JOB_MANGER (JOB_ON | JOB_OFF)) |
             (JOB_WAIT JOB_EXPRESSION) |
             (JOB_SHOW JOB_EXPRESSION) |
             (JOB_ABORT JOB_EXPRESSION) |
             (JOB_SHUTDOWN JOB_EXPRESSION) |
             (JOB_TIMER JOB_EXPRESSION) |
             (JOB_START JOB_EXPRESSION) |
             (JOB_DEREGISTER JOB_WORKER) |
             (JOB_REGISTER JOB_WORKER JOB_TO JOB_EXPRESSION) |
             (JOB_SET JOB_EXPRESSION (JOB_EXPRESSION JOB_EQUAL JOB_EXPRESSION)+) |
             (JOB_CREATE JOB_EXPRESSION (JOB_EXPRESSION JOB_EQUAL JOB_EXPRESSION)*)
           )
           (JOB_SEMICOLON)? CRLF?;

// 文本比对
compare   :
           COMPARE
           (
              (COMPARE_EXPRESSION COMPARE_EXPRESSION
                (COMPARE_MASK|COMPARE_NOMASK|COMPARE_CASE|COMPARE_NOCASE|COMPARE_IGBLANK|COMPARE_NOIGBLANK|COMPARE_TRIM|COMPARE_NOTRIM)*)
              | ((COMPARE_SKIPLINE|COMPARE_NOSKIPLINE) COMPARE_EXPRESSION)
              | (COMPARE_MASKLINE COMPARE_EXPRESSION COMPARE_EQUAL COMPARE_EXPRESSION)
              | (COMPARE_NOMASKLINE COMPARE_EXPRESSION)
              | COMPARE_RESET
              | (COMPARE_SET (COMPARE_MASK|COMPARE_NOMASK|COMPARE_CASE|COMPARE_NOCASE|COMPARE_IGBLANK|COMPARE_NOIGBLANK|COMPARE_TRIM|COMPARE_NOTRIM)*
                )
              | (COMPARE_SET COMPARE_OUTPUT (COMPARE_CONSOLE | COMPARE_DIFFFILE)+)
              | (COMPARE_SET COMPARE_ALGORITHM (COMPARE_LCS | COMPARE_MYERS))
              | (COMPARE_SET (COMPARE_WORK|COMPARE_REFERENCE) COMPARE_ENCODING COMPARE_EXPRESSION)
           )
           (COMPARE_SEMICOLON)? CRLF?;

// 随机文件生成,用于fake测试数据
data      :
          DATA
          (
              (DATA_SET DATA_SEEDFILE DATA_DIR DATA_EXPRESSION) |
              (
                  DATA_CREATE DATA_FILETYPE DATA_FILE DATA_EXPRESSION
                  DATACOLUMN_OPEN (DATACOLUMN_CONTENT)?
                  (DATA_ROWS DATA_INT)?
              ) |
              (DATA_CONVERT DATA_FILETYPE DATA_FILE DATA_EXPRESSION DATA_FROM DATA_FILETYPE DATA_FILE DATA_EXPRESSION)
          )
          (DATA_SEMICOLON)? CRLF?;

// 帮助信息
help       :
           HELP (HELP_COMMAND)? (HELP_SEMICOLON)? CRLF?;
