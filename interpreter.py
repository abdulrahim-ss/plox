from typing import List, Dict, Any, Callable, Type
from error_types import RunTimeError

from Expr import *
from Expr import Assign
from Stmt import *
from Stmt import Expression, Var
from plox_token import PloxToken
from tokenType import TokenType as TT
from plox_callable import *
from unwind_exceptions import *
from natives import *
from environment import Environment


class Interpreter(ExprVisitor, StmtVisitor):
    #TODO: get the comma operator to work
    def __init__(self, error: Callable[[Type[Exception]], None], repl: bool = False):
        self.error = error
        self.repl = repl
        self.print_flag = False
        self.globals = Environment(RunTimeError) # Global scope objects reside on line -9
        self.locals : Dict[Expr, int] = dict()
        self.env = self.globals
        self.natives()

    def natives(self) -> None:
        self.globals.assign(PloxToken(TT.IDENTIFIER, "clock", None, -9), Clock())
        self.globals.assign(PloxToken(TT.IDENTIFIER, "sleep", None, -9), Sleep())
        self.globals.assign(PloxToken(TT.IDENTIFIER, "struct", None, -9), Struct())
        self.globals.assign(PloxToken(TT.IDENTIFIER, "input", None, -9), Input())
        self.globals.assign(PloxToken(TT.IDENTIFIER, "help", None, -9), Help())

    def interpret(self, statements: List[Stmt]) -> None:
        try:
            for statement in statements:
                self.print_flag = False
                self._exec(statement)
        except RunTimeError as err:
            self.error(err)
        except NotImplementedError as err:
            print("Not yet implemented")

    def visitEmpty(self, stmt: Empty) -> None:
        return

    def visitBlock(self, stmt: Block) -> None:
        self._exec_block(stmt.statements, Environment(RunTimeError, self.env))

    def visitExpression(self, stmt: Expression) -> None:
        value = self._eval(stmt.expression)
        if self.repl and not self.print_flag:
            value = self._stringify(value)
            print(value)

    def visitIf(self, stmt: If) -> None:
        if self._isTruthy(self._eval(stmt.condition)):
            self._exec(stmt.thenBranch)
        elif stmt.elseBranch:
            self._exec(stmt.elseBranch)

    def visitWhile(self, stmt: While) -> None:
        while self._isTruthy(self._eval(stmt.condition)):
            try:
                self._exec(stmt.body)
            except BreakException:
                break
            except ContinueException:
                self._exec_block([stmt.body.statements[-1]], Environment(RunTimeError, self.env))
                continue

    def visitBreak(self, stmt: Break) -> None:
        raise BreakException

    def visitContinue(self, stmt: Continue) -> None:
        raise ContinueException

    def visitPrint(self, stmt: Print) -> None:
        self.print_flag = True
        value = self._eval(stmt.expression)
        print(self._stringify(value))

    def visitVar(self, stmt: Var) -> None:
        value = None
        if stmt.Initializer is not None:
            value = self._eval(stmt.Initializer)
        self.env.assign(stmt.name, value)

    def visitClassStmt(self, stmt: ClassStmt) -> None:
        parentclass = None
        if stmt.parentclass:
            parentclass = self._eval(stmt.parentclass)
            if not isinstance(parentclass, ploxClass):
                raise RunTimeError(stmt.parentclass.name, "A parent class must be a class")
        self.env.assign(stmt.name, None)
        if stmt.parentclass:
            self.env = Environment(RunTimeError, self.env)
            self.env.assign(PloxToken(TT.PARENT, "parent", None, stmt.name.line), parentclass)
        methods : Dict[str, ploxFunction] = dict()
        for method in stmt.methods:
            name = method.name.lexeme
            func = ploxFunction(name, method.function, self.env, name == "init")
            methods[name] = func
        klass = ploxClass(stmt.name.lexeme, parentclass, methods)
        if parentclass:
            self.env = self.env.enclosing
        self.env.assign_existing(stmt.name, klass)

    def visitFunction(self, stmt: Function) -> None:
        name = stmt.name
        func = ploxFunction(name.lexeme, stmt.function, self.env)
        self.env.assign(name, func)

    def visitReturn(self, stmt: Return) -> None:
        value = None
        if stmt.value:
            value = self._eval(stmt.value)
        raise ReturnException(value)

    def visitFuncExpr(self, expr: FuncExpr) -> object:
        return ploxFunction(None, expr, self.env)

    def visitAssign(self, expr: Assign) -> object:
        value = self._eval(expr.value)
        distance = self.locals.get(expr)
        if distance:
            self.env.assignAt(distance, expr.name, value)
        else:
            self.globals.assign_existing(expr.name, value)
        return value

    def visitLiteral(self, expr: Literal) -> object:
        return expr.value

    def visitListExpr(self, expr: ListExpr) -> object:
        vals = []
        for value in expr.values:
            vals.append(self._eval(value))
        return vals

    def visitVariable(self, expr: Variable) -> object:
        value = self.look_up_var(expr.name, expr)
        return value
        # if value:
        #     return value
        # raise RunTimeError(expr.name, f"Variable {{{expr.name.lexeme}}} must be initialized in order to be accessed")

    def look_up_var(self, name: PloxToken, expr: Expr) -> object:
        distance = self.locals.get(expr)
        if distance:
            return self.env.fetchAt(distance, name)
        return self.globals.fetch(name)

    def visitLogical(self, expr: Logical) -> object:
        left = self._eval(expr.left)
        if expr.operator.type == TT.OR:
            if self._isTruthy(left): return left
        elif expr.operator.type == TT.AND:
            if not self._isTruthy(left):
                return left
        return self._eval(expr.right)

    def visitGrouping(self, expr: Grouping) -> object:
        return self._eval(expr.expression)

    def visitUnary(self, expr: Unary) -> object:
        right = self._eval(expr.right)

        match expr.operator.type:
            case TT.MINUS:
                self._check_number(expr.operator, right)
                return - right
            case TT.BANG:
                return not self._isTruthy(right)
            
    def visitBinary(self, expr: Binary) -> object:
        left = self._eval(expr.left)
        right = self._eval(expr.right)

        match expr.operator.type:
            # Arithmatic -------------------------------------------
            case TT.MINUS:
                self._check_number(expr.operator, left, right)
                return left - right
            case TT.SLASH:
                self._check_number(expr.operator, left, right)
                try:
                    return left / right
                except ZeroDivisionError:
                    raise RunTimeError(expr.operator, "Tried dividing by zero")
            case TT.STAR:
                self._check_number(expr.operator, left, right)
                return left * right
            case TT.PLUS:
                if isinstance(left, str) or isinstance(right, str):
                    return self._stringify(left) + self._stringify(right)
                else:
                    return self._numify(left) + self._numify(right)
            # Comparison -------------------------------------------
            case TT.GREATER:
                # self._check_number(expr.operator, left, right)
                return self._numify(left) > self._numify(right)
            case TT.GREATER_EQUAL:
                # self._check_number(expr.operator, left, right)
                return self._numify(left) >= self._numify(right)
            case TT.LESS:
                # self._check_number(expr.operator, left, right)
                return self._numify(left) < self._numify(right)
            case TT.LESS_EQUAL:
                # self._check_number(expr.operator, left, right)
                return self._numify(left) <= self._numify(right)
            # Comaprison - equality --------------------------------
            case TT.EQUAL_EQUAL:
                return left == right
            case TT.BANG_EQUAL:
                return not (left == right)

    def visitCall(self, expr: Call) -> object:
        callee : ploxCallable = self._eval(expr.callee)

        args = []
        for arg in expr.arguments:
            args.append({"expr": arg, "value": self._eval(arg)})
        if not isinstance(callee, ploxCallable):
            raise RunTimeError(expr.paren, "Tried to call non-callable object")

        if len(args) != callee.arity():
            raise RunTimeError(expr.paren,f"Expected {callee.arity()} arguments, but got {len(args)}")

        return callee.call(self, args)

    def visitSubscriptable(self, expr: Subscriptable) -> object:
        subscribee = self._eval(expr.subscribee)
        if not isinstance(subscribee, list) and not isinstance(subscribee, str):
            raise RunTimeError(expr.subscribee, "Only subscriptable objects currently available are lists and strings")
        index = self._eval(expr.index)
        try:
            index = int(index)
        except:
            raise RunTimeError(expr.index, "Index must be a number. Other types of indexing not yet implemented")
        if index > len(subscribee):
            raise RunTimeError(expr.index, f"Index {{{index}}} is out of range")
        return subscribee[index]

    def visitGet(self, expr: Get) -> object:
        obj = self._eval(expr.obj)
        if isinstance(obj, ploxInstance):
            return obj.get(expr.name)

        raise RunTimeError(expr.name, "Only instances have properties")

    def visitSet(self, expr: Set) -> object:
        obj = self._eval(expr.obj)
        if not isinstance(obj, ploxInstance):
            raise RunTimeError(expr.name, "Only instances have fields")

        value = self._eval(expr.value)
        obj.set(expr.name, value)
        return value

    def visitThis(self, expr: This) -> object:
        return self.look_up_var(expr.keyword, expr)

    def visitParent(self, expr: Parent) -> object:
        distance = self.locals.get(expr)
        superclass : ploxClass = self.env.fetchAt(distance, expr.keyword)
        obj : ploxInstance = self.env.fetchAt(distance - 1, PloxToken(TT.THIS, "this", None, expr.keyword.line))
        method = superclass.find_method(expr.method.lexeme)
        if method is None:
            raise RunTimeError(expr.method, f"Undefined property {{{expr.method.lexeme}}}")
        return method.bind(obj)

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
        # if value is None: return -1
        if isinstance(value, str): return int.from_bytes(value.encode(), "big", signed=False)
        return float(value)

    @staticmethod
    def _stringify(value: object) -> str:
        if value is None:
            return "nil"
        if str(value).endswith(".0"): return str(value).split(".")[0]
        if value is True: return "true"
        if value is False: return "false"
        if isinstance(value, list):
            lista = "["
            for val in value:
                lista += Interpreter._stringify(val) + ", "
            lista = lista[:-2] + "]"
            return lista
        if isinstance(value, str):
            string = value.encode("utf-8").decode("unicode_escape")
            string = string.encode('utf-16').decode('utf-16')
            return string
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
    def _check_number(operator: Expr, *operands: object) -> None:
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

    def _resolve(self, expr: Expr, depth: int) -> None:
        self.locals[expr] = depth

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