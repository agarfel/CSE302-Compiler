#! /usr/bin/env python3

#--------- Main ---------#
import sys
import json

from bxparser import Parser
from bxlexer import Lexer
from bxerrors import Reporter
from bxast import *
from bxsynchecker import *
from bxasttac import *




def read_file_to_string(file_path):
    try:
        with open(file_path, 'r') as file:
            file_content = file.read()
        return file_content
    except FileNotFoundError:
        return f"Error: The file '{file_path}' does not exist."


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: ./myprogram.py <filename>")
    else:
        file_path = sys.argv[1]
        content = read_file_to_string(file_path)
        reporter = Reporter()
        reporter.filename = file_path
        lexer = Lexer(reporter)
        parser = Parser(reporter)
        ast = (parser.parser.parse(content, lexer=lexer.lexer))
        checker = SynChecker(reporter=reporter)
        checker.for_program(ast)
        totac = ToTac(reporter)
        totac.processProgram(ast)
        data = totac.getData()
        with open('source.tac.json', 'w') as f:
            json.dump(data, f)
        reporter.describe()