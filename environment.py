from __future__ import annotations
from typing import Type

from plox_token import PloxToken

class Environment:
    def __init__(self, raisable: Type[Exception], enclosing = None):
        self.raisable = raisable
        self.values = dict()
        self.enclosing: Environment = enclosing

    def assign(self, name: PloxToken, value: object) -> None:
        self.values[name.lexeme] = value

    def assign_existing(self, token: PloxToken, value: object) -> None:
        name = token.lexeme
        if name in self.values.keys():
            self.values[name] = value
            return
        if self.enclosing is not None:
            self.enclosing.assign_existing(token, value)
            return
        raise self.raisable(token, f"Undefined variable {{{name}}}")

    def assignAt(self, distance: int, token: PloxToken, value: object) -> None:
        name = token.lexeme
        self.ancestor(distance).values[name] = value
    
    def fetch(self, token: PloxToken) -> object:
        name = token.lexeme
        if name in self.values.keys():
            return self.values.get(name)
        if self.enclosing is not None:
            return self.enclosing.fetch(token)

        raise self.raisable(token, f"Undefined variable {{{name}}}")

    def fetchAt(self, distance: int, token: PloxToken) -> object:
        name = token.lexeme
        return self.ancestor(distance).values[name]
    
    def ancestor(self, distance: int) -> Environment:
        env = self
        for _ in range(distance - 1):
            print(_, distance)
            env = env.enclosing
        print(env.values)
        return env
