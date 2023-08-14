from time import time, sleep

from plox_callable import *
from error_types import RunTimeError

class Clock(ploxCallable):
    def arity(self) -> int:
        return 0

    def call(self, interpreter, args: list) -> float:
        return time()
    
    def __repr__(self) -> str:
        return "<native fun>"


class Input(ploxCallable):
    def arity(self) -> int:
        return 1

    def call(self, interpreter, args: list) -> str:
        output = bytes(args[0]["value"], "utf-8").decode("unicode_escape")
        if not isinstance(output, str):
            raise RunTimeError(None, "argument must be a string")
        result = input("{output}>")
        return result
    
    def __repr__(self) -> str:
        return "<native fun>"


class Sleep(ploxCallable):
    def arity(self) -> int:
        return 1

    def call(self, interpreter, args: list) -> None:
        inp = args[0]["value"]
        if not isinstance(inp, float) and inp >= 0:
            raise RunTimeError(None,"argument must be a positive number")
        sleep(inp)

    def __repr__(self) -> str:
        return "<native fun>"


class Struct(ploxCallable):
    def arity(self) -> int:
        return 1
    
    def call(self, interpreter, args:list) -> str:
        callable = args[0]["value"]
        if not isinstance(callable, ploxFunction):
            return "not implemented"
        try:
            inp = args[0]["expr"].name.lexeme
        except:
            inp = "EXPRESSION"
        return "\n".join(self._struct(inp, callable, interpreter))
    
    def __repr__(self) -> str:
        return "<native fun>"
 
    @staticmethod
    def _struct(name, callable, interpreter):
        yield "--------------------------"
        yield f"INPUT {{{name}}}:"
        if callable.name:
            yield "   Type: function"
            yield f"   Name: {callable.name}"
        else:
            yield "   Type: anonymous function"
        yield "   Parameters:"
        if not callable.declaration.params:
            yield "      NONE"
        for i, param in enumerate(callable.declaration.params):
            yield f"      - param[{i}]:   ({param.lexeme})"
        # yield "   Returns:"
        # explicit_return = False
        # for i, stmt in enumerate(callable.declaration.body):
        #     if isinstance(stmt, Return):
        #         explicit_return = True
        #         yield f"      - return[{i}]:   ({interpreter._eval(stmt.value)})"
        # if not explicit_return:
        #     yield "      returns nil"
        yield "--------------------------"