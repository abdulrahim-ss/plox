#!/bin/python3
import argparse, os
from typing import List
from cmd import Cmd

from scanner import Scanner
from token import Token


class Lox:
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
        tokens: List[Token] = scanner.scanTokens()
 
        for token in tokens:
            print(token)

    def error(self, line: int, message: str) -> None:
        self.report(line, "", message)

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
    w = Lox(args)
