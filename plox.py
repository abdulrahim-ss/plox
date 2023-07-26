#!/bin/python3
import argparse
from typing import List, Optional, Type, Union
# from cmd import Cmd

from plox_token import PloxToken
from Expr import Expr

from scanner import Scanner
from plox_parser import PloxParser

#temp import
from ast_printer import AstPrinter


class PLox:
    def __init__(self, args: List[str]):
        self.args = args
        self.hadError = False

        if len(self.args) > 1:
            print("Usage: plox <script>")
            exit(64)

        elif len(self.args) == 1:
            self.runFile(self.args[0])
            
        else:
            self.runPrompt()

    def runFile(self, path) -> None:
        with open(path, "r") as f:
            lines = f.read()
            f.close()
        self.run(lines)
        if self.hadError: exit(65)

    def runPrompt(self) -> None:
        intro = """\
=================================================================
         § PLOX - The Python 🐍 implementation of LOX §
=================================================================\
"""
        print(intro)
        while True:
            try:
                #line = input(f"[{os.getcwd()}] § ")
                line = input("§ ")
            except EOFError:
                print("\nBye 👋")
                break
            if line == "exit":
                print("Bye 👋")
                break
            self.run(line)
            self.hadError = False

    def run(self, source: str) -> None:
        scanner = Scanner(source, self.error)
        tokens: List[PloxToken] = scanner.scanTokens()

        parser = PloxParser(tokens, self.error)
        expressions: Expr|None = parser.parse()

        if self.hadError: return
        print(AstPrinter().stringify(expressions))

    def error(self, line: int, where: str, message: str, error: Optional[Type[Exception]]=None) -> Union[Type[Exception], None]:
        self.report(line, where, message)
        return error

    def report(self, line: int, where: str, message: str) -> None:
        print(f"line {line} - Error {where}: {message}")
        self.hadError = True


# class PloxCmd(Cmd):
#     prompt = "§ "
#     commands = []
#     def __init__(self)  -> None:
#         intro = """\
# =================================================================
#          § PLOX - The Python 🐍 implementation of LOX §
# =================================================================\
# """
#         print(intro)

#     def default(self, line: str) -> None:
#         return super().default(line)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plox. The Python implementation of the LOX language.")
    parser.add_argument("arguments", type=str, nargs='*')
    args = vars(parser.parse_args())['arguments']
    w = PLox(args)
