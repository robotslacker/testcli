java -jar antlr-4.11.1-complete.jar -o ../antlrgen -package testcli.antlr -visitor -Dlanguage=Python3 -no-listener BaseLexer.g4
java -jar antlr-4.11.1-complete.jar -o ../antlrgen -package testcli.antlr -visitor -Dlanguage=Python3 -no-listener BaseParser.g4
java -jar antlr-4.11.1-complete.jar -o ../antlrgen -package testcli.antlr -visitor -Dlanguage=Python3 -no-listener SQLLexer.g4
java -jar antlr-4.11.1-complete.jar -o ../antlrgen -package testcli.antlr -visitor -Dlanguage=Python3 -no-listener SQLParser.g4
java -jar antlr-4.11.1-complete.jar -o ../antlrgen -package testcli.antlr -visitor -Dlanguage=Python3 -no-listener APILexer.g4
java -jar antlr-4.11.1-complete.jar -o ../antlrgen -package testcli.antlr -visitor -Dlanguage=Python3 -no-listener APIParser.g4

