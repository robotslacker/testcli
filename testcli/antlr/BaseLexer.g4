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

EXIT                : 'EXIT';
QUIT                : 'QUIT';
USE                 : 'USE';
API                 : 'API';
SQL                 : 'SQL';
START               : 'START';
WHENEVER_ERROR      : 'WHENEVER_ERROR';
CONTINUE            : 'CONTINUE';
LOOP                : 'LOOP';
SPOOL               : 'SPOOL';
END                 : 'END';
SET                 : 'SET';
SLEEP               : 'SLEEP';

// 回显随后的脚本
ECHO_OPEN           : 'ECHO' .*? (CRLF | EOF) ->pushMode(EchoMode);

// 执行内置的脚本
SCRIPT_OPEN         : '> {%' ->pushMode(ScriptMode);

// 表达式判断，用来验证执行结果
ASSERT              :  'ASSERT' -> pushMode(AssertMode);

// 加载驱动或者映射关系
LOAD                : '_LOAD' -> pushMode(LoadMode);
HOST                : '_HOST' -> pushMode(HostMode);

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

mode HostMode;
HOST_SPACE         : [ \t]+ -> channel (HIDDEN);
HOST_TAG           : '"""';
HOST_BLOCK         :HOST_TAG '\n' .*? '\n' HOST_TAG -> popMode;
