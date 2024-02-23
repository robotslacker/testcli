// 基础词法
lexer grammar BaseLexer;

options {
    caseInsensitive = true;
}

// 分割符号
CRLF                : '\n';
COMMA               : ',';
SEMICOLON           : ';';
COLON               : ':';
AT                  : '@';
DOT                 : '.';
SLASH               : '/';
BRACKET_OPEN        : '(';
BRACKET_CLOSE       : ')';
SQUARE_OPEN         : '[';
SQUARE_CLOSE        : ']';
DOUBLE_QUOTE        : '"';
SINGLE_QUOTE        : '\'';
ESCAPE              : '\\';
SPACE               : [ \t]+ ->channel(HIDDEN);

EXIT                : '_EXIT';
QUIT                : '_QUIT';
SLEEP               : '_SLEEP' -> pushMode(SleepMode);

// 切换应用模式
USE                 : '_USE' -> pushMode(UseMode);

// 回显随后的脚本
ECHO                : '_ECHO' .*? (CRLF | EOF) ->pushMode(EchoMode);

// 执行内置的Python脚本
SCRIPT              : '> {%' ->pushMode(ScriptMode);

// 表达式判断，用来验证执行结果
ASSERT              :  '_ASSERT' -> pushMode(AssertMode);

// 执行脚本
START               : '_START' -> pushMode(StartMode);

// 加载驱动或者映射关系
LOAD                : '_LOAD' -> pushMode(LoadMode);

// 执行主机操作系统命令
HOST                : '_HOST' -> pushMode(HostMode);

// 指定帮助命令
HELP                : '_HELP' -> pushMode(HelpMode);

// 条件表达式判断
IF                  : '_IF' -> pushMode(IfMode);
ENDIF               : '_ENDIF';

// 设置系统参数
SET                 : '_SET' -> pushMode(SetMode);

// 输出到指定文件
SPOOL               : '_SPOOL' -> pushMode(SpoolMode);

// 循环执行
LOOP                : '_LOOP' -> pushMode(LoopMode);

// 一旦错误，将会执行的操作
WHENEVER            : '_WHENEVER' -> pushMode(WheneverMode);

// 执行远程操作系统命令
SSH                 : '_SSH' ->pushMode(SshMode);

// 执行并行任务的控制
JOB                 : '_JOB' ->pushMode(JobMode);

// 比对文件的一致性
COMPARE             : '_COMPARE' ->pushMode(CompareMode);

// 执行随机文件生成
DATA                : '_DATA' ->pushMode(DataMode);

// 执行主机监控任务
MONITOR             : '_MONITOR'  ->pushMode(MonitorMode);

// PLUGIN命令
// 这个命令必须放在解析文件所有内置命令的最后，以保证不会对其他内置命令带来冲突
PLUGIN              : '_'[A-Z]+ -> pushMode(PluginMode);

INT                 : DIGIT+ ;
DECIMAL             : DIGIT+ '.' DIGIT+ ;
String              : (OBS_TEXT | UNRESERVED | SUBDELIMS | PCTENCODED | DoubleQuoteString | SingleQuoteString)+;
fragment UNRESERVED : ALPHA | DIGIT | '-' | '.' | '_' | '~';
fragment SUBDELIMS  : '!' | '$' | '&' | '(' | ')' | '*' | '+' | '=';
fragment PCTENCODED : '%' HEX HEX;
fragment DIGIT      : [0-9];
fragment ALPHA      : [A-Z];
fragment HEX        : [0-9A-F];
fragment OBS_TEXT   : '\u00ff' ..'\uffff';
fragment DoubleQuoteString
                    : '"' (~'"' | '\\' ('\n' | .))* '"';
fragment SingleQuoteString
                    : '\'' (~'\'' | '\\' ('\r'? '\n' | .))* '\'';

/**
 * 脚本模式
 */
mode ScriptMode;
ScriptBlock         : .*? ('\n%}'| EOF) -> popMode;

/**
 * 回显模式
 */
mode EchoMode;
EchoBlock           :.*? 'ECHO' (' ' | '\t')+ 'OFF' -> popMode;

