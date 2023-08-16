from typing import List, Optional, Callable
from error_types import ParserError

from plox_token import PloxToken
from tokenType import TokenType, TokenType as TT
from Expr import *
from Stmt import *


class PloxParser:
    def __init__(self, tokens: List[PloxToken], error:Callable[[PloxToken, str], None]) -> None:
        self.tokens = tokens
        self.current = 0
        self.error = error
        self.loop_count = 0

    def parse(self) -> List[Stmt]:
        statements : List[Stmt, None] = []
        while not self._isAtEnd():
            statements.append(self.declaration())
        return statements
        
    def declaration(self) -> Optional[Stmt]:
        try:
            if self._match(TT.VAR):
                return self.varDeclaration()
            if self._check(TT.FUN) and self._checkNext(TT.IDENTIFIER):
                self._advance()
                return self.function("function")
            if self._match(TT.CLASS):
                return self.class_declaration()
            return self.statement()
        except ParserError:
            self._sync()
            return None

    def class_declaration(self) -> Stmt:
        name : PloxToken = self._consume(TT.IDENTIFIER, "Expected a class name")
        parentclass : Variable = None
        if self._match(TT.COLON, TT.LESS):
            self._consume(TT.IDENTIFIER, "Expected a parent class name")
            parentclass = Variable(self._previous())
        self._consume(TT.LEFT_BRACE, "Expected { \"{\" } before class body")

        methods : List[Function] = []
        while not self._check(TT.RIGHT_BRACE) and not self._isAtEnd():
            methods.append(self.function("method"))
        self._consume(TT.RIGHT_BRACE, "Expected { \"}\" } after class body")

        return ClassStmt(name, parentclass, methods)

    def function(self, kind: str) -> Stmt:
        name : PloxToken = self._consume(TT.IDENTIFIER, f"Expected a {kind} name")
        return Function(name, self.functionBody(kind))

    def functionBody(self, kind: str) -> Expr:
        self._consume(TT.LEFT_PAREN, f"Expected {{(}} after {kind} name")
        params : List[PloxToken] = []
        if not self._check(TT.RIGHT_PAREN):
            params.append(self._consume(TT.IDENTIFIER, "Expected parameter name"))
            while self._match(TT.COMMA):
                if len(params) >= 255:
                    self._error(self._peek(), "Too many parameters! The maximum number of params allowed is 255")
                params.append(self._consume(TT.IDENTIFIER, "Expected parameter name"))
        self._consume(TT.RIGHT_PAREN, "Expected {)} after parameters")
        self._consume(TT.LEFT_BRACE, "Expected { \"{\" } before %s body"%kind)
        body : List[Stmt] = self.block()
        return FuncExpr(params, body, kind)

    def varDeclaration(self) -> Stmt:
        name : PloxToken = self._consume(TT.IDENTIFIER, "Expected a variable name")
        initializer : Expr = None
        if self._match(TT.EQUAL):
            initializer = self.expression()
        self._consume(TT.SEMICOLON, "Expected {;} after variable declaration")
        return Var(name, initializer)

    def statement(self) -> Stmt:
        if self._match(TT.IF): return self.ifStatement()
        if self._match(TT.WHILE): return self.whileStatement()
        if self._match(TT.FOR): return self.forStatement()
        if self._match(TT.BREAK): return self.breakStatement()
        if self._match(TT.CONTINUE): return self.continueStatement()
        if self._match(TT.PRINT): return self.printStatement()
        if self._match(TT.RETURN): return self.returnStatement()
        if self._match(TT.LEFT_BRACE): return Block(self.block())
        if self._match(TT.SEMICOLON): return self.emptyStatement()
        return self.expressionStatement()

    def emptyStatement(self) -> Stmt:
        return Empty()

    def returnStatement(self) -> Stmt:
        keyword : PloxToken = self._previous()
        value = None
        if not self._check(TT.SEMICOLON):
            value = self.expression()
        self._consume(TT.SEMICOLON, "Expected {;} after return value")
        return Return(keyword, value)

    def ifStatement(self) -> Stmt:
        self._consume(TT.LEFT_PAREN, "Expected {(} after {'if'}")
        condition = self.expression()
        self._consume(TT.RIGHT_PAREN, "Expected {)} after if condition")
        thenBranch : Stmt = self.statement()
        elseBranch = None
        if self._match(TT.ELSE):
            elseBranch = self.statement()
        return If(condition, thenBranch, elseBranch)

    def whileStatement(self) -> Stmt:
        self.loop_count += 1
        self._consume(TT.LEFT_PAREN, "Expected {(} after {'while'}")
        condition = self.expression()
        self._consume(TT.RIGHT_PAREN, "Expected {)} after if condition")
        body : Stmt = self.statement()
        body = Block([body, Empty])
        self.loop_count -= 1
        return While(condition, body)

    def forStatement(self) -> Stmt:
        self.loop_count += 1
        self._consume(TT.LEFT_PAREN, "Expected {(} after {'for'}")
        initializer = None
        if self._match(TT.SEMICOLON): initializer = None
        elif self._match(TT.VAR): initializer = self.varDeclaration()
        else: initializer = self.expressionStatement()

        condition = None
        if not self._check(TT.SEMICOLON):
            condition = self.expression()
        self._consume(TT.SEMICOLON, "Expected {;} after loop condition")

        increment = None
        if not self._check(TT.RIGHT_PAREN):
            increment = self.expression()
        self._consume(TT.RIGHT_PAREN, "Expected {)} after for clauses")
        body = self.statement()

        if increment:
            body = Block([body, Expression(increment)])

        if not condition:
            condition = Literal(True)
        body = While(condition, body)

        if initializer:
            body = Block([initializer, body])

        self.loop_count -= 1
        return body

    def breakStatement(self) -> Stmt:
        if self.loop_count == 0:
            raise self._error(self._previous(), "break statement called but no loop was found")
        self._consume(TT.SEMICOLON, "Expected {;} after break")
        return Break()

    def continueStatement(self) -> Stmt:
        if self.loop_count == 0:
            raise self._error(self._previous(), "continue statement called but no loop was found")
        self._consume(TT.SEMICOLON, "Expected {;} after continue")
        return Continue()

    def printStatement(self) -> Stmt:
        value = self.expression()
        self._consume(TT.SEMICOLON, "Expected {;} after value")
        return Print(value)

    def expressionStatement(self) -> Stmt:
        value = self.expression()
        self._consume(TT.SEMICOLON, "Expected {;} after expression")
        return Expression(value)

    def block(self) -> List[Stmt]:
        statements : List[Stmt] = []

        while not self._check(TT.RIGHT_BRACE) and not self._isAtEnd():
            statements.append(self.declaration())
        self._consume(TT.RIGHT_BRACE, "Expected { \"}\" } after block")

        return statements

    def expression(self) -> Expr:
        #skip comma operator for now
        return self.assignment()

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
            elif isinstance(expr, Get):
                get = expr
                return Set(get.obj, get.name, value)
            self._error(equals, "Invalid assignment target")

        return expr

    def conditional(self) -> Expr:
        expr : Expr = self.orExpr()

        if self._match(TT.QUESTION):
            then_clause : Expr = self.expression()
            self._consume(TT.COLON, "Expected {:} after THEN expression")
            else_clause : Expr = self.conditional()
            expr = Conditional(expr, then_clause, else_clause)
        
        return expr
    
    def orExpr(self) -> Expr:
        expr : Expr = self.andExpr()

        while self._match(TT.OR):
            operator : PloxToken = self._previous()
            right = self.andExpr()
            expr = Logical(expr, operator, right)

        return expr

    def andExpr(self) -> Expr:
        expr : Expr = self.equality()

        while self._match(TT.AND):
            operator : PloxToken = self._previous()
            right = self.equality()
            expr = Logical(expr, operator, right)

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
        
        return self.call()

    def call(self) -> Expr:
        expr : Expr = self.primary()

        while True:
            if self._match(TT.LEFT_PAREN):
                expr = self.finishCall(expr)
            elif self._match(TT.DOT):
                name = self._consume(TT.IDENTIFIER, "Expected property name after {.}")
                expr = Get(expr, name)
            else: break

        return expr

    def finishCall(self, callee) -> Expr:
        args = []
        if not self._check(TT.RIGHT_PAREN):
            args.append(self.expression())
            while self._match(TT.COMMA):
                if len(args) >= 255:
                    self._error(self._peek(), "Too many arguments! The maximum number of args allowed is 255")
                args.append(self.expression())

        paren = self._consume(TT.RIGHT_PAREN, "Expected {)} after arguments")
        return Call(callee, paren, args)

    def primary(self) -> Expr:
        if self._match(TT.FALSE): return Literal(False)
        if self._match(TT.TRUE): return Literal(True)
        if self._match(TT.NIL): return Literal(None)
        if self._match(TT.FUN): return self.functionBody("function")
        if self._match(TT.THIS): return This(self._previous())
        if self._match(TT.NUMBER, TT.STRING): return Literal(self._previous().literal)

        if self._match(TT.SUPER, TT.PARENT):
            keyword = self._previous()
            self._consume(TT.DOT, f"Expected {{.}} after {{{keyword.lexeme}}}")
            method = self._consume(TT.IDENTIFIER, "Expected a parent class method name")
            keyword.lexeme = "parent"
            return Parent(keyword,  method)

        if self._match(TT.LEFT_PAREN):
            expr: Expr = self.expression()
            self._consume(TT.RIGHT_PAREN, "Expected {)} after expression")
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

    def _checkNext(self, type: TokenType) -> bool:
        if self._isAtEnd():
            return False
        if self.tokens[self.current + 1].type == TT.EOF:
            return False
        return self.tokens[self.current + 1].type == type

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