#! /usr/bin/env python3

import sys

class Reporter:
    def __init__(self):
        self.error_number = 0
        self.errors = []
        self.filename = 'Unknown'
        self.stage = None

    def report(self, reason, line, file):
        self.errors.append([reason, int(line), file])
        self.error_number += 1
    
    def describe(self):
        msg = ''
        if len(self.errors) != 0:
            msg += "---------------------------------------------\n"
            msg += f'FILE: {self.filename}\n'
            msg += f'Stopped compiling in {self.stage} due to errors\n'
            for error in self.errors:
                if error[1] < 0:
                    msg += f'Error: {error[0]} during {error[2]}\n'
                else:
                    msg += f'Error: {error[0]} on line: {error[1]} during {error[2]}\n'
                if error[1] > -1:
                    with open(self.filename, 'r') as file:
                        for i, line in enumerate(file, 1):  # Start counting from 1
                            if i == error[1]:
                                msg += f'\t {line.strip()}\n'

            msg += "---------------------------------------------\n"
            msg += f'TOTAL ERRORS: {self.error_number}\n'
            msg += '----------------------------------------------\n'
            sys.exit(msg)
        