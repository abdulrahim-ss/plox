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
        if isinstance(callable, ploxFunction):
            try:
                inp = args[0]["expr"].name.lexeme
            except:
                inp = "EXPRESSION"
            return "\n".join(self._struct_func(inp, callable, "function"))

        elif isinstance(callable, ploxClass):
            try:
                inp = args[0]["expr"].name.lexeme
            except:
                inp = "EXPRESSION"
            return "\n".join(self._struct_class(inp, callable))
        else:
            raise NotImplementedError
    
    def __repr__(self) -> str:
        return "<native fun>"
 
    def _struct_class(self, name, callable):
        yield "--------------------------"
        yield f"INPUT {{{name}}}:"
        yield f"   Type: class"
        yield f"   Name: {callable.name}"
        if callable.parentclass:
            yield f"   Parent: {callable.parentclass}"
        for method in callable.methods:
            print(method)
            self._struct_func("Member method", method, "method")
        yield "--------------------------"

    @staticmethod
    def _struct_func(name, callable, type):
        if type == "function":
            yield "--------------------------" 
            yield f"INPUT {{{name}}}:"
        else:
            yield "  *********************  "
            yield f"   {name}:"
        if callable.name:
            yield f"   Type: {type}"
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
        finish_line = "--------------------------" if type == "function" else "  *********************  "
        yield finish_line