mode AssertMode;
ASSERT_SPACE        : [ \t]+ -> channel (HIDDEN);
ASSERT_OPEN         : '{%';
ASSERT_CLOSE        : '%}';
ASSERT_CRLF         : CRLF -> popMode;
ASSERT_EXPRESSION   : ASSERT_OPEN .*? ASSERT_CLOSE;
ASSERT_NAME         : (OBS_TEXT | UNRESERVED | PCTENCODED | DoubleQuoteString | SingleQuoteString | ':' | '/' | '\\' )+;
ASSERT_COMMA        : ',';
ASSERT_SEMICOLON    : ';';

mode LoadMode;
LOAD_SPACE          : [ \t]+ -> channel (HIDDEN);
LOAD_EQUAL          : '=';
LOAD_PLUGIN         : 'PLUGIN';
LOAD_SCRIPT         : 'SCRIPT';
LOAD_MAP            : 'MAP';
LOAD_JDBCDRIVER     : 'JDBCDRIVER';
LOAD_JDBCFILE       : 'FILE';
LOAD_JDBCCLASS      : 'CLASS';
LOAD_JDBCNAME       : 'NAME';
LOAD_JDBCPROP       : 'PROPS';
LOAD_JDBCURL        : 'URL';
LOAD_EXPRESSION     :
    (OBS_TEXT | UNRESERVED | PCTENCODED | DoubleQuoteString | SingleQuoteString | ':' | '/' | '\\' )+;
LOAD_SEMICOLON       : ';';
LOAD_CRLF           : CRLF -> popMode;

mode StartMode;
START_SPACE        : [ \t]+ -> channel (HIDDEN);
START_EXPRESSION   :
    (OBS_TEXT | UNRESERVED | SUBDELIMS | PCTENCODED | DoubleQuoteString | SingleQuoteString | ':' | '/' | '\\' )+;
START_CRLF         : CRLF -> popMode;

mode HostMode;
HOST_SPACE         : [ \t]+ -> channel (HIDDEN);
HOST_EXPRESSION    :
    (OBS_TEXT | UNRESERVED | SUBDELIMS | PCTENCODED | DoubleQuoteString | SingleQuoteString | ':' | '/' | '\\' |' ')+;
HOST_CRLF          : CRLF -> popMode;

mode IfMode;
IF_SPACE        : [ \t]+ -> channel (HIDDEN);
IF_OPEN         : '{%';
IF_CLOSE        : '%}';
IF_EXPRESSION   : IF_OPEN .*? IF_CLOSE -> popMode;

mode LoopMode;
LOOP_SEMICOLON  : ';';
LOOP_SPACE      : [ \t]+ -> channel (HIDDEN);
LOOP_BEGIN      : 'BEGIN';
LOOP_UNTIL      : 'UNTIL';
LOOP_INTERVAL   : 'INTERVAL';
LOOP_INT        : INT;
LOOP_OPEN       : '{%';
LOOP_CLOSE      : '%}';
LOOP_BREAK      : 'BREAK';
LOOP_END        : 'END';
LOOP_CONTINUE   : 'CONTINUE';
LOOP_EXPRESSION : LOOP_OPEN .*? LOOP_CLOSE;
LOOP_CRLF       : CRLF -> popMode;

mode WheneverMode;
WHENEVER_SPACE      : [ \t]+ -> channel (HIDDEN);
WHENEVER_EXITCODE   : INT;
WHENEVER_ERROR      : 'ERROR';
WHENEVER_SEMICOLON  : ';';
WHENEVER_CONTINUE   : 'CONTINUE';
WHENEVER_EXIT       : 'EXIT';
WHENEVER_CRLF       : CRLF -> popMode;

mode SpoolMode;
SPOOL_SPACE           : [ \t]+ -> channel (HIDDEN);
SPOOL_EXPRESSION      : (OBS_TEXT | UNRESERVED | SUBDELIMS | PCTENCODED | DoubleQuoteString | SingleQuoteString | ':' | '/' | '\\' | '@' | '{' | '}' | '%')+;
SPOOL_SEMICOLON       : ';';
SPOOL_OFF             : 'OFF';
SPOOL_CRLF            : CRLF -> popMode;

