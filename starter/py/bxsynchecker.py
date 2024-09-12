#! /usr/bin/env python3

from bxast import *
from bxerrors import Reporter

class Scope:
    def __init__(self):
        self._variables = set()
    
    def declare(self, name : str):
        assert (name not in self._variables)
        self._variables.add(name)

    def __contains__(self, name: str) -> bool:
        return name in self._variables

class SynChecker:
    def __init__(self, reporter : Reporter):
        self._scopes = Scope()
        self._reporter = reporter

    def for_program(self, p: Program):
        if p == None:
            self._reporter.report("Program is empty", "-1", "Check 1")
            return
        for statement in p.statements:
            self.for_statement(statement)

    def for_expression(self, e: Expr):
        if type(e) == VarExpr:
            if e.name not in self._scopes:
                self._reporter.report(f'undeclared variable: {e.name}', e.line, "Check 1")

        elif type(e) == BinOpExpr:
            self.for_expression(e.left)
            self.for_expression(e.right)

        elif type(e) == UnOpExpr:
            self.for_expression(e.value)
        
        elif type(e) == NumberExpr:
            if not -(2**63) <= int(e.value) < 2**63:
                self._reporter.report("Invalid Integer (too large)", e.line, "Check 1")
                e.value = 0

        else:
            self._reporter.report(f'Unidentified expression: {e}', e.line, "Check 1")

        
    def for_statement(self, s: Statement):
        if type(s) == VarDecl:
            if s.name in self._scopes:
                self._reporter.report(f'Variable declared twice: {s.name}', s.line, "Check 1")
            else:
                self._scopes.declare(s.name)

            self.for_expression(s.value)

        elif type(s) == Assign:
            if s.name not in self._scopes:
                self._reporter.report(f'Undeclared variable: {s.name}', s.line, "Check 1")
            self.for_expression(s.value)
        
        elif type(s) == Print:
            self.for_expression(s.value)

        else:
            self._reporter.report(f'Unidentified statement: {s}', s.line, "Check 1")