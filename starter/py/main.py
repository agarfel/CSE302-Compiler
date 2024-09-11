#! /usr/bin/env python3

#--------- Main ---------#
import sys
from bxparser import Parser
from bxlexer import Lexer


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
        lexer = Lexer()
        parser = Parser()
        parser.parser.parse(content, lexer=lexer.lexer)