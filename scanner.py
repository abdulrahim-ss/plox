from typing import List, Callable

from typing import Callable
from plox_token import PloxToken
from tokenType import TokenType, TokenType as TT


class Scanner:
    keywords = {
        'and':    TT.AND,
        'class':  TT.CLASS,
        'else':   TT.ELSE,
        'false':  TT.FALSE,
        'for':    TT.FOR,
        'fun':    TT.FUN,
        'if':     TT.IF,
        'nil':    TT.NIL,
        'or':     TT.OR,
        'print':  TT.PRINT,
        'return': TT.RETURN,
        'super':  TT.SUPER,
        'this':   TT.THIS,
        'true':   TT.TRUE,
        'var':    TT.VAR,
        'while':  TT.WHILE,
    }

    def __init__(self, source: str, error:Callable[[int, str], None]) -> None:
        self.start:int = 0
        self.current:int = 0
        self.line:int = 1

        self.source = source
        self.tokens: List[PloxToken] = []

        self.error = error

    def scanTokens(self) -> List[PloxToken]:
        while not self.isAtEnd():
            self.start = self.current
            self.scanToken()

        self.tokens.append(PloxToken(TT.EOF, "", None, self.line))
        return self.tokens
    
    def isAtEnd(self) -> bool:
        return self.current >= len(self.source)
    
    def scanToken(self) -> None:
        c = self.advance()

        match c:
            #SINGLE-CHARACTER TOKENS
            case "(": self.addToken(TT.LEFT_PAREN)
            case ")": self.addToken(TT.RIGHT_PAREN)
            case "{": self.addToken(TT.LEFT_BRACE)
            case "}": self.addToken(TT.RIGHT_BRACE)
            case ",": self.addToken(TT.COMMA)
            case ".": self.addToken(TT.DOT)
            case "-": self.addToken(TT.MINUS)
            case "+": self.addToken(TT.PLUS)
            case ";": self.addToken(TT.SEMICOLON)
            case "*": self.addToken(TT.STAR)
            case "?": self.addToken(TT.QUESTION)
            case ":": self.addToken(TT.COLON)
            #SPECIAL SINGLE-CHARACTER OPERATOR TOKENS
            case "!":
                t = TT.BANG_EQUAL if self.match('=') else TT.BANG
                self.addToken(t)
            case "=":
                t = TT.EQUAL_EQUAL if self.match('=') else TT.EQUAL
                self.addToken(t)
            case "<":
                t = TT.LESS_EQUAL if self.match('=') else TT.LESS
                self.addToken(t)
            case ">":
                t = TT.GREATER_EQUAL if self.match('=') else TT.GREATER
                self.addToken(t)
            case '/':
                if self.match('/'):
                    while self.peek() != '\n' and self.peek() != '\0':
                        self.advance()
                elif self.match('*'):
                    nested = 0
                    while self.peek() != '\0':
                        temp_char = self.advance()
                        if temp_char == '/' and self.peek() == '*': nested += 1
                        if temp_char == '*' and self.peek() == '/':
                            if nested < 1:
                                break
                            nested -= 1
                            self.advance()
                        if temp_char == '\n': self.line += 1
                    if not self.isAtEnd() : self.advance() # consume last slash
                else:
                    self.addToken(TT.SLASH)
            case ' ':
                pass
            case '\t':
                pass
            case '\r':
                pass
            case '\n':
                self.line += 1
            #LITERALS
            case '\"': self.string()

            case _: 
                if self.is_digit(c):
                    self.number()
                elif self.is_alpha(c):
                    self.identifier()
                else:
                    self.error(self.line, f"Unexpected Character \"{c}\"")

    def advance(self) -> str:
        self.current += 1
        return self.source[self.current-1]
    
    def match(self, expected:str) -> bool:
        if self.isAtEnd(): return False
        if self.source[self.current] == expected: 
            self.current += 1
            return True
        return False
    
    def peek(self) -> str:
        if self.isAtEnd(): return '\0'
        return self.source[self.current]
    
    def string(self) -> None:
        value = ""
        while self.peek() != '\"':
            if self.peek() == '\0': break
            c = self.advance()
            if c == '\n': self.line += 1
            value += c
        else:
            self.advance()
            self.addToken(TT.STRING, value)
            return
        self.error(self.line, "Unterminated string")

    def number(self) -> None:
        number = self.source[self.start]
        while self.is_digit(self.peek()): number += self.advance()
        if self.peek() == '.':
            number += self.advance()
            if self.is_digit(self.peek()):
                while self.is_digit(self.peek()): number += self.advance()
            else:
                self.error(self.line, "Number value format is incorrect.")
                return
        number = float(number)
        self.addToken(TT.NUMBER, number)

    def identifier(self) -> None:
        identifier = self.source[self.start]
        while self.is_alpha_numeric(self.peek()): identifier += self.advance()
        type = self.keywords.get(identifier)
        if not type: type = TT.IDENTIFIER
        self.addToken(type)

    def is_alpha_numeric(self, c: str) -> bool:
        return self.is_alpha(c) or self.is_digit(c)
    
    @staticmethod
    def is_alpha(c: str) -> bool:
        return ('a' <= c <= 'z') or ('A' <= c <= 'Z') or (c == '_')

    @staticmethod
    def is_digit(c: str) -> bool:
        return '0' <= c <= '9'

    def addToken(self, type: TokenType, literal: object = None) -> None:
        text = self.source[self.start:self.current]
        self.tokens.append(PloxToken(type, text, literal, self.line))
