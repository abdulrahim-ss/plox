#!/bin/python3
import argparse
from os import get_terminal_size
from typing import List, Type
from cmd import Cmd

from plox_token import PloxToken
from tokenType import TokenType as TT
from Stmt import Stmt

from scanner import Scanner
from plox_parser import PloxParser
from resolver import Resolver
from interpreter import Interpreter

#temp import
# from ast_printer import AstPrinter


class PLox:
    def __init__(self, args: List[str]):
        self.args = args
        self.repl = False

        self.hadError = False
        self.hadRunTimeError = False

        if len(self.args) > 1:
            print("Usage: plox <script>")
            exit(64)

        elif len(self.args) == 1:
            self.interpreter = Interpreter(self.runtime_error)
            self.runFile(self.args[0])
            
        else:
            self.repl = True
            self.interpreter = Interpreter(self.runtime_error, repl=self.repl)
            self.runPrompt()

    def runFile(self, path: str) -> None:
        if path.split('.')[-1].lower() not in ["plox", "lox", "🐍"]:
            print("Extension must be one of the following: \"plox\", \"lox\", or \"🐍\"")
            exit(999)
        with open(path, "r") as f:
            lines = f.read()
            f.close()
        self.run(lines)
        if self.hadError: exit(65)
        if self.hadRunTimeError: exit(70)

    def runPrompt(self) -> None:
        prompt = PloxCmd(self)
        while True:
            try:
                prompt.cmdloop()
            except KeyboardInterrupt:
                prompt.prompt = "§ "
                prompt.current_command = ""
                print("\nEXCEPTION: Interrupted by user")

    def run(self, source: str) -> None:
        try:
            scanner = Scanner(source, self.scanning_error)
            tokens: List[PloxToken] = scanner.scanTokens()

            parser = PloxParser(tokens, self.parsing_error)
            statements: List[Stmt] = parser.parse()

            if self.hadError: return
            resolver = Resolver(self.interpreter, self.resolve_error)
            resolver.resolve(statements)
            if self.hadError: return
            self.interpreter.interpret(statements)

        except KeyboardInterrupt:
            print("\nEXCEPTION: Interrupted by user")
        # print(AstPrinter().stringify(expression))

    ############### ERROR handling #########################
    def runtime_error(self, err: Type[Exception]) -> None:
        if self.repl:
            print(f"RUNTIME ERROR:")
        else:
            print(f"RUNTIME ERROR [at line {err.token.line}]:")
        print("\t", err)
        self.hadRunTimeError = True

    def scanning_error(self, line: int, message: str) -> None:
        self.report(line, "Syntax Error", message)

    def resolve_error(self, token: PloxToken, message: str) -> None:
        self.report(token.line, "Resolution Error", message)

    def parsing_error(self, token: PloxToken, message: str) -> None:
        char = token.lexeme
        if char == "{":
            char = " \"{\" "
        if char == "}":
            char = " \"}\" "
        where = "Syntax Error at the end" if token.type == TT.EOF else f"Syntax Error at {{{char}}}"
        self.report(token.line, where, message)

    def report(self, line: int, where: str, message: str) -> None:
        if self.repl:
            print(f"{where}: {message}")
        else:
            print(f"line {line} - {where}: {message}")
        self.hadError = True


class PloxCmd(Cmd):
    prompt = "§ "
    current_command : str = ""
    count = 0
    def __init__(self, plox) -> None:
        width = get_terminal_size()[0]
        padding = int((width - 45) / 2)
        padding = " " * padding
        l = "\n" + ("=" * width) + "\n"
        title = "§ PLOX - The Python 🐍 implementation of LOX §"
        intro = l + padding + title + padding + l
        self.plox = plox
        print(intro)
        super().__init__()

    def do_help(self, line: str) -> None:
        return self.default(f"help{line}")

    def do_exit(self, arg) -> None:
        """EXIT"""
        print("Bye 👋")
        exit(0)

    def do_EOF(self, arg) -> None:
        """EXIT"""
        print("\nBye 👋")
        exit(0)

    def do_clear(self, arg) -> None:
        """CLEAR SCREEN"""
        print("\033c")

    def emptyline(self) -> None:
        if self.current_command != "":
            self.plox.run(self.current_command)
            self.current_command = ""
            self.prompt = "§ "
            self.plox.hadError = False

    def default(self, line: str) -> None:
        if any([match in line for match in [
                                            "class",
                                            "for",
                                            "while",
                                            "if",
                                            "else",
                                            "fun",
                                            # "{",
                                            # "(",
                                            # "["
                                            ]
                ]): # and not any([match in line for match in [")","}","]"]])
            self.current_command += line
            self.count += 1
            self.prompt = "... "
            return
        if self.current_command != "": # and "}" not in line
            self.current_command += line
            return
        # if self.current_command != "" and "}" in line:
        #     self.count -= 1
        #     if self.count == 0:
        #         self.current_command += line
        #         self.plox.run(self.current_command)
        #         self.current_command = ""
        #         self.plox.hadError = False
        #         self.prompt = "§ "
        #     return
        self.plox.run(line)
        self.plox.hadError = False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plox. The Python implementation of the LOX language.")
    parser.add_argument("arguments", type=str, nargs='*')
    args = vars(parser.parse_args())['arguments']
    w = PLox(args)
