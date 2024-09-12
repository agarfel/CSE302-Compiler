#! /usr/bin/env python3

import abc
import dataclasses as dc


@dc.dataclass
class AST(abc.ABC):
    pass

@dc.dataclass
class Expr(AST):
    line: int

@dc.dataclass
class Statement(AST):
    line: int

@dc.dataclass
class Program(AST):
    statements : list[Statement]

@dc.dataclass
class VarExpr(Expr):
    name: str

@dc.dataclass
class NumberExpr(Expr):
    value: int

@dc.dataclass
class BinOpExpr(Expr):
    left: Expr
    right: Expr
    operation: str

@dc.dataclass
class UnOpExpr(Expr):
    value: Expr
    operation: str

@dc.dataclass
class VarDecl(Statement):
    name: str
    type: str
    value: Expr

@dc.dataclass
class Assign(Statement):
    name: str
    value: Expr

@dc.dataclass
class Print(Statement):
    value: Expr