from enum import Enum


class TokenType(Enum):
    #Single-character tokens.
    (LEFT_PAREN, RIGHT_PAREN, LEFT_BRACE, RIGHT_BRACE, LEFT_BRACKET, RIGHT_BRACKET,
    COMMA, DOT, MINUS, PLUS, SEMICOLON, SLASH, STAR,
    QUESTION, COLON,

    # One or two character tokens.
    BANG, BANG_EQUAL,
    EQUAL, EQUAL_EQUAL,
    GREATER, GREATER_EQUAL,
    LESS, LESS_EQUAL,

    # Literals.
    IDENTIFIER, STRING, NUMBER,

    # Keywords.
    AND, CLASS, ELSE, FALSE, FUN, FOR, IF, NIL, OR,
    PRINT, RETURN, SUPER, PARENT, THIS, TRUE, VAR, WHILE, BREAK, CONTINUE,
    
    EOF) = range(46)
