#! /usr/bin/env python3

#--------- Main ---------#
import sys
import json

from bxlib.bxparser import Parser
from bxlib.bxlexer import Lexer
from bxlib.bxerrors import Reporter
from bxlib.bxast import *
# from bxlib.bxsyntaxchecker import *
from bxlib.bxtac import *
from bxlib.bxtypechecker import *
from bxlib.bx64 import *
from bxlib.bxcfg import *


def read_file_to_string(file_path):
    try:
        with open(file_path, 'r') as file:
            file_content = file.read()
        return file_content
    except FileNotFoundError:
        return f"Error: The file '{file_path}' does not exist."


def run_compiler(reporter, content, basename, debug=False):
    lexer = Lexer(reporter)
    parser = Parser(reporter)

    reporter.stage = 'Parsing'
    ast = parser.parser.parse(content, lexer=lexer.lexer)
    if reporter.error_number != 0:
        return
    if ast is None:
        if debug: print("Error: Parsing returned None.")
        return
    if debug: print('Parsing successfull')

    # reporter.stage = 'Syntax Check'
    # syntax_checker = SyntaxChecker(reporter=reporter)
    # syntax_checker.for_program(ast)
    # if reporter.error_number != 0:
    #     return
    # if debug: print('Syntax Check successfull')

    reporter.stage = 'Type Check'
    type_checker = TypeChecker(reporter=reporter)
    type_checker.for_program(ast)
    if reporter.error_number != 0:
        return
    if debug: print('Type Check successfull')
    if debug: 
        print(ast)

    reporter.stage = "Transforming AST to TAC"
    totac = ToTac(type_checker.functions, reporter)
    totac.processProgram(ast)
    if reporter.error_number != 0:
        return
    data = totac.getData()
    with open(f'{basename}.tac.json', 'w') as f:
        json.dump(data, f)

    # reporter.stage = "CFG"
    # cfg = CFG(reporter)
    # data = cfg.run(data)
    
    # with open(f'{basename}.opt.tac.json', 'w') as f:
    #     json.dump(data, f)

    reporter.stage = "TAC to x64"
    tox64 = Tox64(reporter)
    tox64.compile_tac(f'{basename}.tac.json')
    


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: ./myprogram.py <filename>")
    else:
        file_path = sys.argv[1]
        content = read_file_to_string(file_path)
        if content.startswith("Error:"):
            print(content)
        else:
            source = file_path[:-3]
            reporter = Reporter()
            reporter.filename = file_path
            run_compiler(reporter, content, source, False)
            reporter.describe()
