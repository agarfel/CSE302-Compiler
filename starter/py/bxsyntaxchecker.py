#! /usr/bin/env python3

from bxast import *
from bxerrors import Reporter

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
        self._reporter = reporter

    def is_declared(self, name):
        for scope in reversed(self._scopes):
            if name in scope._variables:
                return True

    def for_program(self, p: Block):
        if p == None:
            self._reporter.report("Program is empty", "-1", "Syntax Check")
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
                self._reporter.report(f'Undeclared variable: {e.name}', e.line, "Syntax Check")

        elif type(e) == BinOpExpr:
            self.for_expression(e.left)
            self.for_expression(e.right)

        elif type(e) == UnOpExpr:
            self.for_expression(e.value)
        
        elif type(e) == NumberExpr:
            if not -(2**63) <= int(e.value) < 2**63:
                self._reporter.report("Invalid Integer (too large)", e.line, "Syntax Check")

        elif type(e) == Bool:
            if e.value not in ['true','false']:
                self._reporter.report(f"Invalid Boolean: {e.value}", e.line, "Syntax Check")
        else:
            self._reporter.report(f'Unidentified expression: {e}', e.line, "Syntax Check")

        
    def for_statement(self, s: Statement):
        if type(s) == VarDecl:
            if s.name in self._scopes[-1]._variables:
                self._reporter.report(f'Variable declared twice: {s.name}', s.line, "Syntax Check")
            else:
                self._scopes[-1].declare(s.name)

            self.for_expression(s.value)

        elif type(s) == Assign:
            if not self.is_declared(s.name):
                self._reporter.report(f'Undeclared variable: {s.name}', s.line, "Syntax Check")
            self.for_expression(s.value)
        
        elif type(s) == Print:
            self.for_expression(s.value)

        elif type(s) == Block:
            self.for_block(s)

        elif type(s) == Ifelse:
            self.for_expression(s.condition)
            self.for_block(s.ifbranch)
            self.for_block(s.elsebranch)

        elif type(s) == While:
            self.for_expression(s.condition)
            self.for_block(s.block)

        elif type(s) == Jump:
            pass
        else:
            self._reporter.report(f'Unidentified statement: {s}', s.line, "Syntax Check")