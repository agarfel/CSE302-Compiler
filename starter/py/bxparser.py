#! /usr/bin/env python3

import ply.lex as lex
import ply.yacc as yacc

#--------- Lexer ---------#

reserved = {'print': 'PRINT',
            'def': 'DEF',
            'main': 'MAIN',
            'int': 'INT',
            'var': 'VAR'
            }

tokens = (
  'IDENT',
  'NUMBER',
  'PLUS',
  'MINUS',
  'STAR',
  'SLASH',
  'EQUAL',
  'LPAREN',
  'RPAREN',
  'LCPAREN',
  'RCPAREN',
  'LSHIFT',
  'RSHIFT',
  'MOD',
  'AND',
  'OR',
  'XOR',
  'SEMICOLON',
  'COLON',
  'COMPLEMENT',
) + tuple(reserved.values())

t_PLUS = r'\+'
t_MINUS = r'-'
t_STAR = r'\*'
t_SLASH = r'/'
t_EQUAL = r'\='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LCPAREN = r'\{'
t_RCPAREN = r'\}'
t_LSHIFT = r'<<'
t_RSHIFT = r'>>'
t_MOD = r'%'
t_AND = r'\&'
t_OR = r'\|'
t_XOR = r'\^'
t_SEMICOLON = r'\;'
t_COLON = r':'
t_COMPLEMENT = r'~'

t_ignore = ' \t\f\v'

def t_IDENT(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'IDENT')
    return t


def t_NUMBER(t):
    r'0|[1-9][0-9]*'
    t.value = int(t.value)
    return t

def t_comment(t):
    r'//.*\n'
    t.lexer.lineno += 1

def t_newline(t):
    r'\n'
    t.lexer.lineno += 1

def t_error(t):
    print(f"Illegal character '{t.value[0]}' on line {t.lexer.lineno}")
    t.lexer.skip(1)



lexer = lex.lex()

"""
-----    TEST    -----

lexer.input('print(x + y);') 
print(lexer.token())
print(lexer.token())
t = lexer.token()
print(t.type, t.value, t.lineno, t.lexpos)
"""

#--------- Parser ---------#

precedence = (
    ('left', 'OR'),
    ('left', 'XOR'),
    ('left', 'AND'),
    ('left', 'LSHIFT','RSHIFT'),
    ('left', 'PLUS','MINUS'),
    ('left', 'STAR','SLASH','MOD'),
    ('nonassoc', 'NEGATION'),
    ('nonassoc', 'COMPLEMENT')
)

# dictionary of names
names = { }
def p_program(p):
    """program : DEF MAIN LPAREN RPAREN LCPAREN stmt RCPAREN"""

def p_stmt(p):
    """stmt : vardecl
        | assign
        | print 
        | stmt stmt
        | """

def p_vardecl(p):
    """vardecl : VAR IDENT EQUAL expr COLON INT SEMICOLON"""

def p_assign(p):
    """assign : IDENT EQUAL expr SEMICOLON"""

def p_print(p):
    """print : PRINT LPAREN expr RPAREN SEMICOLON"""

def p_expr_ident(p):
    """expr : IDENT"""

def p_expr_number(p):
    """expr : NUMBER"""

def p_expr_binop(p):
    """expr : expr PLUS expr
    | expr MINUS expr
    | expr STAR expr
    | expr SLASH expr
    | expr MOD expr
    | expr AND expr
    | expr OR expr
    | expr XOR expr
    | expr LSHIFT expr
    | expr RSHIFT expr"""



def p_expression_negation(t):
    """expr : MINUS expr %prec NEGATION"""

def p_expr_complement(p):
    """expr : COMPLEMENT expr"""

def p_expr_parens(p):
    """expr : LPAREN expr RPAREN
            | LCPAREN expr RCPAREN"""

def p_expr_single(p):
    """expr : COLON
            | SEMICOLON
            | EQUAL """
    
def p_expr_keywords(p):
    """expr : DEF
            | MAIN
            | PRINT
            | INT """


def p_error(t):
    print("Syntax error at '%s'" % t.value)

parser = yacc.yacc()

#--------- Main ---------#
import sys

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
        parser.parse(content, lexer=lexer)
