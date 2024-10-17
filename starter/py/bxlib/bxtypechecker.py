#! /usr/bin/env python3

from bxlib.bxast import *
from bxlib.bxerrors import Reporter

bool_op = ['||','&&','<','>','<=','>=','!','==','!=']
int_op = ['|','^','&','<<','>>','+','-','*','/','%','-','~']

class Scope:
    def __init__(self):
        self._variables = dict()
    
    def declare(self, name : str, type : str):
        self._variables[name] = type

    def __contains__(self, name: str) -> bool:
        return name in self._variables.keys()

class TypeChecker:
    def __init__(self, reporter : Reporter):
        self._scopes = []
        self.reporter = reporter

    def getVar_type(self, name, line):
        for scope in reversed(self._scopes):
            if name in scope._variables.keys():
                return scope._variables[name]
        self.reporter.report(f"Undefined variable {name}", line, self.reporter.stage)

    def setVar_type(self, name, ty, line):
        for scope in reversed(self._scopes):
            if name in scope._variables.keys():
                scope._variables[name] = ty
                return
        self.reporter.report(f"Undefined variable {name}", line, self.reporter.stage)

    def for_block(self, p: Block):
        self._scopes.append(Scope())
        for statement in p.statements:
            self.for_statement(statement)
        self._scopes.pop()

    def for_expression(self, e: Expr):
        if type(e) == VarExpr:
            tmp = self.getVar_type(e.name, e.line)
            if tmp != 'int':
                self.reporter.report(f"Invalid variable type: {e.name} is a {tmp}", e.line, self.reporter.stage)
            e.ty = tmp

        elif type(e) == BinOpExpr:
            self.for_expression(e.left)
            self.for_expression(e.right)
            if e.operation in bool_op:
                if e.operation in ['&&','||']:
                    if e.left.ty == e.right.ty == 'bool':
                        e.ty = 'bool'
                    else:
                        self.reporter.report(f'Cannot perform operation {e.operation} between instances of types {e.left.ty} and {e.right.ty}, expected type bool', e.line, self.reporter.stage)
                if e.operation in ['<','>','<=','>=','!','==','!=']:
                    if e.left.ty == e.right.ty == 'int':
                        e.ty = 'bool'
                    else:
                        self.reporter.report(f'Cannot perform operation {e.operation} between instances of types {e.left.ty} and {e.right.ty}, expected type int', e.line, self.reporter.stage)
            if e.operation in int_op:
                if e.left.ty == e.right.ty == 'int':
                    e.ty = 'int'
                else:
                    self.reporter.report(f'Cannot perform operation {e.operation} between instances of types {e.left.ty} and {e.right.ty}, expected type int', e.line, self.reporter.stage)

        elif type(e) == UnOpExpr:
            self.for_expression(e.value)
            if e.operation == '!':
                if e.value.ty == 'bool':
                    e.ty = 'bool'
                else:
                    self.reporter.report(f'Cannot perform operation {e.operation} in instance of type {e.value.ty}, expected type bool', e.line, self.reporter.stage)
            if e.operation in ['-','~']:
                if e.value.ty == 'int':
                    e.ty = 'int'
                else:
                    self.reporter.report(f'Cannot perform operation {e.operation} in instance of type {e.value.ty}, expected type int', e.line, self.reporter.stage)
        
        elif type(e) == NumberExpr:
            e.ty = 'int'

        elif type(e) == Bool:
            e.ty = 'bool'
        

    def for_statement(self, s: Statement):
        if type(s) == VarDecl:
            self.for_expression(s.value)
            if s.value.ty not in ['int']:
                self.reporter.report(f'Cannot declare variable of type {s.value.ty}. Type not recognized', s.line, self.reporter.stage)
            #if s.value.ty == s.ty:
            self._scopes[-1].declare(s.name, s.value.ty)
            #else:
            #    self.reporter.report(f'Cannot declare variable of type {s.ty} with value of type {s.value.ty}', s.line, self.reporter.stage)

        elif type(s) == Assign:
            self.for_expression(s.value)
            tmp = self.getVar_type(s.name, s.line)
            if s.value.ty != tmp:
                self.reporter.report(f'Cannot assign value of type {s.value.ty} to variable of type {tmp}', s.line, self.reporter.stage)

        elif type(s) == Print:
            self.for_expression(s.value)

        elif type(s) == Block:
            self.for_block(s)
        
        elif type(s) == Ifelse:
            self.for_expression(s.condition)
            if s.condition.ty != 'bool':
                self.reporter.report(f'Cannot use value of type {s.condition.ty} as condition. Expected expression of type bool', s.line, self.reporter.stage)
            self.for_statement(s.ifbranch)
            self.for_statement(s.elsebranch)

        elif type(s) == While:
            self.for_expression(s.condition)
            if s.condition.ty != 'bool':
                self.reporter.report(f'Cannot use value of type {s.condition.ty} as condition. Expected expression of type bool', s.line, self.reporter.stage)
            self.for_statement(s.block)

        elif type(s) == Jump:
            pass

        else:
            self.reporter.report(f'Unidentified statement: {s}', s.line, self.reporter.stage)
