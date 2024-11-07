#! /usr/bin/env python3

from bxlib.bxast import *
from bxlib.bxerrors import Reporter

bool_op = ['||','&&','<','>','<=','>=','!','==','!=']
int_op = ['|','^','&','<<','>>','+','-','*','/','%','-','~']

class ProcedureType():
    def __init__(self, input_types, return_type):
        if type(return_type) == str:
            self.return_type = return_type
        else: self.return_type = return_type.ty
        if len(input_types) == 0:
            self.input_types = []
        elif type(input_types[0]) == str:
            self.input_types = input_types
        elif type(input_types[0]) == Param:
            r = []
            for param in input_types:
                for var in param.name:
                    r += param.ty.ty
            self.input_types = r
        elif type(input_types[0]) == VarExpr:
            r = []
            for var in input_types:
                r += var.ty
            self.input_types = r

    def __str__(self):
        r = ', '.join(self.input_types)
        r += f'  -->  {self.return_type}'
        return r


class Scope:
    def __init__(self):
        self.variables = dict()
    
    def declare(self, name : str, type : str):
        if name in self:

            return
        self.variables[name] = type

    def __contains__(self, name: str) -> bool:
        return name in self.variables.keys()

class TypeChecker:
    def __init__(self, reporter : Reporter):
        self.scopes = [Scope()]
        self.procedures = {'__bx_print_int': ProcedureType(['int'], 'void'), '__bx_print_bool': ProcedureType(['bool'], 'void')}  # Procedure_name : ([type of arguments], return type / void))
        self.reporter = reporter
        self.proc = None
        self.functions = {'Function': [], 'Subroutine': []}

    def is_declared(self, name):
        for scope in reversed(self.scopes):
            if name in scope.variables.keys():
                return True
        return False

    def getVar_type(self, name, line):
        for scope in reversed(self.scopes):
            if name in scope.variables.keys():
                return scope.variables[name]
        self.reporter.report(f"Undefined variable {name}", line, self.reporter.stage)
        return

    def setVar_type(self, name, ty, line):
        for scope in reversed(self.scopes):
            if name in scope.variables.keys():
                scope.variables[name] = ty
                return
        self.reporter.report(f"Undefined variable {name}", line, self.reporter.stage)
        return

    def declare_var(self, name, ty):
        if name in self.scopes[-1]:
            self.reporter.report(f'Variable {name} already declared in scope.', -1 , self.reporter.stage)
            return
        else:
            self.scopes[-1].declare(name, ty)

    def get_processes(self, p):
        for decl in p:
            if type(decl) == ProcDecl:
                if len(decl.name) >= 5 and decl.name[:5] == '__bx_':
                    self.reporter.report(f'Cannot declare procedures starting with "__bx_": {decl.name}', decl.line , self.reporter.stage)
                    return
                if decl.name in self.procedures.keys():
                    self.reporter.report(f'Procedure {decl.name} already declared.', decl.line , self.reporter.stage)
                    return
                arg_ty = []
                for param in decl.args:
                    for n in param.name:
                        arg_ty.append(param.ty.ty)
                if decl.return_ty == None:
                    self.procedures[decl.name] = ProcedureType(arg_ty, 'void')
                    self.functions['Subroutine'].append(decl.name)
                else:
                    self.procedures[decl.name] = ProcedureType(arg_ty, decl.return_ty.ty)
                    self.functions['Function'].append(decl.name)

                if not self.hasReturn(decl.block):
                    self.reporter.report(f'Procedure {decl.name} is missing a return statement.', decl.line , self.reporter.stage)
                    


    def for_program(self, p: list):
        if len(p) == 0:
            self.reporter.report("Program is empty", "-1", self.reporter.stage)
            return
        self.get_processes(p)
        if 'main' not in self.procedures.keys():
            self.reporter.report("main() not found", "-1", self.reporter.stage)
            return
        for decl in p:
            self.for_decl(decl)


    def for_decl(self, decl):
        # print(decl)
        if type(decl) == VarDecl:
            self.for_varDecl(decl)
        elif type(decl) == ProcDecl:
            self.for_procDecl(decl)
        else:
            self.reporter.report(f'Unidentified declaration: {decl}', decl.line, self.reporter.stage)
            return

    def for_varDecl(self, decl):
        for var_init in decl.var_l:
            self.for_varInit(var_init, decl.ty.ty)

    def for_varInit(self, var_init, ty):
        # print(type(var_init))
        self.for_expression(var_init.value)
        expr_ty = var_init.value.ty
        if expr_ty != ty:   # Check if type of expression matches declared type
            self.reporter.report(f'Declaring variable {var_init.name} of type {ty} but found type {expr_ty}', var_init.line, self.reporter.stage)
            return
        if len(self.scopes) == 1:   # Check if it's a Global Variable
            if ty not in ['bool', 'int']:
                self.reporter.report(f'Global variable {var_init.name} is of type {ty}. Expected type Bool or Int', var_init.line, self.reporter.stage)
                return
        self.declare_var(var_init.name, ty)

    def for_procDecl(self, decl):
        self.proc = decl.name
        self.for_block(decl.block, decl.args)
        self.proc = None

    def for_args(self, args):
        r = []
        for param in args:
            for var in param:
                r.append(param.ty)
        return r

    def for_block(self, p: Block, args=None):
        self.scopes.append(Scope())
        if args != None:
            for param in args:
                for var in param.name:
                    self.declare_var(var, param.ty.ty)

        for statement in p.statements:
            self.for_statement(statement)
        self.scopes.pop()

    def for_statement(self, s: Statement):
        if type(s) == VarDecl:
            self.for_varDecl(s)
            
        elif type(s) == Block:
            self.for_block(s)

        elif type(s) == Assign:
            if not self.is_declared(s.name):    # Check already declared
                self.reporter.report(f'Undeclared variable: {s.name}', s.line, self.reporter.stage)
                return
            self.for_expression(s.value)
            var_ty = self.getVar_type(s.name, s.line)
            if s.value.ty != var_ty:
                self.reporter.report(f'Cannot assign value of type {s.value.ty} to variable of type {var_ty}', s.line, self.reporter.stage)
                return

        elif type(s) == Eval:
            self.for_expression(s.value)

        elif type(s) == Ifelse:
            self.for_expression(s.condition)
            if s.condition.ty != 'bool':
                self.reporter.report(f'Cannot use value of type {s.condition.ty} as condition. Expected expression of type bool', s.line, self.reporter.stage)
                return
            self.for_statement(s.ifbranch)
            self.for_statement(s.elsebranch)

        elif type(s) == While:
            self.for_expression(s.condition)
            if s.condition.ty != 'bool':
                self.reporter.report(f'Cannot use value of type {s.condition.ty} as condition. Expected expression of type bool', s.line, self.reporter.stage)
                return
            self.for_statement(s.block)

        elif type(s) == Jump:
            pass
        
        elif type(s) == Return:
            if self.proc == None:
                self.reporter.report(f'Return found outside procedure', s.line, self.reporter.stage)
                return
            if s.value != None:
                self.for_expression(s.value)
                ret_v = s.value.ty
            else:
                ret_v = 'void'
            if ret_v != self.procedures[self.proc].return_type:
                self.reporter.report(f'Returning with value of type {ret_v} expected {self.procedures[self.proc].return_type}', s.line, self.reporter.stage)
                return

        else:
            self.reporter.report(f'Unidentified statement: {s}', s.line, self.reporter.stage)
            return


    def for_expression(self, e: Expr):
        if type(e) == VarExpr:
            if not self.is_declared(e.name):
                self.reporter.report(f'Undeclared variable: {e.name}', e.line, self.reporter.stage)
                return
            tmp = self.getVar_type(e.name, e.line)
            if tmp != 'int' and tmp != 'bool':
                self.reporter.report(f"Invalid variable type: {e.name} is a {tmp}", e.line, self.reporter.stage)
                return
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
                        return

                if e.operation in ['<','>','<=','>=','!','==','!=']:
                    if e.left.ty == e.right.ty == 'int':
                        e.ty = 'bool'
                    else:
                        self.reporter.report(f'Cannot perform operation {e.operation} between instances of types {e.left.ty} and {e.right.ty}, expected type int', e.line, self.reporter.stage)
                        return

            if e.operation in int_op:
                if e.left.ty == e.right.ty == 'int':
                    e.ty = 'int'
                else:
                    self.reporter.report(f'Cannot perform operation {e.operation} between instances of types {e.left.ty} and {e.right.ty}, expected type int', e.line, self.reporter.stage)
                    return

        elif type(e) == UnOpExpr:
            self.for_expression(e.value)
            if e.operation == '!':
                if e.value.ty == 'bool':
                    e.ty = 'bool'
                else:
                    self.reporter.report(f'Cannot perform operation {e.operation} in instance of type {e.value.ty}, expected type bool', e.line, self.reporter.stage)
                    return
            if e.operation in ['-','~']:
                if e.value.ty == 'int':
                    e.ty = 'int'
                else:
                    self.reporter.report(f'Cannot perform operation {e.operation} in instance of type {e.value.ty}, expected type int', e.line, self.reporter.stage)
                    return

        elif type(e) == NumberExpr:
            if not -(2**63) <= int(e.value) < 2**63:
                self.reporter.report("Invalid Integer (too large)", e.line, self.reporter.stage)
                return
            e.ty = 'int'

        elif type(e) == Bool:
            if e.value not in ['true','false']:
                self.reporter.report(f"Invalid Boolean: {e.value}", e.line, self.reporter.stage)
                return
            e.ty = 'bool'
        
        elif type(e) == ProcCall:
            for arg in e.args:
                self.for_expression(arg)
            if e.name == 'print':
                if e.args[0].ty == 'int':
                    e.name = '__bx_print_int'
                elif e.args[0].ty == 'bool':
                    e.name = '__bx_print_bool'
                else:
                    self.reporter.report(f"Procedure print called with unexpected type {[a.ty for a in e.args]} . Expected int or bool", e.line, self.reporter.stage)

            if e.name not in self.procedures.keys():    # Procedure not defined or called yet
                self.reporter.report(f"Calling undeclared procedure: {e.name}", e.line, self.reporter.stage)
                return
            if len(e.args) != len(self.procedures[e.name].input_types):
                self.reporter.report(f"Calling procedure {e.name} with {len(e.args)} arguments. Expected {len(self.procedures[e.name].input_types)}", e.line, self.reporter.stage)
                return

            for i, arg in enumerate(e.args):
                if arg.ty != self.procedures[e.name].input_types[i]:
                    self.reporter.report(f"Procedure {e.name} called with unexpected type {arg.ty} . Expected {self.procedures[e.name]}", e.line, self.reporter.stage)
                    return
            e.ty = self.procedures[e.name].return_type


        else:
            self.reporter.report(f'Unidentified expression: {e}', e.line, self.reporter.stage)
            return

    def hasReturn(self, statement):
        if type(statement) == Return:
            return True
        elif  type(statement) == Ifelse:
            return self.hasReturn(statement.ifbranch) and self.hasReturn(statement.elsebranch)
        elif type(statement) == Block:
            return any([self.hasReturn(s) for s in statement.statements])
        else:
            return False