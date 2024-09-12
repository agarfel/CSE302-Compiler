#! /usr/bin/env python3

class Reporter:
    def __init__(self):
        self.error_number = 0
        self.errors = []
        self.filename = 'Unknown'

    def report(self, reason, line, file):
        self.errors.append([reason, int(line), file])
        self.error_number += 1
    
    def describe(self):
        if len(self.errors) != 0:
            print("---------------------------------------------")
            print("FILE:", self.filename)
            for error in self.errors:
                print("Error:", error[0], "on line:", error[1], "during", error[2])
                if error[1] > -1:
                    with open(self.filename, 'r') as file:
                        for i, line in enumerate(file, 1):  # Start counting from 1
                            if i == error[1]:
                                print('\t', line.strip())

            print("---------------------------------------------")
            print("TOTAL ERRORS: ", self.error_number)
            print("---------------------------------------------")

        