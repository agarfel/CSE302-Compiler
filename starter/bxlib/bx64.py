#!/usr/bin/env python3
import json
import sys
import os
from pathlib import Path


binops = {'add': 'addq',
          'sub': 'subq',
          'mul': (lambda ra, rb, rd: [f'movq {ra}, %rax',
                                      f'imulq {rb}',
                                      f'movq %rax, {rd}']),
          'div': (lambda ra, rb, rd: [f'movq {ra}, %rax',
                                      f'cqto',
                                      f'idivq {rb}',
                                      f'movq %rax, {rd}']),
          'mod': (lambda ra, rb, rd: [f'movq {ra}, %rax',
                                      f'cqto',
                                      f'idivq {rb}',
                                      f'movq %rdx, {rd}']),
          'and': 'andq',
          'or': 'orq',
          'xor': 'xorq',
          'shl': (lambda ra, rb, rd: [f'movq {ra}, %r11',
                                      f'movq {rb}, %rcx',
                                      f'salq %cl, %r11',
                                      f'movq %r11, {rd}']),
          'shr': (lambda ra, rb, rd: [f'movq {ra}, %r11',
                                      f'movq {rb}, %rcx',
                                      f'sarq %cl, %r11',
                                      f'movq %r11, {rd}'])}
unops = {'neg': 'negq',
         'not': 'notq'}

jumps= ['jl', 'jg', 'jle', 'jge', 'jz', 'jnz', 'jmp']

callee_saved = {'rbx', 'rbp', 'r12', 'r13', 'r14', 'r15'}
caller_saved = {'rax', 'rcx', 'rdx', 'rdi', 'rsi', 'r8', 'r9', 'r10', 'r11'}
arg_registers = ['rdi','rsi','rdx','rcx', 'r8', 'r9']

