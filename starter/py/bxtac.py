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
            self.reporter.report("Block is empty", "-1", "Transforming AST to TAC")
            return
        self.scopes.append(Scope(self.tmp_counter))
        self.body.append({f'%.{self.tmp_counter}:'})
        self.tmp_counter += 1
        for statement in p.statements:
            self.processStatement(statement)
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
            #TO DO
            self.processBlock(s)

        elif type(s) == Ifelse:
            #TO DO
            condition = self.processExpression(s.condition)
            self.processBlock(ifbranch)
            self.processBlock(elsebranch)
        
        elif type(s) == While:
            #TO DO
            condition = self.processExpression(s.condition)
            self.processBlock(ifbranch)    

        elif type(s) == Jump:
            #TO DO
            self.body.append({"opcode": "JUMP", "args": [s.type], "result": None})


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
        elif op == '&': return "and"
        elif op == '|': return "or"
        elif op == '^': return "xor"
        elif op == '<<': return "shl"
        elif op == '>>': return "shr"
        #TO DO
        elif op == '==': return ""
        elif op == '!=': return ""
        elif op == '<': return ""
        elif op == '<=': return ""
        elif op == '>': return ""
        elif op == '>=': return ""
        elif op == '&&': return ""
        elif op == '||': return ""


    def getUnOp(self, op):
        if op == '-': return "neg"
        elif op == '~': return "not"
        #TO DO
        elif op == '!': return ""


    def getData(self):
        data = [{"proc": "@main", "body" : self.body}]
        return data