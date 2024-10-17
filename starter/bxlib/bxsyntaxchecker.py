#! /usr/bin/env python3

from bxlib.bxast import *
from bxlib.bxerrors import Reporter

class Scope:
    def __init__(self, ):
        self._variables = set()
    
    def declare(self, name : str):
        assert (name not in self._variables)
        self._variables.add(name)

    def __contains__(self, name: str) -> bool:
        return name in self._variables

class SyntaxChecker:
    def __init__(self, reporter : Reporter):
        self._scopes = []
        self.reporter = reporter

    def is_declared(self, name):
        for scope in reversed(self._scopes):
            if name in scope._variables:
                return True

    def for_program(self, p: Block):
        if p == None:
            self.reporter.report("Program is empty", "-1", self.reporter.stage)
            return
        self.for_block(p)

    def for_block(self, p: Block):
        self._scopes.append(Scope())
        for statement in p.statements:
            self.for_statement(statement)
        self._scopes.pop()

    def for_expression(self, e: Expr):
        if type(e) == VarExpr:
            if not self.is_declared(e.name):
                self.reporter.report(f'Undeclared variable: {e.name}', e.line, self.reporter.stage)

        elif type(e) == BinOpExpr:
            self.for_expression(e.left)
            self.for_expression(e.right)

        elif type(e) == UnOpExpr:
            self.for_expression(e.value)
        
        elif type(e) == NumberExpr:
            if not -(2**63) <= int(e.value) < 2**63:
                self.reporter.report("Invalid Integer (too large)", e.line, self.reporter.stage)

        elif type(e) == Bool:
            if e.value not in ['true','false']:
                self.reporter.report(f"Invalid Boolean: {e.value}", e.line, self.reporter.stage)
        else:
            self.reporter.report(f'Unidentified expression: {e}', e.line, self.reporter.stage)

        
    def for_statement(self, s: Statement):
        if type(s) == VarDecl:
            if s.name in self._scopes[-1]._variables:
                self.reporter.report(f'Variable declared twice: {s.name}', s.line, self.reporter.stage)
            else:
                self._scopes[-1].declare(s.name)

            self.for_expression(s.value)

        elif type(s) == Assign:
            if not self.is_declared(s.name):
                self.reporter.report(f'Undeclared variable: {s.name}', s.line, self.reporter.stage)
            self.for_expression(s.value)
        
        elif type(s) == Print:
            self.for_expression(s.value)

        elif type(s) == Block:
            self.for_block(s)

        elif type(s) == Ifelse:
            self.for_expression(s.condition)
            self.for_statement(s.ifbranch)
            self.for_statement(s.elsebranch)               

        elif type(s) == While:
            self.for_expression(s.condition)
            self.for_statement(s.block)

        elif type(s) == Jump:
            pass
        else:
            self.reporter.report(f'Unidentified statement: {s}', s.line, self.reporter.stage)