class Tox64:
    def __init__(self, reporter):
        self.temps = {}
        self.asm = []
        self.body = []
        self.inUse = set()
        self.reporter = reporter

    
    def lookup_tmp(self, tmp):
        if type(tmp) != str:
            self.reporter.report(f'Temporary {tmp} has an unexpected type ({type(tmp)}). Expected str', -2, self.reporter.stage)
            return
        if tmp[0] == '@':
            return f'{tmp[1:]}(%rip)'
        if tmp  not in self.temps.keys():
            self.temps[tmp] = f'{-8 * (len(self.temps.keys()) + 1)}(%rbp)'
        # print(self.temps)
        return self.temps[tmp]

    def tac_to_asm(self, tac):
        for instr in tac:
            if "var" in instr.keys():
                name = instr['var']
                value = instr['init']
                self.process_globalVar(name, value)

            elif "proc" in instr.keys():
                self.process_procedure(instr)
            else:
                self.reporter.report(f'Unexpected instruction found: {instr.keys()}', -2, self.reporter.stage)
                return

    def process_procedure(self, instr):
        name = instr['proc'][1:]
        args = instr['args']
        body = instr['body']
        self.proc_tmps = 0
        self.process_body(name, args, body)
        stack_size = len(self.temps.keys())
        if stack_size % 2 != 0: stack_size += 1 # 16 byte alignment for x64
        self.asm += [
            f'.text',
            f'.globl {name}',
            f'{name}:',
            f'pushq %rbp',
            f'movq %rsp, %rbp',
            f'subq ${8*(stack_size)}, %rsp'
        ]

        for i in range(min(6, len(args))):
            self.asm += [f'movq %{arg_registers[i]}, {self.lookup_tmp(args[i])}']

        for i, arg in enumerate(args[6:]):
            self.temps[arg] = f'{8 * (i + 1)}(%rbp)'
            
        self.asm += self.body
        self.body = []
        self.temps = {}

        self.asm += [
            f'E_{name}:',
            f'movq %rbp, %rsp',
            f'popq %rbp',
            f'retq'
        ]


    def process_body(self, proc_name, proc_args, proc_body):
        for instr in proc_body:
            opcode = instr['opcode']
            args = instr['args']
            result = instr['result']
            param_calls = 0
            if opcode == 'nop':
                pass
            elif opcode == 'const':
                self.process_const(args, result)
            elif opcode == 'copy':
                self.process_copy(args, result)
            elif opcode in binops:
                self.process_binop(opcode, args, result)
            elif opcode in unops:
                self.process_unop(opcode, args, result)
            elif opcode in jumps:
                self.process_jump(opcode, args)
            elif opcode == 'label':
                self.process_label(args)
            elif opcode == 'cmpq':
                self.process_boolop(args)
            elif opcode =='ret':
                if args != []:
                    self.body += [f'movq {self.lookup_tmp(args[0])}, %rax']
                self.body += [f'jmp E_{proc_name}']
            elif opcode == 'call':
                self.process_call(args, result)
            elif opcode == 'param':
                self.process_param(args)
            else:
                self.reporter.report(f'Processing Intruction: unknown opcode {opcode}', -2, self.reporter.stage)
        


    def process_const(self, args, result):
        if len(args) != 1:
            self.reporter.report(f'Processing Const: expected len(args) == 1, found length {len(args)}', -2, self.reporter.stage)

        if  type(args[0]) != int:
            self.reporter.report(f'Processing Const: expected type(args[0]) == int, found type {type(args[0])}', -2, self.reporter.stage)
        result = self.lookup_tmp(result)
        self.body.append(f'movq ${args[0]}, {result}')

    def process_copy(self, args, result):
        if len(args) != 1:
            self.reporter.report(f'Processing Copy: expected len(args) == 1, found length {len(args)}', -2, self.reporter.stage)
        arg = self.lookup_tmp(args[0])
        result = self.lookup_tmp(result)        
        self.body.append(f'movq {arg}, %r11')
        self.body.append(f'movq %r11, {result}')

    def process_binop(self, opcode, args, result):
        if len(args) != 2:
            self.reporter.report(f'Processing Binary Operation ({opcode}): expected len(args) == 2, found length {len(args)}', -2, self.reporter.stage)
        arg1 = self.lookup_tmp(args[0])
        arg2 = self.lookup_tmp(args[1])
        result = self.lookup_tmp(result)
        op = binops[opcode]
        if type(op) == str:
            self.body += [f'movq {arg1}, %r11',
                        f'{op} {arg2}, %r11',
                        f'movq %r11, {result}']
        else: 
            self.body.extend(op(arg1, arg2, result))

    def process_unop(self, opcode, args, result):
        if len(args) != 1:
            self.reporter.report(f'Processing Unary Operation ({opcode}): expected len(args) == 1, found length {len(args)}', -2, self.reporter.stage)
        arg = self.lookup_tmp(args[0])
        result = self.lookup_tmp(result)
        op = unops[opcode]
        self.body += [f'movq {arg}, %r11',
                    f'{op} %r11',
                    f'movq %r11, {result}']

    def process_boolop(self, args):
        if len(args) != 2:
            self.reporter.report(f'Processing cmpq: expected len(args) == 2, found length {len(args)}', -2, self.reporter.stage)
        arg1 = self.lookup_tmp(args[0])
        arg2 = self.lookup_tmp(args[1])
        self.body += [f'movq {arg2}, %r11']
        self.body += [f'cmpq %r11, {arg1}']

    def process_jump(self, opcode, args):
        if len(args) != 1:
            self.reporter.report(f'Processing Jump ({opcode}): expected len(args) == 1, found length {len(args)}', -2, self.reporter.stage)
        self.body += [f'{opcode} .L{args[0]}']

    def process_label(self, args):
        if len(args) != 1:
            self.reporter.report(f'Processing Label ({args[0]}): expected len(args) == 1, found length {len(args)}', -2, self.reporter.stage)
        self.body += [f'.L{args[0]}:']

    def process_globalVar(self, name, value):
        self.asm += [f'.globl {name[1:]}']
        self.asm += [f'.data']
        self.asm += [f'{name[1:]}: .quad {value}']

    def process_call(self, args, result):
        name, num_args = args
        self.body += [f'callq {name[1:]}']
        if num_args > 6:
            self.body += [f'addq ${8*(num_args-6)}, %rsp']
        if result != None:
            self.body += [f'movq %rax, {self.lookup_tmp(result)}']

    def process_param(self, args):
        arg_num, var = args
        if arg_num <= 6:
            self.body += [f'movq {self.lookup_tmp(var)}, %{arg_registers[arg_num-1]}']
        else:
            self.body += [f'pushq {self.lookup_tmp(var)}']


    def compile_tac(self, file):
        if file.endswith('.opt.tac.json'):
            rname = file[:-13]
        elif file.endswith('.tac.json'):
            rname = file[:-9]
        elif file.endswith('.json'):
            rname = file[:-5]
        else:
            raise ValueError(f'{file} does not end in .tac.json or .json')
        tjs = None
        with open(file, 'rb') as fp:
            tjs = json.load(fp)
        assert isinstance(tjs, list), tjs
        self.tac_to_asm(tjs)
        asm = ['\t' + line for line in self.asm]
        asm[:0] = [f'\t.section .rodata',
                    f'.lprintfmt:',
                    f'\t.string "%ld\\n"']
        sname = rname + '.s'
        with open(sname, 'w') as afp:
            print(*asm, file=afp, sep='\n')
        
        sname = rname + '.x64-linux.s'
        with open(sname, 'w') as afp:
            print(*asm, file=afp, sep='\n')