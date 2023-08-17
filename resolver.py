from typing import List, Callable, Type

from Expr import *
from Stmt import *
from plox_token import PloxToken

class Resolver(StmtVisitor, ExprVisitor):
    def __init__(self, interpreter, error: Callable[[PloxToken, str], None]) -> None:
        self.interpreter = interpreter
        self.error = error
        self.scopes: List[dict] = []
        self.current_function = None
        self.current_class = None

    def visitBlock(self, stmt: Block) -> None:
        self.begin_scope()
        self.resolve(stmt.statements)
        self.end_scope()

    def visitVar(self, stmt: Var) -> None:
        self.declare(stmt.name)
        if stmt.Initializer is not None:
            self._resolve(stmt.Initializer)
        self.define(stmt.name)

    def visitVariable(self, expr: Variable) -> None:
        if not (len(self.scopes) == 0) and self.scopes[-1].get(expr.name.lexeme) == False:
            self.error(expr.name, "Can't read local variable in its own initializer")
        self.resolveLocal(expr, expr.name)

    def visitAssign(self, expr: Assign) -> None:
        self._resolve(expr.value)
        self.resolveLocal(expr, expr.name)

    def visitClassStmt(self, stmt: ClassStmt) -> None:
        enclosing_class = self.current_class
        self.current_class = "class"
        self.declare(stmt.name)
        self.define(stmt.name)
        if stmt.parentclass:
            self.current_class = "childclass"
            if stmt.name.lexeme == stmt.parentclass.name.lexeme:
                self.error(stmt.parentclass.name, "A class can't inherit from itself")
                return
            self._resolve(stmt.parentclass)
            self.begin_scope()
            self.scopes[-1]["parent"] = True
        self.begin_scope()
        self.scopes[-1]["this"] = True
        for method in stmt.methods:
            declaration = "method"
            if method.name.lexeme == "init":
                declaration = "initializer"
            self.resolveFunction(method.function, declaration)
        self.end_scope()
        if stmt.parentclass: self.end_scope()
        self.current_class = enclosing_class

    def visitFunction(self, stmt: Function) -> None:
        self.declare(stmt.name)
        self.define(stmt.name)
        self.resolveFunction(stmt.function, "function")

    def visitExpression(self, stmt: Expression) -> None:
        self._resolve(stmt.expression)

    def visitIf(self, stmt: If) -> None:
        self._resolve(stmt.condition)
        self._resolve(stmt.thenBranch)
        if stmt.elseBranch: self._resolve(stmt.thenBranch)

    def visitPrint(self, stmt: Print) -> None:
        self._resolve(stmt.expression)

    def visitReturn(self, stmt: Return) -> None:
        if self.current_function is None:
            self.error(stmt.keyword, "Can't return from top-level code")
        if stmt.value:
            if self.current_function == "initializer":
                self.error(stmt.keyword, "Can't return a value from an initializer")
            self._resolve(stmt.value)

    def visitWhile(self, stmt: While) -> None:
        self._resolve(stmt.condition)
        self._resolve(stmt.body)

    def visitBreak(self, stmt: Break) -> None:
        return None

    def visitContinue(self, stmt: Continue) -> None:
        return None

    def visitListExpr(self, expr: ListExpr) -> None:
        for expression in expr.values:
            self._resolve(expression)

    def visitBinary(self, expr: Binary) -> None:
        self._resolve(expr.left)
        self._resolve(expr.right)

    def visitFuncExpr(self, expr: FuncExpr) -> None:
        self.resolveFunction(expr, "function")

    def visitCall(self, expr: Call) -> None:
        self._resolve(expr.callee)
        for arg in expr.arguments:
            self._resolve(arg)

    def visitSubscriptable(self, expr: Subscriptable) -> None:
        self._resolve(expr.subscribee)
        self._resolve(expr.index)


    def visitGet(self, expr: Get) -> None:
        self._resolve(expr.obj)

    def visitSet(self, expr: Set) -> None:
        self._resolve(expr.value)
        self._resolve(expr.obj)

    def visitThis(self, expr: This) -> None:
        if self.current_class is None:
            self.error(expr.keyword, "Tried calling {this} outside of a class")
            return
        self.resolveLocal(expr, expr.keyword)

    def visitParent(self, expr: Parent) -> None:
        if not self.current_class:
            self.error(expr.keyword, f"Can't use {{{expr.keyword.lexeme}}} outside of a class")
        elif not self.current_class == "childclass":
            self.error(expr.keyword, f"Can't use {{{expr.keyword.lexeme}}} with no parent class")
        self.resolveLocal(expr, expr.keyword)

    def visitConditional(self, expr: Conditional) -> None:
        self._resolve(expr.condition)
        self._resolve(expr.then_clause)
        self._resolve(expr.else_clause)

    def visitGrouping(self, expr: Grouping) -> None:
        self._resolve(expr.expression)

    def visitLiteral(self, expr: Literal) -> None:
        return None

    def visitEmpty(self, expr: Empty) -> None:
        return None
    
    def visitLogical(self, expr: Logical) -> None:
        self._resolve(expr.left)
        self._resolve(expr.right)
    
    def visitUnary(self, expr: Unary) -> None:
        self._resolve(expr.right)

    def declare(self, name: PloxToken) -> None:
        if len(self.scopes) == 0: return
        scope = self.scopes[-1]
        if name.lexeme in scope.keys():
            self.error(name, "Already a variable with this name in this scope")
        self.scopes[-1][name.lexeme] = False

    def define(self, name: PloxToken) -> None:
        if len(self.scopes) == 0: return
        self.scopes[-1][name.lexeme] = True

    def resolveLocal(self, expr: Expr, name: PloxToken) -> None:
        for scope in reversed(self.scopes):
            if name.lexeme in scope.keys():
                depth = len(self.scopes) - self.scopes.index(scope)
                # print(name.lexeme, depth, len(self.scopes))
                self.interpreter._resolve(expr, depth)
                return
            
    def resolveFunction(self, function: FuncExpr, type: str) -> None:
        enclosing_function = self.current_function
        self.current_function = type
        self.begin_scope()
        for param in function.params:
            self.declare(param)
            self.define(param)
        self.resolve(function.body)
        self.end_scope()
        self.current_function = enclosing_function

    def resolve(self, statements: List[Stmt]) -> None:
        for statement in statements:
            self._resolve(statement)
        # print(self.scopes)

    def _resolve(self, visited: Stmt | Expr) -> None:
        visited.accept(self)

    def begin_scope(self) -> None:
        self.scopes.append(dict())

    def end_scope(self) -> None:
        self.scopes.pop()
