#! /usr/bin/env python3
from bxast import *

class ToTac:
    def __init__(self, reporter):
        self._tmp_counter = 0
        self.body = []
        self.variables = {}
        self.reporter = reporter

    def processProgram(self, p : Program):
        if p == None:
            self.reporter.report("Program is empty", "-1", "Transforming AST to TAC")
            return
        for statement in p.statements:
            self.processStatement(statement)

    def processStatement(self, s: Statement):
        if type(s) == VarDecl:
            value = self.processExpression(s.value)
            tmp = self._tmp_counter
            self._tmp_counter += 1
            self.variables[s.name] = f'%{tmp}'
            self.body.append({"opcode": "copy", "args": [value], "result": f'%{tmp}'})

        elif type(s) == Assign:
            value = self.processExpression(s.value)
            try:
                var = self.variables[s.name]
            except:
                tmp = self._tmp_counter
                self._tmp_counter += 1
                self.variables[s.name] = f'%{tmp}'
            self.body.append({"opcode": "copy", "args": [value], "result": var})

        elif type(s) == Print:
            value = self.processExpression(s.value)
            self.body.append({"opcode": "print", "args": [value], "result": None})


    def processExpression(self, e : Expr):
        if type(e) == VarExpr:
            try:
                var = self.variables[e.name]
            except:
                tmp = self._tmp_counter
                self._tmp_counter += 1
                self.variables[e.name] = f'%{tmp}'
            return self.variables[e.name]

        elif type(e) == NumberExpr:
            tmp = self._tmp_counter
            self._tmp_counter += 1
            self.body.append({"opcode": "const", "args": [e.value], "result": f'%{tmp}'})
            return f'%{tmp}'

        elif type(e) == BinOpExpr:
            left = self.processExpression(e.left)
            right = self.processExpression(e.right)
            tmp = self._tmp_counter
            self._tmp_counter += 1
            operation = self.getBinOp(e.operation)
            self.body.append({"opcode": operation, "args": [left, right], "result": f'%{tmp}'})
            return f'%{tmp}'


        elif type(e) == UnOpExpr:
            value = self.processExpression(e.value)
            operation = self.getUnOp(e.operation)
            tmp = self._tmp_counter
            self._tmp_counter += 1
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

    def getUnOp(self, op):
        if op == '-': return "neg"
        elif op == '~': return "not"


    def getData(self):
        data = [{"proc": "@main", "body" : self.body}]
        return data