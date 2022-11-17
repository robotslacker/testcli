lexer grammar TextLexer;

options {
    caseInsensitive = true;
}

// 分割符号
CRLF              : '\n';
COMMA             : ',';
SEMICOLON         : ';';
DOT               : '.';
BRACKET_OPEN      : '(';
BRACKET_CLOSE     : ')';
SQUARE_OPEN       : '[';
SQUARE_CLOSE      : ']';
DOUBLE_QUOTE      : '"';
SINGLE_QUOTE      : '\'';
ESCAPE            : '\\';
SPACE             : [ \t]+ ->channel(HIDDEN);

CONNECT: 'CONNECT';

CONNECT_SPACE
            : [ \t]+
            ;

CONNECT_CRLF
            : '\n'
            ;

CONNECT_AT
            : '@'
            ;

CONNECT_SLASH
            : '/'
            ;

CONNECT_COLON
            : ':'
            ;

CONNECT_QUESTION
            : '?'
            ;

CONNECT_POUND
            : '#'
            ;

CONNECT_OR
            : '|'
            ;

CONNECT_DASH
            : '//'
            ;

CONNECT_EQUAL
            : '='
            ;

CONNECT_PARA_AND
            : '&'
            ;

JDBC: 'JDBC';

IPV4
            : DIGIT+ '.' DIGIT+ '.' DIGIT+ '.' DIGIT+
            ;

// Fragments
fragment DIGIT: [0-9];
fragment ALPHA: [A-Z];
fragment HEX: [0-9A-F];

// 双引号字符串
fragment DoubleQuoteString: '"' (~'"' | '\\' ('\n' | .))* '"';
// 单引号字符串
fragment SingleQuoteString: '\'' (~'\'' | '\\' ('\r'? '\n' | .))* '\'';


fragment CONNECT_DOUBLEQUOTE
            : '"' (~'"' | '\\' ('\r'? '\n' | .))* '"'
            ;

fragment CONNECT_SINGLEQUOTE
            : '\'' (~'\'' | '\\' ('\r'? '\n' | .))* '\''
            ;

fragment OBS_TEXT: '\u00ff' ..'\uffff';

fragment UNRESERVED
            : ALPHA | DIGIT | '-' | '.' | '_' | '~'
            ;

fragment SUBDELIMS
            : '!' | '$' | '&' | '(' | ')' | '*' | '+' | '='
            ;

fragment PCTENCODED
            : '%' HEX HEX
            ;

CONNECT_STRING
            : (OBS_TEXT | UNRESERVED | PCTENCODED | CONNECT_DOUBLEQUOTE | CONNECT_SINGLEQUOTE)+
            ;

