lexer grammar SQLLexer;
import BaseLexer;

options { 
    caseInsensitive = true;
}

channels {SQLSTATEMENT_CHANNEL }

// 关键字
CONNECT: '_CONNECT' -> pushMode(ConnectMode);
SESSION: '_SESSION' -> pushMode(SessionMode);

DISCONNECT: '_DISCONNECT';

// --SQL注释
MINUS_MINUS_COMMENT   : '--' .*? (CRLF | EOF) ->channel(HIDDEN);

// SQL创建语句
SQL_CREATE:     'CREATE' -> mode(SQLStatementMode) ;
SQL_INSERT:     'INSERT' -> mode(SQLStatementMode) ;
SQL_UPDATE:     'UPDATE' -> mode(SQLStatementMode) ;
SQL_SELECT:     'SELECT' -> mode(SQLStatementMode) ;
SQL_DELETE:     'DELETE'  -> mode(SQLStatementMode) ;
SQL_REPLACE:    'REPLACE' -> mode(SQLStatementMode);
SQL_DECLARE:    'DECLARE' -> mode(SQLProcedureMode) ;
SQL_BEGIN:      'BEGIN' -> mode(SQLProcedureMode) ;
SQL_DROP:       'DROP' -> mode(SQLStatementMode) ;
SQL_COMMIT:     'COMMIT' -> mode(SQLStatementMode) ;
SQL_ROLLBACK:   'ROLLBACK' -> mode(SQLStatementMode) ;
SQL_CREATE_PROCEDURE: ('CREATE' | 'REPLACE' | 'ALTER'| ' '+ | 'OR')+ ('PROCEDURE'|'FUNCTION'|'CLASS'|'TRIGGER'|'PACKAGE')
                             ->mode(SQLProcedureMode);

/**
 * 数据库连接模式
 */
mode ConnectMode;

CONNECT_SPACE
            : [ \t]+ -> channel (HIDDEN) 
            ;

CONNECT_CRLF
            : '\n' ->type(CRLF), popMode
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

CONNECT_SEMICOLON
            : ';'
            ;

JDBC: 'JDBC';

IPV4
            : DIGIT+ '.' DIGIT+ '.' DIGIT+ '.' DIGIT+ 
            ;

IPV6
            : '[' (HEX | ':' | '.') + ']'
            ;

fragment CONNECT_DOUBLEQUOTE
            : '"' (~'"' | '\\' ('\r'? '\n' | .))* '"'
            ;

fragment CONNECT_SINGLEQUOTE
            : '\'' (~'\'' | '\\' ('\r'? '\n' | .))* '\''
            ;

CONNECT_STRING
            : (OBS_TEXT | UNRESERVED | PCTENCODED | CONNECT_DOUBLEQUOTE | CONNECT_SINGLEQUOTE | '{' | '}')+
            ;


/**
 * 注释模式
 */
mode CommentMode;

COMMENT_CRLF
      : '\n' ->type(CRLF), popMode
      ;

CommentString
      : ~('\n')+
      ;


/**
 * 提示模式
 */
mode HintMode;

HINT_SP
      : [ \t]+ -> channel (HIDDEN)
      ;

HINT
      : 'HINT'
      ;

HINT_SQUARE_OPEN
      : '[' ->type(SQUARE_OPEN)
      ;

HINT_SQUARE_CLOSE
      : ']' ->type(SQUARE_CLOSE)
      ;

HINT_CLOSE
      : '\n' -> popMode
      ;

HINT_STRING
      : String
      ;

HintMore
      : . -> type(HINT_STRING)
      ;

mode SessionMode;
SESSION_SPACE
            : [ \t]+ -> channel(SQLSTATEMENT_CHANNEL)
            ;
SESSION_SAVE
        : 'SAVE';
SESSION_RELEASE
        : 'RELEASE';
SESSION_RESTORE
        : 'RESTORE';
SESSION_SAVEURL
        : 'SAVEURL';
SESSION_SHOW
        : 'SHOW';
SESSION_NAME
            : String
            ;
SESSION_END
        : ';'->mode(DEFAULT_MODE)
        ;

/**
 * SQL语句
 */
mode SQLStatementMode;

SQL_CRLF
            : '\n' -> channel(SQLSTATEMENT_CHANNEL)
            ;

SQL_SPACE
            : [ \t]+ -> channel(SQLSTATEMENT_CHANNEL)
            ;

SQL_SLASH_END
            : '\n' '/' ->type(SQL_END), mode(DEFAULT_MODE)
            ;

SQL_END
            : ';' ->mode(DEFAULT_MODE)
            ;

SQL_STRING
            : String ->channel(SQLSTATEMENT_CHANNEL)
            ;

SQL_SINGLE
            : SingleQuoteString ->channel(SQLSTATEMENT_CHANNEL)
            ;

SQL_OTHER
            : . -> channel(SQLSTATEMENT_CHANNEL)
            ;

mode SQLProcedureMode;

SQL_PROCEDURE_CRLF
            : '\n' ->channel(SQLSTATEMENT_CHANNEL)
            ;

SQL_SLASH
            : '\n' '/'->mode(DEFAULT_MODE)
            ;

SQL_PROCEDURE_SLASH
            : '/' ->channel(SQLSTATEMENT_CHANNEL)
            ;

SQLProcedureStatement
            : ~('\n'|'/')+ -> channel(SQLSTATEMENT_CHANNEL)
            ;
