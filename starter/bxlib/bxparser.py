#! /usr/bin/env python3

import ply.yacc as yacc
from bxlib.bxlexer import Lexer
from bxlib.bxast import *


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
        """program : decl
                | decl program"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = [p[1]]
            p[0] += p[2]

    def p_decl(self, p):
        """decl : vardecl
        | procdecl 
        | exception"""
        p[0] = p[1]

    def p_exception(self, p):
        """exception : EXCEPTION IDENT SEMICOLON"""
        p[0] = ExceptionDecl(name=p[2], line=p.lineno(1))
            
    def p_procdecl(self, p):
        """procdecl : DEF IDENT LPAREN params RPAREN COLON ty RAISES raises block
                    | DEF IDENT LPAREN params RPAREN COLON ty block
                    | DEF IDENT LPAREN params RPAREN RAISES raises block
                    | DEF IDENT LPAREN params RPAREN block """

        if len(p) == 7:
            # print(1, p[2])
            p[0] = ProcDecl(name=p[2], args=p[4], block=p[6], return_ty=None, raises=[], line=p.lineno(1))

        elif len(p) == 9 and type(p[7])==Ty:
            p[0] = ProcDecl(name=p[2], args=p[4], return_ty=p[7], raises=[], block=p[8], line=p.lineno(1))
            # print(2, p[2])
        elif len(p) == 9:
                p[0] = ProcDecl(name=p[2], args=p[4], return_ty=None, raises=p[7], block=p[8], line=p.lineno(1))
        elif len(p) == 11:
            p[0] = ProcDecl(name=p[2], args=p[4], return_ty=p[7], raises=p[9], block=p[10], line=p.lineno(1))
        else: print('CRY')

    def p_raises(self, p):
        """raises : IDENT COMMA raises
                    | IDENT
                    |"""
        if len(p) == 1:
            p[0] = []
        elif len(p) == 2:
            p[0] = [Raises(name=p[1], line=p.lineno(1))]
        else:
            p[0] = [Raises(name=p[1], line=p.lineno(1))]
            p[0] += p[3]

    def p_param(self, p):
        """params : identl COLON ty
                | identl COLON ty COMMA params 
                | """

        if len(p) == 1:
            p[0] = []
        elif len(p) == 4:
            p[0] = [Param(name=p[1], ty=p[3], line=p.lineno(1))]
        else:
            p[0] = [Param(name=p[1], ty=p[3], line=p.lineno(1))]
            p[0]+= p[5]

    def p_identl(self,p):
        """identl : IDENT 
                    | IDENT COMMA identl"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0]= [p[1]]
            p[0] += p[3]

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
        | block
        | eval
        | ifelse
        | while
        | jump 
        | return
        | raise
        | tryexcept
        | """
        p[0] = p[1]

    def p_tryexcept(self, p):
        """tryexcept : TRY block catches"""
        p[0] = TryExcept(block=p[2], catches=p[3], line=p.lineno(1))

    def p_catches(self, p):
        """catches : EXCEPT IDENT block catches
                    | """
        if len(p) == 1:
            p[0] = []
        else:
            p[0] = [Catch(name=p[2], block=p[3], line=p.lineno(1))]
            p[0] += p[4]


    def p_raise(self, p):
        """raise : RAISE IDENT SEMICOLON"""
        p[0] = Raise(name=p[2], line=p.lineno(1))

    def p_vardecl(self, p):
        """vardecl : VAR varinits COLON ty SEMICOLON"""
        p[0] = VarDecl(var_l=p[2], ty=p[4], line=p.lineno(1))

    def p_varninits(self, p):
        """varinits : IDENT EQUAL expr 
                | IDENT EQUAL expr COMMA varinits"""
        if len(p) == 4:
            p[0] = [VarInit(name=p[1], value=p[3], line=p.lineno(1))]
        else:
            p[0] = [VarInit(name=p[1], value=p[3], line=p.lineno(1))]
            p[0] += p[5]

    def p_assign(self, p):
        """assign : IDENT EQUAL expr SEMICOLON"""
        p[0] = Assign(name=p[1], value=p[3], line=p.lineno(1))

    def p_eval(self, p):
        """eval : expr SEMICOLON"""
        p[0] = Eval(value=p[1], line=p.lineno(1))

    def p_ifelse(self, p):
        """ifelse : IF LPAREN expr RPAREN block
                    | IF LPAREN expr RPAREN block ELSE block
                    | IF LPAREN expr RPAREN block ELSE ifelse
                     """
        if len(p) != 8:
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

    def p_return(self, p):
        """return : RETURN SEMICOLON
                | RETURN expr SEMICOLON"""
        if len(p) == 3:
            p[0] = Return(value=None, line=p.lineno(1))
        else:
            p[0] = Return(value=p[2], line=p.lineno(1))

    def p_block(self, p):
        """block : LCPAREN stmts RCPAREN"""
        p[0] = Block(statements=p[2], line=p.lineno(1))

    def p_expr_ident(self, p):
        """expr : IDENT"""
        p[0] = VarExpr(name=p[1], line=p.lineno(1), ty='undefined')

    def p_expr_number(self, p):
        """expr : NUMBER
                | MINUS NUMBER"""
        if len(p) == 2:
            p[0] = NumberExpr(value=p[1], line=p.lineno(1), ty='undefined')
        else:
            p[0] = NumberExpr(value=-p[1], line=p.lineno(1), ty='undefined')

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
    
    def p_expr_proccall(self, p):
        """expr : IDENT LPAREN args RPAREN """
        if len(p) == 5:
            p[0] = ProcCall(name=p[1], args=p[3], line=p.lineno(1),ty='undefined')
        else:
            p[0] = ProcCall(name=p[1], args=None, line=p.lineno(1),ty='undefined')

    def p_args(self, p):
        """args : expr COMMA args
                | expr
                | """
        if len(p) == 1:
            p[0] = []
        elif len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = [p[1]]
            p[0] += p[3]

    def p_type(self, p):
        """ty : BOOL
                | INT"""
        p[0] = Ty(ty=p[1], line=p.lineno(1))

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
