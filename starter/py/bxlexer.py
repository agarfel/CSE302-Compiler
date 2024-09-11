#! /usr/bin/env python3

import ply.lex as lex


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
t_ignore_comments =  r'//.*'


def t_IDENT(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'IDENT')
    return t

def t_NUMBER(t):
    r'0|[1-9][0-9]*'
    t.value = int(t.value)
    return t

def t_newline(t):
    r'\n'
    t.lexer.lineno += 1


def t_error(t):
    print(f"Illegal character '{t.value[0]}' on line {t.lexer.lineno}")
    t.lexer.skip(1)


class Lexer:
    def __init__(self):
        self.lexer = lex.lex()