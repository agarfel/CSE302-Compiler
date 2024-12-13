#! /usr/bin/env python3
from bxlib.bxast import *
import hashlib

boolOp= {'<': 'jl','>': 'jg','<=': 'jle','>=': 'jge','==': 'jz','!=': 'jnz'}

class Scope:
    def __init__(self):
        self.variables = dict()    
    
    def declare(self, name : str, register : str):
        self.variables[name] = register


class ToTac:
    def __init__(self, functions, reporter):
        self.tmp_counter = 0
        self.label_counter = 0
        self.body = []
        self.tac = []
        self.scopes = [Scope()]
        self.whiles = []
        self.exceptions_stack = []
        self.reporter = reporter
        self.proc = 'Global'
        self.functions = functions

    def hash_exception(self, name):
        h = hashlib.shake_256(name.encode('utf-8'))
        i = int(h.hexdigest(3), 16)
        return i

    def emit(self, opcode, args, result):
        self.body.append({"opcode": opcode, "args": args, "result": result})

    def getVar_register(self, name):
        for scope in reversed(self.scopes):
            if name in scope.variables.keys():
                return scope.variables[name]
        self.reporter.report(f"Undefined variable {name}", -1, self.reporter.stage)

    def processProgram(self, p):
        self.tac.append({"var": f'@exception', "init": 0})
        self.scopes[-1].variables["exception"] = '@exception'
        for decl in p:
            self.processDeclaration(decl)

    def processBlock(self, p : Block):
        #TO DO
        if p == None:
            self.reporter.report("Block is empty", p.line, self.reporter.stage)
            return
        # s = self.label_counter
        self.scopes.append(Scope())
        # self.emit("label", ['%.s{s}:'],None)
        # self.label_counter += 1
        for statement in p.statements:
            self.processStatement(statement)
        # self.emit("label", ['%.e{s}:'], None)

        self.scopes.pop()

    def processDeclaration(self, s: Decl):
        if type(s) == VarDecl:
            for var in s.var_l:
                if var.value.ty == 'int':
                    if type(var.value.value) != int:
                        self.reporter.report(f'global variable wrong type: {var}', s.line, self.reporter.stage)
                    self.tac.append({"var": f'@{var.name}', "init": var.value.value})
                elif var.value.ty == 'bool':
                    if var.value.value == 'true':
                        self.tac.append({"var": f'@{var.name}', "init": 1})
                    elif var.value.value == 'false':
                        self.tac.append({"var": f'@{var.name}', "init": 0})
                    else:
                        self.reporter.report(f'global variable wrong type: {var}', s.line, self.reporter.stage)
                self.scopes[-1].variables[var.name] = f'@{var.name}'

        elif type(s) == ProcDecl:
            r = [name for p in s.args for name in p.name]
            for x in r:
                self.scopes[-1].variables[x] = f'%{x}'
            self.proc = s.name
            self.processBlock(s.block)
            self.tac.append({"proc": f'@{s.name}', "args": [f'%{x}' for x in r], "body": self.body})
            self.body = []


    def processStatement(self, s: Statement):
        if type(s) == VarDecl:
            for varinit in s.var_l:
                value = self.processExpression(varinit.value)
                tmp = self.tmp_counter
                self.tmp_counter += 1
                self.scopes[-1].variables[varinit.name] = f'%{tmp}'
                self.emit("copy", [value], f'%{tmp}')

        elif type(s) == Assign:
            value = self.processExpression(s.value)
            var = self.getVar_register(s.name)
            self.emit("copy", [value], var)

        elif type(s) == Eval:
            value = self.processExpression(s.value)

        elif type(s) == Block:
            self.processBlock(s)

        elif type(s) == Ifelse:
            lab_true = self.label_counter
            lab_false = self.label_counter + 1
            lab_over =  self.label_counter +2
            self.label_counter += 3

            condition = self.processBool(s.condition, lab_true, lab_false)
            self.emit("label", [lab_true], None)
            self.processStatement(s.ifbranch)
            self.emit("jmp", [lab_over], None)
            self.emit("label", [lab_false], None)
            self.processStatement(s.elsebranch)
            self.emit("label", [lab_over], None)

        
        elif type(s) == While:
            lab_head = self.label_counter
            lab_body = self.label_counter + 1
            lab_end =  self.label_counter +2
            self.label_counter += 3
            self.whiles.append((lab_head, lab_end))
            self.emit("label", [lab_head], None)
            condition = self.processBool(s.condition, lab_body, lab_end)
            self.emit("label", [lab_body], None)
            self.processStatement(s.block)    
            self.emit("jmp", [lab_head], None)
            self.emit("label", [lab_end], None)
            self.whiles.pop()

        elif type(s) == Jump:
            if s.ty == 'break':
                try:
                    self.emit("jmp", [self.whiles[-1][1]], None)
                except:
                    self.reporter.report("Break found outside a while loop", s.line, self.reporter.stage)
 
            elif s.ty == 'continue':
                try:
                    self.emit("jmp", [self.whiles[-1][0]], None)
                except:
                    self.reporter.report("Continue found outside a while loop", s.line, self.reporter.stage)

            else:
                self.reporter.report("Unidentified jump: {s.ty}", s.line, self.reporter.stage)

        elif type(s) == Return:
            if s.value == None:
                self.emit("ret", [], None)
            else:
                value = self.processExpression(s.value)
                self.emit("ret", [value], None)

        elif type(s) == TryExcept:
            lab_exceptions = self.label_counter
            lab_end =  self.label_counter +1
            self.label_counter += 2
            
            self.exceptions_stack.append((lab_exceptions,lab_end))

            self.processStatement(s.block)
            self.emit("jmp", [lab_end], None)
            self.exceptions_stack.pop()

            self.emit("label", [lab_exceptions], None)



            for c in s.catches:
                lab_false =  self.label_counter
                self.label_counter += 1
                var = '@exception'
                h = self.hash_exception(c.name)
                tmp = f'%{self.tmp_counter}'
                self.tmp_counter += 1
                self.emit('const', [h], tmp)
                self.emit('cmpq', [tmp, var], None)
                self.emit('jnz', [lab_false], None)
                tmp = f'%{self.tmp_counter}'
                self.tmp_counter += 1
                self.emit('const', [0], tmp)
                self.emit("copy", [tmp], var)
                self.processStatement(c.block)
                self.emit("jmp", [lab_end], None)
                self.emit("label", [lab_false], None)

            
            tmp = f'%{self.tmp_counter}'
            self.tmp_counter += 1
            var = '@exception'

            self.emit('const', [0], tmp)
            self.emit('cmpq', [tmp, var], None)
            self.emit('jz', [lab_end], None)

            if self.exceptions_stack == []:
                if self.proc in self.functions['Function']:
                    self.emit("ret", [tmp], None)
                else:
                    self.emit("ret", [], None)
            else:
                label = self.exceptions_stack[-1][0]
                self.emit("jmp", [label], None)
                
            self.emit("label", [lab_end], None)

        elif type(s) == Raise:
            var = '@exception'
            tmp = f'%{self.tmp_counter}'
            self.tmp_counter += 1
            h = self.hash_exception(s.name)
            self.emit('const', [h], tmp)
            self.emit("copy", [tmp], var)
            if self.exceptions_stack == []:
                if self.proc in self.functions['Function']:
                    self.emit("ret", [tmp], None)
                else:
                    self.emit("ret", [], None)
            else:
                label = self.exceptions_stack[-1][0]
                self.emit("jmp", [label], None)
        
        else:
            self.reporter.report(f'Unrecognized statement: {type(s)}', s.line, self.reporter.stage)




    def processExpression(self, e : Expr):
        if type(e) == VarExpr:
            var = self.getVar_register(e.name)
            return var

        elif type(e) == NumberExpr:
            tmp = self.tmp_counter
            self.tmp_counter += 1
            self.emit("const", [e.value], f'%{tmp}')
            return f'%{tmp}'
        
        elif type(e) == Bool:
            tmp = self.tmp_counter
            self.tmp_counter += 1
            if e.value == 'true':
                self.emit("const", [1], f'%{tmp}')
            else:
                self.emit("const", [0], f'%{tmp}')
            return f'%{tmp}'

        elif type(e) == BinOpExpr:
            left = self.processExpression(e.left)
            right = self.processExpression(e.right)
            tmp = self.tmp_counter
            self.tmp_counter += 1
            operation = self.getBinOp(e.operation)
            self.emit(operation, [left, right], f'%{tmp}')
            return f'%{tmp}'


        elif type(e) == UnOpExpr:
            value = self.processExpression(e.value)
            operation = self.getUnOp(e.operation)
            tmp = self.tmp_counter
            self.tmp_counter += 1
            self.emit(operation, [value], f'%{tmp}')
            return f'%{tmp}'

        elif type(e) == ProcCall:
            for i, arg in enumerate(e.args[:6]):
                value = self.processExpression(arg)
                self.emit('param', [i+1, value], None)
            for i, arg in enumerate(e.args[6:]):
                value = self.processExpression(arg)
                self.emit('param', [len(e.args)-i, value], None)
            return_value = None
            if e.name in self.functions['Function']:
                tmp = self.tmp_counter
                self.tmp_counter += 1
                self.emit('call', [f'@{e.name}', len(e.args)+1], f'%{tmp}')
                return_value = f'%{tmp}'
            else:
                self.emit('call', [f'@{e.name}', len(e.args)+1], None)

            tmp = f'%{self.tmp_counter}'
            lab_no_exception =  self.label_counter
            self.label_counter += 1
            self.tmp_counter += 1
            var = '@exception'

            self.emit('const', [0], tmp)
            self.emit('cmpq', [tmp, var], None)
            self.emit('jz', [lab_no_exception], None)

            if self.exceptions_stack == []:
                if self.proc in self.functions['Function']:
                    self.emit("ret", [tmp], None)
                else:
                    self.emit("ret", [], None)
            else:
                label = self.exceptions_stack[-1][0]
                self.emit("jmp", [label], None)
            self.emit("label", [lab_no_exception], None)

            return return_value

            
        else:
            self.reporter.report(f'Unrecognized expression: {type(e)}', e.line, self.reporter.stage)

    def getBinOp(self, op):
        if op == '+': return "add"
        elif op == '-': return "sub"
        elif op == '*': return "mul"
        elif op == '/': return "div"
        elif op == '%': return "mod"
        elif op == '&': return "and"
        elif op == '|': return "or"
        elif op == '^': return "xor"
        elif op == '<<': return "shl"
        elif op == '>>': return "shr"
        # elif op == '==': return "eq"
        # elif op == '!=': return "neq"
        # elif op == '<': return "lt"
        # elif op == '<=': return "lteq"
        # elif op == '>': return "gt"self.label_counter += 
        # elif op == '>=': return "gteq"
        # elif op == '&&': return "and"
        # elif op == '||': return "or"


    def getUnOp(self, op):
        if op == '-': return "neg"
        elif op == '~': return "not"
        # elif op == '!': return "not"

    def processBool(self, e, lab_true, lab_false):
        if type(e) == Bool:
            if e.value == 'true':
                self.emit('jmp', [lab_true], None)
            elif e.value == 'false':
                self.emit('jmp', [lab_false], None)
        else:
            if type(e) == VarExpr:
                var = self.getVar_register(e.name)
                tmp = f'%{self.tmp_counter}'
                self.tmp_counter += 1
                self.emit('const', [0], tmp)
                self.emit('cmpq', [tmp, var], None)
                self.emit('jnz', [lab_true], None)
                self.emit('jmp', [lab_false], None)
            elif e.operation in boolOp.keys():
                t1 = self.processExpression(e.left)
                t2 = self.processExpression(e.right)
                self.emit('cmpq', [t1, t2], None)
                self.emit(boolOp[e.operation], [lab_true], None)
                self.emit('jmp', [lab_false], None)
            
            elif e.operation =='!':
                self.processBool(e.value, lab_false, lab_true)
            
            elif e.operation == '&&':
                self.processBool(e.left, self.label_counter, lab_false)
                self.emit('label', [self.label_counter], None)
                self.label_counter += 1
                self.processBool(e.right, lab_true, lab_false)

            elif e.operation == '||':
                self.processBool(e.left, lab_true, self.label_counter)
                self.emit('label', [self.label_counter], None)
                self.label_counter += 1
                self.processBool(e.right, lab_true, lab_false)

    def getData(self):
        return self.tac