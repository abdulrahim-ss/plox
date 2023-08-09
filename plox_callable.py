from error_types import RunTimeError

from plox_token import PloxToken
from environment import Environment
from Stmt import *
from Expr import *
from unwind_exceptions import *

class ploxCallable:
    def call(self, interpreter, arguments: list) -> object:
        return NotImplementedError
    
    def arity(self) -> int:
        raise NotImplementedError

class ploxFunction(ploxCallable):
    def __init__(self, name: str, declaration: FuncExpr, closure: Environment) -> None:
        self.name = name
        self.declaration = declaration
        self.closure = closure

    def call(self, interpreter, arguments: list) -> object:
        env = Environment(RunTimeError, self.closure)
        for i, param in enumerate(self.declaration.params):
            env.assign(param, arguments[i]["value"])
        try:
            interpreter._exec_block(self.declaration.body, env)
        except ReturnException as r:
            return r.value
        return None
    
    def arity(self) -> int:
        return len(self.declaration.params)
    
    def __str__(self) -> str:
        if self.name:
            return f"<fun {self.name}>"
        else:
            return "<anonymous fun>"

    def __repr__(self) -> str:
        return self.__str__()
