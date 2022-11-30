// 基础词法
lexer grammar BaseLexer;

options {
    caseInsensitive = true;
}

channels { HINT_CHANNEL, COMMENT_CHANNEL, SQLSTATEMENT_CHANNEL }

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
SPOOL               : '_SPOOL';
SLEEP               : '_SLEEP';

// 切换应用模式
USE                 : '_USE' -> pushMode(UseMode);

// 回显随后的脚本
ECHO_OPEN           : '_ECHO' .*? (CRLF | EOF) ->pushMode(EchoMode);

// 执行内置的Python脚本
SCRIPT_OPEN         : '> {%' ->pushMode(ScriptMode);

// 表达式判断，用来验证执行结果
ASSERT              :  '_ASSERT' -> pushMode(AssertMode);

// 执行脚本
START               : '_START' -> pushMode(StartMode);

// 加载驱动或者映射关系
LOAD                : '_LOAD' -> pushMode(LoadMode);

// 执行主机操作系统命令
HOST                : '_HOST' -> pushMode(HostMode);

// 条件表达式判断
IF                  : '_IF' -> pushMode(IfMode);
ENDIF               : '_ENDIF';

// 设置系统参数
SET                 : '_SET' -> pushMode(SetMode);

// 循环执行
LOOP                : '_LOOP' -> pushMode(LoopMode);

// 一旦错误，将会执行的操作
WHENEVER            : '_WHENEVER' -> pushMode(WheneverMode);

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
ASSERT_EXPRESSION   : ASSERT_OPEN .*? ASSERT_CLOSE -> popMode;

mode LoadMode;
LOAD_SPACE          : [ \t]+ -> channel (HIDDEN);
LOAD_OPTION         : 'PLUGIN' | 'MAP' | 'DRIVER';
LOAD_EXPRESSION     : String;
LOAD_CRLF           : CRLF -> popMode;

mode StartMode;
START_SPACE        : [ \t]+ -> channel (HIDDEN);
START_LOOP         : 'LOOP';
START_INT          : INT;
START_COMMA        : ',';
START_EXPRESSION   :
    (OBS_TEXT | UNRESERVED | SUBDELIMS | PCTENCODED | DoubleQuoteString | SingleQuoteString | ':' | '/' | '\\' )+;
START_CRLF         : CRLF -> popMode;

mode HostMode;
HOST_SPACE         : [ \t]+ -> channel (HIDDEN);
HOST_TAG           : '"""';
HOST_BLOCK         :HOST_TAG '\n' .*? '\n' HOST_TAG -> popMode;

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

mode SetMode;
SET_SPACE           : [ \t]+ -> channel (HIDDEN);
SET_EXPRESSION      : String;
SET_SEMICOLON       : ';';
SET_AT              : '@';
SET_CRLF            : CRLF -> popMode;

mode UseMode;
USE_API             : 'API';
USE_SQL             : 'SQL';
USE_SPACE           : [ \t]+ -> channel (HIDDEN);
USE_SEMICOLON       : ';';
USE_CRLF            : CRLF -> popMode;
