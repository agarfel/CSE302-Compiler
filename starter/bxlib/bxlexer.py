#! /usr/bin/env python3

import ply.lex as lex

class Lexer:
    reserved = {
            #'print': 'PRINT',
            'def': 'DEF',
            #'main': 'MAIN',
            'int': 'INT',
            'bool': 'BOOL',
            'var': 'VAR',
            'if': 'IF',
            'else': 'ELSE',
            'while': 'WHILE',
            'break': 'BREAK',
            'continue': 'CONTINUE',
            'true': 'TRUE',
            'false': 'FALSE',
            # 'void': 'VOID',
            'return': 'RETURN',
            'exception': 'EXCEPTION',
            'raise': 'RAISE',
            'try': 'TRY',
            'except': 'EXCEPT',
            'raises': 'RAISES'
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
    'COMMA',
    'COMPLEMENT',
    'EQUALEQUAL',
    'NOTEQUAL',
    'LT',
    'LTEQUAL',
    'GT',
    'GTEQUAL',
    'BAND',
    'BOR',
    'NOT'
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
    t_AND = r'&'
    t_OR = r'\|'
    t_XOR = r'\^'
    t_SEMICOLON = r'\;'
    t_COLON = r':'
    t_COMMA = ','
    t_COMPLEMENT = r'~'
    t_EQUALEQUAL = r'\=\='
    t_NOTEQUAL = r'!\='
    t_LT = r'<'
    t_LTEQUAL = r'<\='
    t_GT = r'>'
    t_GTEQUAL = r'>='
    t_BAND = r'&&'
    t_BOR = r'\|\|'
    t_NOT = r'!'

    t_ignore = ' \t\f\v'
    t_ignore_comments =  r'//.*'


    def t_IDENT(self,t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        t.type = self.reserved.get(t.value, 'IDENT')
        return t

    def t_NUMBER(self, t):
        r'0|[1-9][0-9]*'
        t.value = int(t.value)
        return t

    def t_newline(self, t):
        r'\n'
        t.lexer.lineno += 1


    def t_error(self, t):
        self.reporter.report(f"Illegal character '{t.value[0]}'",  t.lexer.lineno, "Lexing")
        t.lexer.skip(1)


    def __init__(self, reporter):
        self.reporter = reporter
        self.lexer = lex.lex(module=self)