mode SetMode;
SET_SPACE           : [ \t]+ -> channel (HIDDEN);
SET_EXPRESSION      : (OBS_TEXT | UNRESERVED | SUBDELIMS | PCTENCODED | DoubleQuoteString | SingleQuoteString | ':' | '/' | '\\' | '@' | '{' | '}' | '%')+;
SET_SEMICOLON       : ';';
SET_CRLF            : CRLF -> popMode;

mode UseMode;
USE_API             : 'API';
USE_SQL             : 'SQL';
USE_SPACE           : [ \t]+ -> channel (HIDDEN);
USE_SEMICOLON       : ';';
USE_CRLF            : CRLF -> popMode;

mode SshMode;
SSH_CONNECT         : 'CONNECT';
SSH_WITH            : 'WITH';
SSH_USER            : 'USER';
SSH_SET             : 'SET';
SSH_KEYFILE         : 'KEYFILE';
SSH_PASSWORD        : 'PASSWORD';
SSH_EXECUTE         : 'EXECUTE';
SSH_DISCONNECT      : 'DISCONNECT';
SSH_SAVE            : 'SAVE';
SSH_RESTORE         : 'RESTORE';
SFTP                : 'SFTP';
SFTP_CHMOD          : 'CHMOD';
SFTP_GETCWD         : 'GETCWD';
SFTP_CHDIR          : 'CHDIR';
SFTP_CHOWN          : 'CHOWN';
SFTP_MKDIR          : 'MKDIR';
SFTP_GET            : 'GET';
SFTP_PUT            : 'PUT';
SFTP_REMOVE         : 'REMOVE';
SFTP_RENAME         : 'RENAME';
SFTP_LISTDIR        : 'LISTDIR';
SFTP_TRUNCATE       : 'TRUNCATE';
SSH_EQUAL           : '=';
SSH_SPACE           : [ \t]+ -> channel (HIDDEN);
SSH_SEMICOLON       : ';';
SSH_CRLF            : CRLF -> popMode;
SSH_EXPRESSION      :
    (OBS_TEXT | UNRESERVED | SUBDELIMS | PCTENCODED | DoubleQuoteString | SingleQuoteString | ':' | '/' | '\\' | '@' | '{' | '}' | '|'| ',')+;

mode JobMode;
JOB_SPACE           : [ \t]+ -> channel (HIDDEN);
JOB_SEMICOLON       : ';';
JOB_EQUAL           : '=';
JOB_CRLF            : CRLF -> popMode;
JOB_CREATE          : 'CREATE';
JOB_SHOW            : 'SHOW';
JOB_SET             : 'SET';
JOB_START           : 'START';
JOB_WAIT            : 'WAIT';
JOB_SHUTDOWN        : 'SHUTDOWN';
JOB_ABORT           : 'ABORT';
JOB_TIMER           : 'TIMER';
JOB_REGISTER        : 'REGISTER';
JOB_DEREGISTER      : 'DEREGISTER';
JOB_WORKER          : 'WORKER';
JOB_MANGER          : 'JOBMANAGER';
JOB_ON              : 'ON';
JOB_OFF             : 'OFF';
JOB_TO              : 'TO';
JOB_EXPRESSION      :
    (OBS_TEXT | UNRESERVED | PCTENCODED | DoubleQuoteString | SingleQuoteString | ':' | '/' | '\\' | '{' | '}')+;

mode CompareMode;
COMPARE_SPACE       : [ \t]+ -> channel (HIDDEN);
COMPARE_SEMICOLON   : ';';
COMPARE_EQUAL       : '=>';
COMPARE_CRLF        : CRLF -> popMode;
COMPARE_SET         : 'SET';
COMPARE_UNSET       : 'UNSET';
COMPARE_MASK        : 'MASK';
COMPARE_NOMASK      : 'NOMASK';
COMPARE_MASKLINE    : 'MASKLINE';
COMPARE_NOMASKLINE  : 'NOMASKLINE';
COMPARE_CASE        : 'CASE';
COMPARE_NOCASE      : 'NOCASE';
COMPARE_IGBLANK     : 'IGBLANK';
COMPARE_NOIGBLANK   : 'NOIGBLANK';
COMPARE_TRIM        : 'TRIM';
COMPARE_NOTRIM      : 'NOTRIM';
COMPARE_OUTPUT      : 'OUTPUT';
COMPARE_CONSOLE     : 'CONSOLE';
COMPARE_DIFFFILE    : 'DIFFFILE';
COMPARE_HTMLFILE    : 'HTMLFILE';
COMPARE_SKIPLINE    : 'SKIPLINE';
COMPARE_NOSKIPLINE  : 'NOSKIPLINE';
COMPARE_RESET       : 'RESET';
COMPARE_ALGORITHM   : 'ALGORITHM';
COMPARE_ENCODING    : 'ENCODING';
COMPARE_WORK        : 'WORK';
COMPARE_REFERENCE   : 'REFERENCE';
COMPARE_LCS         : 'LCS';
COMPARE_MYERS       : 'MYERS';
COMPARE_DIFFLIB     : 'DIFFLIB';
COMPARE_AUTO        : 'AUTO';
COMPARE_EXPRESSION  :
    (OBS_TEXT | UNRESERVED | PCTENCODED | DoubleQuoteString | SingleQuoteString | ':' | '/' | '\\' | '{' |'}')+;

