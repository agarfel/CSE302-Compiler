#! /usr/bin/env python3

import abc
import dataclasses as dc


@dc.dataclass
class AST(abc.ABC):
    pass

@dc.dataclass
class Expr(AST):
    line: int
    ty : str

@dc.dataclass
class Statement(AST):
    line: int

@dc.dataclass
class Block(Statement):
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
class Bool(Expr):
    value: str

@dc.dataclass
class VarDecl(Statement):
    name: str
    ty: str
    value: Expr

@dc.dataclass
class Assign(Statement):
    name: str
    value: Expr

@dc.dataclass
class Print(Statement):
    value: Expr

@dc.dataclass
class Block(Statement):
    statements: list[Statement]
    
@dc.dataclass
class Ifelse(Statement):
    condition: Expr
    ifbranch: Block
    elsebranch: Block

@dc.dataclass
class While(Statement):
    condition: Expr
    block: Block

@dc.dataclass
class Jump(Statement):
    type: str