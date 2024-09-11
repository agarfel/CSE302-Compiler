#! /usr/bin/env python3

import ply.yacc as yacc
from bxlexer import tokens



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

#--------- Parser ---------#
class Parser:
    
    
    def __init__(self):
        
        # dictionary of names
        self.names = { }
        self.parser = yacc.yacc()
