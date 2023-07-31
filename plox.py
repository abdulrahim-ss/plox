#!/bin/python3
import argparse
from typing import List, Type
from cmd import Cmd

from plox_token import PloxToken
from tokenType import TokenType as TT
from Expr import Expr
from Stmt import Stmt

from scanner import Scanner
from plox_parser import PloxParser
from interpreter import Interpreter

#temp import
# from ast_printer import AstPrinter


class PLox:
    def __init__(self, args: List[str]):
        self.args = args

        self.hadError = False
        self.hadRunTimeError = False

        if len(self.args) > 1:
            print("Usage: plox <script>")
            exit(64)

        elif len(self.args) == 1:
            self.interpreter = Interpreter(self.runtime_error)
            self.runFile(self.args[0])
            
        else:
            self.interpreter = Interpreter(self.runtime_error, repl=True)
            self.runPrompt()

    def runFile(self, path) -> None:
        with open(path, "r") as f:
            lines = f.read()
            f.close()
        self.run(lines)
        if self.hadError: exit(65)
        if self.hadRunTimeError: exit(70)

    def runPrompt(self) -> None:
        prompt = PloxCmd(self)
        prompt.cmdloop()
    #     intro = """\
    # =================================================================
    #         § PLOX - The Python 🐍 implementation of LOX §
    # =================================================================\
    # """
    #     print(intro)
    #     while True:
    #         try:
    #             #line = input(f"[{os.getcwd()}] § ")
    #             line = input("§ ")
    #         except EOFError:
    #             print("\nBye 👋")
    #             break
    #         if line == "exit":
    #             print("Bye 👋")
    #             break
    #         self.run(line)
    #         self.hadError = False

    def run(self, source: str) -> None:
        scanner = Scanner(source, self.scanning_error)
        tokens: List[PloxToken] = scanner.scanTokens()

        parser = PloxParser(tokens, self.parsing_error)
        statements: List[Stmt] = parser.parse()

        if self.hadError: return
        self.interpreter.interpret(statements)
        # print(AstPrinter().stringify(expression))

    ############### ERROR handling #########################
    def runtime_error(self, err: Type[Exception]) -> None:
        print(f"RUNTIME ERROR [at line {err.token.line}]:")
        print("\t", err)
        self.hadRunTimeError = True

    def scanning_error(self, line: int, message: str) -> None:
        self.report(line, "", message)

    def parsing_error(self, token: PloxToken, message: str) -> None:
        where = "at the end" if token.type == TT.EOF else f"at \"{token.lexeme}\""
        self.report(token.line, where, message)

    def report(self, line: int, where: str, message: str) -> None:
        print(f"line {line} - Error {where}: {message}")
        self.hadError = True


class PloxCmd(Cmd):
    prompt = "§ "
    def __init__(self, plox) -> None:
        intro = """\
=================================================================
         § PLOX - The Python 🐍 implementation of LOX §
=================================================================\
"""
        self.plox = plox
        print(intro)
        super().__init__()

    def do_exit(self, arg) -> None:
        """EXIT"""
        print("Bye 👋")
        exit(0)

    def do_EOF(self, arg) -> None:
        """EXIT"""
        print("\nBye 👋")
        exit(0)

    def default(self, line: str) -> None:
        self.plox.run(line)
        self.plox.hadError = False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plox. The Python implementation of the LOX language.")
    parser.add_argument("arguments", type=str, nargs='*')
    args = vars(parser.parse_args())['arguments']
    w = PLox(args)
