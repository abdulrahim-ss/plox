from typing import List, Any, Callable, Type

from Expr import *
from Expr import Assign
from Stmt import *
from Stmt import Expression, Var
from plox_token import PloxToken
from tokenType import TokenType as TT
from environment import Environment

class RunTimeError(RuntimeError):
    def __init__(self, token: PloxToken, msg: str):
        super().__init__(msg)
        self.token = token


class Interpreter(ExprVisitor, StmtVisitor):
    #TODO: get the comma operator to work
    def __init__(self, error: Callable[[Type[Exception]], None], repl: bool = False):
        self.error = error
        self.repl = repl
        self.env = Environment(RunTimeError)

    def interpret(self, statements: List[Stmt]) -> None:
        try:
            for statement in statements:
                self._exec(statement)
        except RunTimeError as err:
            self.error(err)

    def visitBlock(self, stmt: Block) -> None:
        self._exec_block(stmt.statements, Environment(RunTimeError, self.env))

    def visitExpression(self, stmt: Expression) -> None:
        value = self._eval(stmt.expression)
        if self.repl:
            print(self._stringify(value))

    def visitPrint(self, stmt: Print) -> None:
        value = self._eval(stmt.expression)
        print(self._stringify(value))

    def visitVar(self, stmt: Var) -> None:
        value = None
        if stmt.Initializer is not None:
            value = self._eval(stmt.Initializer)
        self.env.assign(stmt.name.lexeme, value)

    def visitAssign(self, expr: Assign) -> object:
        value = self._eval(expr.value)
        self.env.assign_existing(expr.name.lexeme, value)
        return value

    def visitLiteral(self, expr: Literal) -> object:
        return expr.value

    def visitVariable(self, expr: Variable) -> object:
        return self.env.fetch(expr.name)

    def visitGrouping(self, expr: Grouping) -> object:
        return self._eval(expr.expression)

    def visitUnary(self, expr: Unary) -> object:
        right = self._eval(expr.right)

        match expr.operator.type:
            case TT.MINUS:
                self._checkNumber(expr.operator, right)
                return - right
            case TT.BANG:
                return not self._isTruthy(right)
            
    def visitBinary(self, expr: Binary) -> object:
        left = self._eval(expr.left)
        right = self._eval(expr.right)

        match expr.operator.type:
            # Arithmatic -------------------------------------------
            case TT.MINUS:
                self._checkNumber(expr.operator, left, right)
                return left - right
            case TT.SLASH:
                self._checkNumber(expr.operator, left, right)
                try:
                    return left / right
                except ZeroDivisionError:
                    raise RunTimeError(expr.operator, "Tried dividing by zero")
            case TT.STAR:
                self._checkNumber(expr.operator, left, right)
                return left * right
            case TT.PLUS:
                if isinstance(left, str) or isinstance(right, str):
                    return self._stringify(left) + self._stringify(right)
                else:
                    return self._numify(left) + self._numify(right)
            # Comparison -------------------------------------------
            case TT.GREATER:
                # self._checkNumber(expr.operator, left, right)
                return self._numify(left) > self._numify(right)
            case TT.GREATER_EQUAL:
                # self._checkNumber(expr.operator, left, right)
                return self._numify(left) >= self._numify(right)
            case TT.LESS:
                # self._checkNumber(expr.operator, left, right)
                return self._numify(left) < self._numify(right)
            case TT.LESS_EQUAL:
                # self._checkNumber(expr.operator, left, right)
                return self._numify(left) <= self._numify(right)
            # Comaprison - equality --------------------------------
            case TT.EQUAL_EQUAL:
                return left == right
            case TT.BANG_EQUAL:
                return not (left == right)
            
    def visitConditional(self, expr: Conditional) -> object:
        if self._isTruthy(self._eval(expr.condition)):
            return self._eval(expr.then_clause)
        else:
            return self._eval(expr.else_clause)

    ################################################

    @staticmethod
    def _numify(value: object) -> float:
        if value is False: return 0
        if value is True: return 1
        if value is None: return -1
        if isinstance(value, str): return int.from_bytes(value.encode(), "big", signed=False)
        return float(value)

    @staticmethod
    def _stringify(value: object) -> str:
        if value is None:
            return "nil"
        if str(value).endswith(".0"): return str(value).split(".")[0]
        if value is True: return "true"
        if value is False: return "false"
        return str(value)

    @staticmethod
    def _isTruthy(obj: object) -> bool:
        if obj is None: return False
        if isinstance(obj, bool): return bool(obj)
        if isinstance(obj, str) or isinstance(obj, list):
            if len(obj) == 0: return False
        if isinstance(obj, float) and obj == 0:
            return False
        return True
    
    @staticmethod
    def _isEqual(a: object, b: object) -> bool:
        return (a is None) ^ (b is None)
    
    @staticmethod
    def _checkNumber(operator: Expr, *operands: object) -> None:
        if len(operands) == 1:
            if isinstance(operands[0], float): return
            else:
                raise RunTimeError(operator, "Operand must be a number")
        for operand in operands:
            if isinstance(operand, float): continue
            else:
                raise RunTimeError(operator, "Operands must be numbers")

    def _exec(self, stmt: Stmt) -> None:
        stmt.accept(self)

    def _exec_block(self, statements: List[Stmt], env: Environment) -> None:
        previous = self.env
        try:
            self.env = env
            for statement in statements:
                self._exec(statement)
        finally:
            self.env = previous

    def _eval(self, expr: Expr) -> Any:
        return expr.accept(self)