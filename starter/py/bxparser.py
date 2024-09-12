#! /usr/bin/env python3

import ply.yacc as yacc
from bxlexer import Lexer
from bxast import *





#--------- Parser ---------#
class Parser:
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
    tokens = Lexer.tokens

    def p_program(self, p):
        """program : DEF MAIN LPAREN RPAREN LCPAREN stmts RCPAREN"""
        p[0] = Program(p[6])

    def p_stmts(self, p):
        """stmts :
                | stmts stmt"""
        if len(p) == 1:
            p[0] = []
        else:
            p[0] = p[1]
            p[0].append(p[2])


    def p_stmt(self, p):
        """stmt : vardecl
        | assign
        | print 
        | """
        p[0] = p[1]


    def p_vardecl(self, p):
        """vardecl : VAR IDENT EQUAL expr COLON INT SEMICOLON"""
        p[0] = VarDecl(name=p[2], type=p[6], value=p[4], line=p.lineno(1))

    def p_assign(self, p):
        """assign : IDENT EQUAL expr SEMICOLON"""
        p[0] = Assign(name=p[1], value=p[3], line=p.lineno(1))

    def p_print(self, p):
        """print : PRINT LPAREN expr RPAREN SEMICOLON"""
        p[0] = Print(value=p[3], line=p.lineno(1))

    def p_expr_ident(self, p):
        """expr : IDENT"""
        p[0] = VarExpr(name=p[1], line=p.lineno(1))

    def p_expr_number(self, p):
        """expr : NUMBER"""
        p[0] = NumberExpr(value=p[1], line=p.lineno(1))

    def p_expr_binop(self, p):
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
        p[0] = BinOpExpr(left=p[1], right=p[3], operation=p[2], line=p.lineno(1))


    def p_expression_negation(self, p):
        """expr : MINUS expr %prec NEGATION"""
        p[0] = UnOpExpr(value=p[2], operation=p[1], line=p.lineno(1))

    def p_expr_complement(self, p):
        """expr : COMPLEMENT expr"""
        p[0] = UnOpExpr(value=p[2], operation=p[1], line=p.lineno(1))


    def p_expr_parens(self, p):
        """expr : LPAREN expr RPAREN
            | LCPAREN expr RCPAREN"""
        p[0] = p[2]

    def p_expr_single(self, p):
        """expr : COLON
            | SEMICOLON
            | EQUAL """

    def p_expr_keywords(self, p):
        """expr : DEF
            | MAIN
            | PRINT
            | INT """


    def p_error(self, t):
        if t != None:
            self.reporter.report("Syntax error at '%s'" % t.value, t.lineno, "Parsing")
        else:
            self.reporter.report("Found '%s'" % t, -1, "Parsing")
    
    def __init__(self, reporter):
        
        # dictionary of names
        self.names = { }
        self.reporter = reporter
        self.parser = yacc.yacc(module=self)
