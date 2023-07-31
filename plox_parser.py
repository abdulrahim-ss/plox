from typing import List, Optional, Callable

from plox_token import PloxToken
from tokenType import TokenType, TokenType as TT
from Expr import *
from Stmt import *

class ParserError(Exception):
    pass

class PloxParser:
    def __init__(self, tokens: List[PloxToken], error:Callable[[PloxToken, str], None]) -> None:
        self.tokens = tokens
        self.current = 0
        self.error = error

    def parse(self) -> List[Stmt]:
        statements : List[Stmt, None] = []
        while not self._isAtEnd():
            statements.append(self.declaration())
        return statements
        
    def declaration(self) -> Optional[Stmt]:
        try:
            if self._match(TT.VAR):
                return self.varDeclaration()
            return self.statement()
        except ParserError:
            self._sync()
            return None

    def varDeclaration(self) -> Stmt:
        name : PloxToken = self._consume(TT.IDENTIFIER, "Expected a variable name")
        initializer : Expr = None
        if self._match(TT.EQUAL):
            initializer = self.expression()
        self._consume(TT.SEMICOLON, "Expected \";\" after variable declaration")
        return Var(name, initializer)

    def statement(self) -> Stmt:
        if self._match(TT.PRINT): return self.printStatement()
        return self.expressionStatement()
    
    def printStatement(self) -> Stmt:
        value = self.expression()
        self._consume(TT.SEMICOLON, "Expected \";\" after value")
        return Print(value)

    def expressionStatement(self) -> Stmt:
        value = self.expression()
        self._consume(TT.SEMICOLON, "Expected \";\" after expression")
        return Expression(value)

    def expression(self) -> Expr:
        return self.comma()

    def comma(self) -> Expr:
        expr : Expr = self.assignment()

        while self._match(TT.COMMA):
            operator : PloxToken = self._previous()
            right : Expr = self.assignment()
            expr = Binary(expr, operator, right)

        return expr

    def assignment(self) -> Expr:
        expr : Expr = self.conditional()

        if self._match(TT.EQUAL):
            equals = self._previous()
            value = self.assignment()
            if isinstance(expr, Variable):
                name = expr.name
                return Assign(name, value)
            self._error(equals, "Invalid assignment target")

        return expr

    def conditional(self) -> Expr:
        expr : Expr = self.equality()

        if self._match(TT.QUESTION):
            then_clause : Expr = self.expression()
            self._consume(TT.COLON, "Expected \":\" after THEN expression")
            else_clause : Expr = self.conditional()
            expr = Conditional(expr, then_clause, else_clause)
        
        return expr

    def equality(self) -> Expr:
        expr : Expr = self.comparison()

        while self._match(TT.BANG_EQUAL, TT.EQUAL_EQUAL):
            operator : PloxToken = self._previous()
            right : Expr = self.comparison()
            expr = Binary(expr, operator, right)

        return expr

    def comparison(self) -> Expr:
        expr : Expr = self.term()

        while self._match(TT.GREATER, TT.GREATER_EQUAL, TT.LESS, TT.LESS_EQUAL):
            operator: PloxToken = self._previous()
            right : Expr = self.term()
            expr = Binary(expr, operator, right)

        return expr

    def term(self) -> Expr:
        expr : Expr = self.factor()

        while self._match(TT.MINUS, TT.PLUS):
            operator: PloxToken = self._previous()
            right : Expr = self.factor()
            expr = Binary(expr, operator, right)

        return expr

    def factor(self) -> Expr:
        expr : Expr = self.unary()

        while self._match(TT.SLASH, TT.STAR):
            operator: PloxToken = self._previous()
            right: Expr = self.unary()
            expr: Expr = Binary(expr, operator, right)

        return expr

    def unary(self) -> Expr:
        if self._match(TT.MINUS, TT.BANG):
            operator: PloxToken = self._previous()
            right: Expr = self.unary()
            return Unary(operator, right)
        
        return self.primary()

    def primary(self) -> Expr:
        if self._match(TT.FALSE): return Literal(False)
        if self._match(TT.TRUE): return Literal(True)
        if self._match(TT.NIL): return Literal(None)

        if self._match(TT.NUMBER, TT.STRING): return Literal(self._previous().literal)

        if self._match(TT.LEFT_PAREN):
            expr: Expr = self.expression()
            self._consume(TT.RIGHT_PAREN, "Expected ')' after expression")
            return Grouping(expr)
        
        if self._match(TT.IDENTIFIER): return Variable(self._previous())
        
        # Error production
        if self._match(
            TT.BANG_EQUAL, TT.EQUAL_EQUAL,
            TT.GREATER, TT.GREATER_EQUAL, TT.LESS, TT.LESS_EQUAL,
            TT.PLUS,
            TT.STAR, TT.SLASH,
            ):
            self._error(self._previous(), "Missing left-hand operand")
            self.expression()
            return

        raise self._error(self._peek(), "Expected expression")

#####################################################

    def _advance(self) -> PloxToken:
        if not self._isAtEnd(): self.current += 1
        return self._previous()

    def _match(self, *types: TokenType) -> bool:
        for t in types:
            if self._check(t):
                self._advance()
                return True
        return False
    
    def _check(self, type: TokenType) -> bool:
        if self._isAtEnd():
            return False
        return self._peek().type == type

    def _isAtEnd(self) -> bool:
        return self._peek().type == TT.EOF

    def _peek(self) -> PloxToken:
        return self.tokens[self.current]
    
    def _previous(self) -> PloxToken:
        return self.tokens[self.current - 1]

####################################################

    def _consume(self, type: TokenType, message: str) -> PloxToken:
        if self._check(type):
            return self._advance()
        raise self._error(self._peek(), message)

    def _error(self, token: PloxToken, message: str) -> ParserError:
        self.error(token, message)
        return ParserError
        
    def _sync(self) -> None:
        self._advance()
        while not self._isAtEnd():
            if self._previous().type == TT.SEMICOLON or \
            self._peek().type in (
                TT.CLASS,
                TT.FUN,
                TT.VAR,
                TT.FOR,
                TT.IF,
                TT.WHILE,
                TT.PRINT,
                TT.RETURN,
                ):
                return
            self._advance()


####################################################


if __name__ == "__main__":
    tokens = [
        PloxToken(TT.PRINT, "print", None, 1),
        PloxToken(TT.STRING, "test", "test", 1),
        PloxToken(TT.SEMICOLON, ";", None, 1),
        PloxToken(TT.EOF, "", None, 1),
    ]
    from plox import PLox
    l = PLox([""])
    error = l.parsing_error
    p = PloxParser(tokens, error)
    try:
        x = p.parse()
        for _ in x:
            print(_)
    except Exception as e:
        print(e)