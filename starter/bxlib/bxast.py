#! /usr/bin/env python3

import abc
import dataclasses as dc


@dc.dataclass
class AST(abc.ABC):
    pass

@dc.dataclass
class Decl(AST):
    line: int

@dc.dataclass
class ExceptionDecl(Decl):
    name: str

@dc.dataclass
class Program(AST):
    line: int
    declarations: list[Decl]
    
@dc.dataclass   
class Ty(AST):
    line: int
    ty: str

@dc.dataclass
class Param(AST):
    line: int
    name: list[str]
    ty: Ty

@dc.dataclass
class Statement(AST):
    line: int

@dc.dataclass
class Block(Statement):
    statements : list[Statement]

@dc.dataclass
class Raise(Statement):
    name: str

@dc.dataclass
class Catch(Statement):
    name: str
    block: Block

@dc.dataclass
class TryExcept(Statement):
    block: Block
    catches: list[Catch]

@dc.dataclass
class Expr(AST):
    line: int
    ty : Ty

@dc.dataclass
class Raises(Statement):
    name: str

@dc.dataclass
class ProcDecl(Decl):
    name: str
    block: Block
    args: [Param]
    return_ty : Ty
    raises: list[Raises]

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
class VarInit(AST):
    name: str
    value: Expr
    line: int


@dc.dataclass
class VarDecl(Statement):
    var_l : list[VarInit]
    ty: Ty

@dc.dataclass
class Assign(Statement):
    name: str
    value: Expr

@dc.dataclass
class Eval(Statement):
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
    ty: str

@dc.dataclass
class Return(Statement):
    value: Expr

@dc.dataclass
class ProcCall(Expr):
    name: str
    args: [Expr]