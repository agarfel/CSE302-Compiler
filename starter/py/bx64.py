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

jumps= ['jl', 'jnl', 'jle', 'jnle', 'jz', 'jnz','jmp']

class Tox64:
    def __init__(self, reporter):
        self.temps = {}
        self.asm = []
        self.reporter = reporter

    
    def lookup_tmp(self, tmp):
        if type(tmp) != str:
            self.reporter.report(f'Temporary {tmp} has an unexpected type ({type(tmp)}). Expected str', -2, self.reporter.stage)
        if tmp[0] != '%':
            self.reporter.report(f'Temporary {tmp} has an unexpected format. Should start with %', -2, self.reporter.stage)
        if not tmp[1:].isnumeric():
            self.reporter.report(f'Temporary {tmp} has an unexpected format. Expected %(int)', -2, self.reporter.stage)
        if tmp  not in self.temps.keys():
            self.temps[tmp] = f'{-8 * (len(self.temps.keys()) + 1)}(%rbp)'

        return self.temps[tmp]

    def tac_to_asm(self, tac_instrs):
        for instr in tac_instrs:
            opcode = instr['opcode']
            args = instr['args']
            result = instr['result']

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
            elif opcode == 'print':
                self.process_print(args)
            elif opcode in jumps:
                self.process_jump(opcode, args)
            elif opcode == 'label':
                self.process_label(args)
            elif opcode == 'cmpq':
                self.process_boolop(args)
            else:
                self.reporter.report(f'Processing Intruction: unknown opcode {opcode}', -2, self.reporter.stage)
        
        stack_size = len(self.temps.keys())
        if stack_size % 2 != 0: stack_size += 1 # 16 byte alignment for x64
        self.asm[:0] = [f'pushq %rbp',
                    f'movq %rsp, %rbp',
                    f'subq ${8 * stack_size}, %rsp'] \
        #  + [f'// {tmp} in {reg}' for (tmp, reg) in temp_map.items()]
        self.asm += [f'movq %rbp, %rsp',
                    f'popq %rbp',
                    f'xorq %rax, %rax',
                    f'retq']

    def process_const(self, args, result):
        if len(args) != 1:
            self.reporter.report(f'Processing Const: expected len(args) == 1, found length {len(args)}', -2, self.reporter.stage)

        if  type(args[0]) != int:
            self.reporter.report(f'Processing Const: expected type(args[0]) == int, found type {type(args[0])}', -2, self.reporter.stage)
        result = self.lookup_tmp(result)
        self.asm.append(f'movq ${args[0]}, {result}')

    def process_copy(self, args, result):
        if len(args) != 1:
            self.reporter.report(f'Processing Copy: expected len(args) == 1, found length {len(args)}', -2, self.reporter.stage)
        arg = self.lookup_tmp(args[0])
        result = self.lookup_tmp(result)
        self.asm.append(f'movq {arg}, %r11')
        self.asm.append(f'movq %r11, {result}')

    def process_binop(self, opcode, args, result):
        if len(args) != 2:
            self.reporter.report(f'Processing Binary Operation ({opcode}): expected len(args) == 2, found length {len(args)}', -2, self.reporter.stage)
        arg1 = self.lookup_tmp(args[0])
        arg2 = self.lookup_tmp(args[1])
        result = self.lookup_tmp(result)
        op = binops[opcode]
        if type(op) == str:
            self.asm += [f'movq {arg1}, %r11',
                        f'{op} {arg2}, %r11',
                        f'movq %r11, {result}']
        else: 
            self.asm.extend(op(arg1, arg2, result))

    def process_unop(self, opcode, args, result):
        if len(args) != 1:
            self.reporter.report(f'Processing Unary Operation ({opcode}): expected len(args) == 1, found length {len(args)}', -2, self.reporter.stage)
        arg = self.lookup_tmp(args[0])
        result = self.lookup_tmp(result)
        op = unops[opcode]
        self.asm += [f'movq {arg}, %r11',
                    f'{op} %r11',
                    f'movq %r11, {result}']

    def process_print(self, args):
        arg = self.lookup_tmp(args[0])
        self.asm += [f'leaq .lprintfmt(%rip), %rdi',
                    f'movq {arg}, %rsi',
                    f'xorq %rax, %rax',
                    f'callq printf@PLT']

    def process_boolop(self, args):
        if len(args) != 2:
            self.reporter.report(f'Processing cmpq: expected len(args) == 2, found length {len(args)}', -2, self.reporter.stage)
        arg1 = self.lookup_tmp(args[0])
        arg2 = self.lookup_tmp(args[1])
        self.asm += [f'movq {arg2}, %r11']
        self.asm += [f'cmpq %r11, {arg1}']

    def process_jump(self, opcode, args):
        if len(args) != 1:
            self.reporter.report(f'Processing Jump ({opcode}): expected len(args) == 1, found length {len(args)}', -2, self.reporter.stage)
        self.asm += [f'{opcode} .L{args[0]}']

    def process_label(self, args):
        if len(args) != 1:
            self.reporter.report(f'Processing Label ({args[0]}): expected len(args) == 1, found length {len(args)}', -2, self.reporter.stage)
        self.asm += [f'.L{args[0]}:']



    def compile_tac(self, file):
        if file.endswith('.tac.json'):
            rname = file[:-9]
        elif file.endswith('.json'):
            rname = file[:-5]
        else:
            raise ValueError(f'{file} does not end in .tac.json or .json')
        tjs = None
        with open(file, 'rb') as fp:
            tjs = json.load(fp)
        assert isinstance(tjs, list) and len(tjs) == 1, tjs
        tjs = tjs[0]
        assert 'proc' in tjs and tjs['proc'] == '@main', tjs
        self.tac_to_asm(tjs['body'])
        asm = ['\t' + line for line in self.asm]
        asm[:0] = [f'\t.section .rodata',
                    f'.lprintfmt:',
                    f'\t.string "%ld\\n"',
                    f'\t.text',
                    f'\t.globl main',
                    f'main:']
        sname = rname + '.s'
        with open(sname, 'w') as afp:
            print(*asm, file=afp, sep='\n')