mode DataMode;
DATA_SPACE          : [ \t\n]+ -> channel (HIDDEN);
DATA_SEMICOLON      : ';' -> popMode;
DATA_SET            : 'SET';
DATA_SEEDFILE       : 'SEEDFILE';
DATA_DIR            : 'DIR';
DATA_CREATE         : 'CREATE';
DATA_FILE           : 'FILE';
DATA_FILETYPE       : 'FS' | 'MEM' | 'HDFS';
DATA_HDFSUSER       : 'HDFSUSER';
DATA_ROWS           : 'ROWS';
DATA_INT            : INT;
DATA_COMMA          : ',';
DATACOLUMN_OPEN     : '(' -> pushMode(DataColumnMode);
DATA_CONVERT        : 'CONVERT';
DATA_TO             : 'TO';
DATA_EXPRESSION     :
    (OBS_TEXT | UNRESERVED | PCTENCODED | DoubleQuoteString | SingleQuoteString | ':' | '/' | '\\' | '{' | '}')+;

mode DataColumnMode;
DATACOLUMN_SPACE    : [ \t\n]+ -> channel (HIDDEN);
DATACOLUMN_CLOSE    : ')';
DATACOLUMN_CONTENT  : (.*? DATACOLUMN_CLOSE)+ -> popMode;

mode HelpMode;
HELP_SPACE           : [ \t]+ -> channel (HIDDEN);
HELP_COMMAND         : [0-9A-Z]+;
HELP_CRLF            : CRLF -> popMode;
HELP_SEMICOLON       : ';';

mode MonitorMode;
MONITOR_SPACE         : [ \t]+ -> channel (HIDDEN);
MONITOR_MANAGER       : 'MONITORMANAGER';
MONITOR_WORKERS       : 'WORKERS';
MONITOR_CREATE        : 'CREATE';
MONITOR_TASK          : 'TASK';
MONITOR_EQUAL         : '=';
MONITOR_START         : 'START';
MONITOR_STOP          : 'STOP';
MONITOR_REPORT        : 'REPORT';
MONITOR_LIST          : 'LIST';
MONITOR_ON            : 'ON';
MONITOR_OFF           : 'OFF';
MONITOR_EXPRESSION    :
    (OBS_TEXT | UNRESERVED | PCTENCODED | DoubleQuoteString | SingleQuoteString )+;
MONITOR_CRLF          : CRLF -> popMode;
MONITOR_SEMICOLON     : ';';

mode PluginMode;
PLUGIN_SPACE         : [ \t]+ -> channel (HIDDEN);
PLUGIN_EXPRESSION    :
    (OBS_TEXT | UNRESERVED | PCTENCODED | DoubleQuoteString | SingleQuoteString )+;
PLUGIN_CRLF          : CRLF -> popMode;
PLUGIN_SEMICOLON     : ';';

mode SleepMode;
SLEEP_SPACE         : [ \t]+ -> channel (HIDDEN);
SLEEP_EXPRESSION    :
    (OBS_TEXT | UNRESERVED | PCTENCODED | DoubleQuoteString | SingleQuoteString | ':' | '/' | '\\' | '{' | '}')+;
SLEEP_CRLF          : CRLF -> popMode;
SLEEP_SEMICOLON     : ';';
