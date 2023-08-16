from __future__ import annotations
from typing import Dict

from error_types import RunTimeError
from unwind_exceptions import *

from tokenType import TokenType as TT
from plox_token import PloxToken
from environment import Environment
from Stmt import *
from Expr import *

class ploxCallable:
    def call(self, interpreter, arguments: list) -> object:
        return NotImplementedError
    
    def arity(self) -> int:
        raise NotImplementedError

class ploxFunction(ploxCallable):
    def __init__(self, name: str, declaration: FuncExpr, closure: Environment, isInitializer: bool = False) -> None:
        self.name = name
        self.declaration = declaration
        self.closure = closure
        self.isInitializer = isInitializer

    def call(self, interpreter, arguments: list) -> object:
        env = Environment(RunTimeError, self.closure)
        for i, param in enumerate(self.declaration.params):
            env.assign(param, arguments[i]["value"])
        try:
            interpreter._exec_block(self.declaration.body, env)
        except ReturnException as r:
            if self.isInitializer:
                return self.closure.fetchAt(0, PloxToken(TT.THIS, "this", None, 0))
            return r.value
        if self.isInitializer:
            return self.closure.fetchAt(0, PloxToken(TT.THIS, "this", None, 0))
        return None
    
    def arity(self) -> int:
        return len(self.declaration.params)
    
    def bind(self, instance: ploxInstance, name: PloxToken, callback: callable) -> ploxFunction:
        env = Environment(RunTimeError, self.closure)
        env.assign(PloxToken(TT.THIS, "this", None, name.line), instance)
        bound_method = ploxFunction(self.name, self.declaration, env, self.isInitializer)
        bound_method.to_str = callback
        return bound_method
    
    def to_str(self) -> str:
        if self.name:
            if self.declaration.type == "function":
                return f"<fun {self.name}>"
            elif self.declaration.type == "method":
                return f"<method {self.name}>"
        else:
            return "<anonymous fun>"

    # def __str__(self) -> str:
    #     return self.to_str()

    def __repr__(self) -> str:
        return self.to_str()


class ploxClass(ploxCallable):
    def __init__(self, name: str, methods: Dict[str, ploxFunction]) -> None:
        self.name = name
        self.methods = methods

    def call(self, interpreter, arguments: list) -> object:
        instance = ploxInstance(self)
        initializer = self.find_method("init")
        if initializer:
            initializer.bind(instance,
                             PloxToken(TT.IDENTIFIER, initializer.name, "init", 0),
                             self.init_print
                             ).call(interpreter, arguments)
        return instance

    def init_print(self):
            return f"<initializer method of {self.name}>"

    def arity(self) -> int:
        initializer = self.find_method("init")
        if not initializer:
            return 0
        return initializer.arity()
    
    def find_method(self, name: str) -> ploxFunction | None:
        method = self.methods.get(name)
        if method:
            method.to_str = self.method_print(method)
        return method

    def method_print(self, method: ploxFunction) -> callable:
        def wrapper():
            return f"<method {method.name} member of {self.name}>"
        return wrapper

    def __str__(self) -> str:
        return f"<class {self.name}>"
    
    def __repr__(self) -> str:
        return self.__str__()


class ploxInstance:
    def __init__(self, klass: ploxClass) -> None:
        self.klass = klass
        self.fields = dict()

    def get(self, name: PloxToken) -> object:
        if name.lexeme in self.fields.keys():
            return self.fields.get(name.lexeme)

        method = self.klass.find_method(name.lexeme)
        if method:
            callback = self.klass.init_print if name.lexeme =="init" else self.klass.method_print(method)
            return method.bind(self, name, callback)

        raise RunTimeError(name, f"Undefined property {{{name.lexeme}}}")

    def set(self, name: PloxToken, value: object) -> None:
        self.fields[name.lexeme] = value

    def __str__(self) -> str:
        return f"<{self.klass.name} instance>"
    
    def __repr__(self) -> str:
        return self.__str__()
