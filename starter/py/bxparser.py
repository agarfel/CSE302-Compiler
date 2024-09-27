#! /usr/bin/env python3

import ply.yacc as yacc
from bxlexer import Lexer
from bxast import *


#--------- Parser ---------#
class Parser:
    precedence = (
        ('left', 'BOR'),
        ('left', 'BAND'),
        ('left', 'OR'),
        ('left', 'XOR'),
        ('left', 'AND'),
        ('nonassoc', 'EQUALEQUAL','NOTEQUAL'),
        ('nonassoc', 'LT','LTEQUAL','GT','GTEQUAL'),
        ('left', 'LSHIFT','RSHIFT'),
        ('left', 'PLUS','MINUS'),
        ('left', 'STAR','SLASH','MOD'),
        ('nonassoc', 'NEGATION', 'NOT'),
        ('nonassoc', 'COMPLEMENT')
        )
    tokens = Lexer.tokens

    def p_program(self, p):
        """program : DEF MAIN LPAREN RPAREN LCPAREN stmts RCPAREN"""
        p[0] = Block(statements=p[6], line=p.lineno(1))

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
        | block
        | ifelse
        | while
        | jump 
        | """
        p[0] = p[1]


    def p_vardecl(self, p):
        """vardecl : VAR IDENT EQUAL expr COLON INT SEMICOLON"""
        p[0] = VarDecl(name=p[2], ty=p[6], value=p[4], line=p.lineno(1))

    def p_assign(self, p):
        """assign : IDENT EQUAL expr SEMICOLON"""
        p[0] = Assign(name=p[1], value=p[3], line=p.lineno(1))

    def p_print(self, p):
        """print : PRINT LPAREN expr RPAREN SEMICOLON"""
        p[0] = Print(value=p[3], line=p.lineno(1))

    def p_ifelse(self, p):
        """ifelse : IF LPAREN expr RPAREN block
                    | IF LPAREN expr RPAREN block ELSE block
                    | IF LPAREN expr RPAREN block ELSE ifelse
                     """
        if len(p) != 7:
                p[0] = Ifelse(condition=p[3], ifbranch=p[5], elsebranch=Block(statements=[], line=p.lineno(1)), line=p.lineno(1))
        else:
            p[0] = Ifelse(condition=p[3], ifbranch=p[5], elsebranch=p[7], line=p.lineno(1))

    def p_while(self, p):
        """while : WHILE LPAREN expr RPAREN block"""
        p[0] = While(condition=p[3], block=p[5], line=p.lineno(1))

    def p_jump(self, p):
        """jump : BREAK SEMICOLON
                | CONTINUE SEMICOLON"""
        p[0] = Jump(ty=p[1], line=p.lineno(1))

    def p_block(self, p):
        """block : LCPAREN stmts RCPAREN"""
        p[0] = Block(statements=p[2], line=p.lineno(1))

    def p_expr_ident(self, p):
        """expr : IDENT"""
        p[0] = VarExpr(name=p[1], line=p.lineno(1), ty='undefined')

    def p_expr_number(self, p):
        """expr : NUMBER"""
        p[0] = NumberExpr(value=p[1], line=p.lineno(1), ty='undefined')

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
        | expr RSHIFT expr
        | expr EQUALEQUAL expr
        | expr NOTEQUAL expr
        | expr LT expr
        | expr LTEQUAL expr
        | expr GT expr
        | expr GTEQUAL expr
        | expr BOR expr
        | expr BAND expr
"""
        p[0] = BinOpExpr(left=p[1], right=p[3], operation=p[2], line=p.lineno(1), ty='undefined')


    def p_expression_unop(self, p):
        """expr : MINUS expr %prec NEGATION
                | COMPLEMENT expr
                | NOT expr"""
        p[0] = UnOpExpr(value=p[2], operation=p[1], line=p.lineno(1), ty='undefined')


    def p_expr_parens(self, p):
        """expr : LPAREN expr RPAREN"""
        p[0] = p[2]

    def p_expr_bool(self, p):
        """expr : TRUE
                | FALSE """
        p[0] = Bool(value=p[1], ty='undefined', line=p.lineno(1))
    
    def p_expr_keywords(self, p):
        """expr : DEF
            | MAIN
            | PRINT
            | INT """


    def p_error(self, t):
        if t != None:
            self.reporter.report("Syntax error at '%s'" % t.value, t.lineno, self.reporter.stage)
        else:
            self.reporter.report("Found '%s'" % t, -1, self.reporter.stage)
    
    def __init__(self, reporter):
        
        # dictionary of names
        self.names = { }
        self.reporter = reporter
        self.parser = yacc.yacc(module=self)
