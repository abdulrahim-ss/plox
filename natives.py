from time import time, sleep
from typing import Generator

from plox_callable import *
from error_types import RunTimeError


class Native(ploxCallable):
    def help(self) -> str:
        raise NotImplementedError


class Clock(Native):
    def arity(self) -> int:
        return 0

    def call(self, interpreter, args: list) -> float:
        return time()
    
    def __repr__(self) -> str:
        return "<native fun>"


class Help(Native):
    def arity(self) -> int:
        return 1

    def call(self, interpreter, args: list) -> str:
        try:
            return args[0]["value"].help()
        except NotImplementedError:
            return "self-explanatory"

    def help(self) -> str:
        content = """Me: How much more help do you want me to help?\
                    \nYou: MORE help.\
                    \nMe: But... But I have given you all the help I could!\
                    \nYou: But are you the same animal, and a different beast?\
                    \nMe: WTF does that mean Kobe Bryant?!!!"""
        return content

    def __repr__(self) -> str:
        return "<native fun>"


class Input(Native):
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


class Sleep(Native):
    def arity(self) -> int:
        return 1

    def call(self, interpreter, args: list) -> None:
        inp = args[0]["value"]
        if not isinstance(inp, float) and inp >= 0:
            raise RunTimeError(None,"argument must be a positive number")
        sleep(inp)

    def __repr__(self) -> str:
        return "<native fun>"


class Struct(Native):
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
        elif isinstance(callable, ploxInstance):
            try:
                inp = args[0]["expr"].name.lexeme
            except:
                inp = "EXPRESSION"
            return "\n".join(self._struct_instance(inp, callable))
        else:
            raise NotImplementedError
    
    def __repr__(self) -> str:
        return "<native fun>"
 
    def _struct_class(self, name: str, callable: ploxClass) -> Generator[str, None, None]:
        yield "--------------------------"
        yield f"INPUT {{{name}}}:"
        yield "   Type: class"
        yield f"   Name: {callable.name}"
        if callable.parentclass:
            yield f"   Parent: {callable.parentclass.name}"
        if callable.methods:
            yield from self._member_methods_finder(callable)
        yield "--------------------------"

    def _struct_instance(self, name: str, callable: ploxInstance) -> Generator[str, None, None]:
        yield "--------------------------"
        yield f"INPUT {{{name}}}:"
        yield "   Type: instance"
        yield f"   class: {callable.klass.name}"
        yield "   Fields:"
        if callable.fields:
            for field, value in callable.fields.items():
                yield f"      - field[{field}]:   ({value})"
        else:
            yield "      NONE"
        yield "   Member Methods of class (including parents/ancestors):"
        yield "   *********************  "
        if callable.klass.methods or callable.klass.parentclass.methods:
            yield from self._member_methods_finder(callable.klass, instance=True)
        else:
            yield "      NONE"
        yield "--------------------------"

    def _member_methods_finder(self, klass: ploxClass,
                               parent: bool = False,
                               instance: bool = False) -> Generator[str, None, None]:
        if klass.parentclass:
            if not parent and not instance: 
                yield "   *********************  "
            yield from self._member_methods_finder(klass.parentclass, True, instance)
        if not instance:
            if parent:
                yield "   Member Methods (of parent/ancestor):"
                yield f"    ? which parent/ancestor: {klass.name}"
            else:
                yield "   Own Member Methods:"
        for method_name, method in klass.methods.items():
            yield from self._struct_func(f"* {{{method_name}}}", method, "method")
            yield " "
        yield "   *********************  "

    @staticmethod
    def _struct_func(name: str, callable: ploxFunction, type: str) -> Generator[str, None, None]:
        indent = "      " if type == "method" else ""
        if type == "function":
            yield indent + "--------------------------" 
            yield indent + f"INPUT {{{name}}}:"
        else:
            yield "   " + f"   {name}:"
        if callable.name:
            yield indent + f"   Name: {callable.name}"
            yield indent + f"   Type: {type}"
        else:
            yield indent + "   Type: anonymous function"
        yield indent + "   Parameters:"
        if not callable.declaration.params:
            yield indent + "      NONE"
        for i, param in enumerate(callable.declaration.params):
            yield indent + f"      - param[{i}]:   ({param.lexeme})"
        # yield "   Returns:"
        # explicit_return = False
        # for i, stmt in enumerate(callable.declaration.body):
        #     if isinstance(stmt, Return):
        #         explicit_return = True
        #         yield f"      - return[{i}]:   ({interpreter._eval(stmt.value)})"
        # if not explicit_return:
        #     yield "      returns nil"
        if type == "function":
            finish_line = "--------------------------" 
            yield finish_line

    def help(self) -> str:
        content = """Native function {struct}\
                     \nPrints the structure of a PLOX object\
                     \nA line of stars indicates that the fields/methods \
                     \nbelong to another inherited-from object."""
        return content
