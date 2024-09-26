#! /usr/bin/env python3
from bxast import *

class Scope:
    def __init__(self, start):
        self.variables = dict()
        self.start = start
    
    
    def declare(self, name : str, register : str):
        self._variables[name] = register


class ToTac:
    def __init__(self, reporter):
        self.tmp_counter = 0
        self.label_counter = 0
        self.body = []
        self.scopes = []
        self.reporter = reporter

    def getVar_register(self, name):
        for scope in reversed(self.scopes):
            if name in scope.variables.keys():
                return scope.variables[name]
        self._reporter.report(f"Undefined variable {name}", -1, 'Transforming AST to TAC')

    def processBlock(self, p : Block):
        #TO DO
        if p == None:
            self.reporter.report("Block is empty", p.line, "Transforming AST to TAC")
            return
        s = self.label_counter
        self.scopes.append(Scope(s))
        self.body.append({"opcode": "label", "args": ['%.s{s}:'], "result": None})
        self.label_counter += 1
        for statement in p.statements:
            self.processStatement(statement)
        self.body.append({"opcode": "label", "args": ['%.e{s}:'], "result": None})

        self.scopes.pop()

    def processStatement(self, s: Statement):
        if type(s) == VarDecl:
            value = self.processExpression(s.value)
            tmp = self.tmp_counter
            self.tmp_counter += 1
            self.scopes[-1].variables[s.name] = f'%{tmp}'
            self.body.append({"opcode": "copy", "args": [value], "result": f'%{tmp}'})

        elif type(s) == Assign:
            value = self.processExpression(s.value)
            var = self.getVar_register(s.name)
            self.body.append({"opcode": "copy", "args": [value], "result": var})

        elif type(s) == Print:
            value = self.processExpression(s.value)
            self.body.append({"opcode": "print", "args": [value], "result": None})

        elif type(s) == Block:
            self.processBlock(s)

        elif type(s) == Ifelse:
            condition = self.processExpression(s.condition)
            self.body.append({"opcode": "CMP", "args": [condition], "result": None})
            self.body.append({"opcode": "jump", "args": [self.label_counter], "result": None})
            self.processBlock(s.ifbranch)
            self.body.append({"opcode": "jump", "args": [self.label_counter], "result": None})
            self.processBlock(s.elsebranch)

        
        elif type(s) == While:
            condition = self.processExpression(s.condition)
            self.body.append({"opcode": "CMP", "args": [condition], "result": None})
            self.body.append({"opcode": "jump", "args": [self.label_counter],"result":  None})
            self.processBlock(s.block)    

        elif type(s) == Jump:
            if s.ty == 'break':
                self.body.append({"opcode": "JUMP", "args": [f'e{self.scopes[-1].start}'], "result": None})
            elif s.ty == 'continue':
                self.body.append({"opcode": "JUMP", "args": [f's{self.scopes[-1].start}'], "result": None})
            else:
                self.reporter.report("Unidentified jump: {s.ty}", s.line, "Transforming AST to TAC")

    def processExpression(self, e : Expr):
        if type(e) == VarExpr:
            var = self.getVar_register(e.name)
            return var

        elif type(e) == NumberExpr:
            tmp = self.tmp_counter
            self.tmp_counter += 1
            self.body.append({"opcode": "const", "args": [e.value], "result": f'%{tmp}'})
            return f'%{tmp}'

        elif type(e) == BinOpExpr:
            left = self.processExpression(e.left)
            right = self.processExpression(e.right)
            tmp = self.tmp_counter
            self.tmp_counter += 1
            operation = self.getBinOp(e.operation)
            self.body.append({"opcode": operation, "args": [left, right], "result": f'%{tmp}'})
            return f'%{tmp}'


        elif type(e) == UnOpExpr:
            value = self.processExpression(e.value)
            operation = self.getUnOp(e.operation)
            tmp = self.tmp_counter
            self.tmp_counter += 1
            self.body.append({"opcode": operation, "args": [value], "result": f'%{tmp}'})
            return f'%{tmp}'



    def getBinOp(self, op):
        if op == '+': return "add"
        elif op == '-': return "sub"
        elif op == '*': return "mul"
        elif op == '/': return "div"
        elif op == '%': return "mod"
        elif op == '&': return "band"
        elif op == '|': return "bor"
        elif op == '^': return "xor"
        elif op == '<<': return "shl"
        elif op == '>>': return "shr"
        #TO DO
        elif op == '==': return "eq"
        elif op == '!=': return "neq"
        elif op == '<': return "lt"
        elif op == '<=': return "lteq"
        elif op == '>': return "gt"
        elif op == '>=': return "gteq"
        elif op == '&&': return "and"
        elif op == '||': return "or"


    def getUnOp(self, op):
        if op == '-': return "neg"
        elif op == '~': return "bnot"
        #TO DO
        elif op == '!': return "not"


    def getData(self):
        data = [{"proc": "@main", "body" : self.body}]
        return data