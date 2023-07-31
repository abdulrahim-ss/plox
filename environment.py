from typing import Type

from plox_token import PloxToken

class Environment:
    def __init__(self, raisable: Type[Exception]):
        self.raisable = raisable
        self.values = dict()

    def assign(self, name: str, value: object) -> None:
        self.values[name] = value

    def assign_existing(self, name: str, value: object) -> None:
        if self.values.get(name):
            self.values[name] = value
        else:
            raise self.raisable(name, f"Undefined variable \"{name}\".")

    def fetch(self, token: PloxToken) -> object:
        name = token.lexeme
        value = self.values.get(name)
        if value:
            return value
        raise self.raisable(name, f"Undefined variable \"{name}\".")
