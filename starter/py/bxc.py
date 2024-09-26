#! /usr/bin/env python3

#--------- Main ---------#
import sys
import json

from bxparser import Parser
from bxlexer import Lexer
from bxerrors import Reporter
from bxast import *
from bxsyntaxchecker import *
from bxtac import *
from bxtypechecker import *


def read_file_to_string(file_path):
    try:
        with open(file_path, 'r') as file:
            file_content = file.read()
        return file_content
    except FileNotFoundError:
        return f"Error: The file '{file_path}' does not exist."


def run_compiler(reporter, content, debug=False):
    lexer = Lexer(reporter)
    parser = Parser(reporter)
    ast = parser.parser.parse(content, lexer=lexer.lexer)
    if ast is None:
        if debug: print("Error: Parsing returned None.")
        return
    if debug: print('Parsing successfull')
    syntax_checker = SyntaxChecker(reporter=reporter)
    syntax_checker.for_program(ast)
    if debug: print('Syntax Check successfull')

    type_checker = TypeChecker(reporter=reporter)
    type_checker.for_block(ast)
    if debug: print('Type Check successfull')

    if debug: 
        print(ast)

    totac = ToTac(reporter)
    totac.processBlock(ast)
    data = totac.getData()
    with open('source.tac.json', 'w') as f:
        json.dump(data, f)
    


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: ./myprogram.py <filename>")
    else:
        file_path = sys.argv[1]
        content = read_file_to_string(file_path)
        if content.startswith("Error:"):
            print(content)
        else:
            reporter = Reporter()
            reporter.filename = file_path
            run_compiler(reporter, content, False)
            reporter.describe()
