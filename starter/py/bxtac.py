#! /usr/bin/env python3
from bxast import *
boolOp= {'<': 'jl','>': 'jnl','<=': 'jle','>=': 'jnle','==': 'jz','!=': 'jnz'}

class Scope:
    def __init__(self):
        self.variables = dict()    
    
    def declare(self, name : str, register : str):
        self._variables[name] = register


class ToTac:
    def __init__(self, reporter):
        self.tmp_counter = 0
        self.label_counter = 0
        self.body = []
        self.scopes = []
        self.whiles = []
        self.reporter = reporter

    def emit(self, opcode, args, result):
        self.body.append({"opcode": opcode, "args": args, "result": result})

    def getVar_register(self, name):
        for scope in reversed(self.scopes):
            if name in scope.variables.keys():
                return scope.variables[name]
        self.reporter.report(f"Undefined variable {name}", -1, self.reporter.stage)

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

    def processStatement(self, s: Statement):
        if type(s) == VarDecl:
            value = self.processExpression(s.value)
            tmp = self.tmp_counter
            self.tmp_counter += 1
            self.scopes[-1].variables[s.name] = f'%{tmp}'
            self.emit("copy", [value], f'%{tmp}')

        elif type(s) == Assign:
            value = self.processExpression(s.value)
            var = self.getVar_register(s.name)
            self.emit("copy", [value], var)

        elif type(s) == Print:
            value = self.processExpression(s.value)
            self.emit("print", [value], None)

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
                self.emit("jmp", [self.whiles[-1][1]], None)
            elif s.ty == 'continue':
                self.emit("jmp", [self.whiles[-1][0]], None)
            else:
                self.reporter.report("Unidentified jump: {s.ty}", s.line, self.reporter.stage)

    def processExpression(self, e : Expr):
        if type(e) == VarExpr:
            var = self.getVar_register(e.name)
            return var

        elif type(e) == NumberExpr:
            tmp = self.tmp_counter
            self.tmp_counter += 1
            self.emit("const", [e.value], f'%{tmp}')
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
        # elif op == '>': return "gt"
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
            if e.operation in boolOp.keys():
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
        data = [{"proc": "@main", "body" : self.body}]
        return data