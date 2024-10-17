#!/usr/bin/env python3

compatible_jmps = {
    'jl': (['jl','jnz','jle'], ['jg','jz','jge']),
    'jg': (['jg','jnz','jge'],['jl','jz','jle']),
    'jle': (['jle'],['jg']),
    'jge': (['jge'],['jl']),
    'jz': (['jz','jge','jle'],['jnz','jl','jg']),
    'jnz': (['jnz','jg','jl'], ['jz']),
}

class Block:
    def __init__(self, content, label):
        self.content = content
        self.next = []
        self.prev = []
        self.label = label

    def __str__(self):
        s = f'Label: {self.label} \nContent: \n'
        for i in self.content:
            s += str(i) + '\n'
        s += 'Next:' + str(self.next) + '\n'
        s += 'Prev:' + str(self.prev)
        return s

class CFG:
    def __init__(self, reporter):
        self.blocks = {}
        self.edges = []     # List of DIRECTED LABELED edges. Edge: (Label origin, Label destination, Condition) with Condition: (var1, comparison, var2) | True
        self.label_counter = 0
        self.reporter = reporter

    def new_label(self):
        self.label_counter += 1
        return f'b{self.label_counter - 1}'

    def bbinference(self, tac):
        first = ''
        if len(tac) == 0 or tac[0]['opcode'] != 'label':
            tac.insert(0, {'opcode': 'label', 'args': ['initial'], 'result': None})
        else:
            first = tac[0]['args'][0]
            tac[0]['args'] = ['initial']
        prev = ''
        label = 'initial'
        for i in range(len(tac)):
            if first != '':
                if tac[i]['opcode'][0] == 'j' and first in tac[i]['args']: 
                    tac[i]['args'][tac[i]['args'].index(first)] = 'initial'
            if tac[i]['opcode'] == 'jmp':
                self.blocks[label].content.append(tac[i])
                if (i + 1 < len(tac)) and tac[i + 1]['opcode'] != 'label':
                    prev = label
                    label = f'b{self.label_counter}'
                    self.blocks[label] = Block([{'opcode': 'label', 'args': [label], 'result': None}], label)
                    self.label_counter += 1

            elif tac[i]['opcode'][0] == 'j':
                self.blocks[label].content.append(tac[i])
                if (i + 1 < len(tac)) and tac[i + 1]['opcode'] != 'label':
                    prev = label
                    label = f'b{self.label_counter}'
                    self.blocks[label] = Block([{'opcode': 'label', 'args': [label], 'result': None}], label)
                    self.label_counter += 1
                    self.blocks[prev].content.append({'opcode': 'jmp', 'args': [label], 'result': None})
                else:
                    prev = label
                    label = str(tac[i + 1]['args'][0])

            elif tac[i]['opcode'] == 'label':
                prev = label
                label = str(tac[i]['args'][0])
                if i != 0 and self.blocks[prev].content[-1]['opcode'] not in ['jmp','ret']:
                    self.blocks[prev].content.append({'opcode': 'jmp', 'args': [label], 'result': None})
                self.blocks[label] = Block([tac[i]] , label)

            else:
                self.blocks[label].content.append(tac[i])
        if self.blocks[label].content[-1]['opcode'] not in ['jmp', 'ret']:
            self.blocks[label].content.append({'opcode': 'ret', 'args': [], 'result': None})

    def build_graph(self):
        for label, block in self.blocks.items():
            i = 1
            while block.content[-i]['opcode'][0] == 'j':
                condition = get_condition(block, i)
                tmp = str(block.content[-i]['args'][0])
                block.next.append(tmp)
                self.blocks[tmp].prev.append(label)
                self.edges.append((label, tmp, condition))
                i += 1
        # print(self.edges)

    def serialise(self):
        current = 'initial'
        result = []
        labels = [str(l) for l in self.blocks.keys()]
        schedule = ['initial']
        result += self.blocks[current].content
        if self.blocks['initial'].content[-1]['opcode'][0] == 'j':
            next = [str(self.blocks['initial'].content[-1]['args'][0])]
        while set(schedule) != set(labels):
            if current in schedule:
                for l in labels:
                    if l not in schedule:
                        current = l
                        break
            while next != []:
                
                if current!='initial':
                    result += self.blocks[current].content
                    schedule.append(current)
                if self.blocks[current].content[-1]['opcode'][0] == 'j':
                    l   = str(self.blocks[current].content[-1]['args'][0])
                if l not in schedule:
                    current = l
                else:
                    for l in self.blocks[current].next:
                        if l not in schedule:
                            current = l
                            break
                    break
        return [{"proc": "@main", "body" : result}]
    
    def coalesce(self):
        count = 0
        # self.print_blocks()
        found = True
        while found:
            found = False
            for b1 in self.blocks.values():
                if len(b1.next) == 1 and b1.next[0] != 'initial':
                    try:
                        b2 = self.blocks[b1.next[0]]
                    except:
                        self.reporter.report(f'Trying to access a block that is not in dictionary',-1, 'Optimisation: Coalesce')
    
                    if len(b2.prev) == 1 and b2.prev[0] == b1.label:
                        found = True
                        count +=1
                        # print('want:', b1.next, b2.prev)
                        content = b1.content[:-1] + b2.content
                        # print('b1', b1.content)
                        # print('b2',b2.content)
                        # print()
                        # print('b',content)
                        label = b1.label
                        b = Block(content, label)
                        b.next = b2.next
                        b.prev = b1.prev
                        # print(f'Coalescing {b1.label} and {b2.label}')
                        del self.blocks[b2.label]
                        del self.blocks[b1.label]
                        self.blocks[b1.label] = b

                        # Modify edges

                        self.edges.remove((b1.label, b2.label, True))

                        break
        # print(f'Coalesced {count} blocks')

    def unreachable(self):
        count = 0
        not_visited = set([b for b in self.blocks.keys()])
        stack = ['initial']
        while stack != []:
            node = stack.pop()
            try:
                not_visited.remove(node)
            except:
                self.reporter.report(f'Trying to remove node that is not in list', -1, 'Optimisation: Unreachable')
            stack.extend(n for n in self.blocks[node].next if n in not_visited)
        
        for l in not_visited:
            # print(f'Removing {b} unreachable')
            count += 1
            del self.blocks[l]


            # Modify Edges

            removable_edges = []
            for edge in self.edges:
                if edge[0] == l or edge[1] == l:
                    removable_edges.append(edge)
            for edge in removable_edges:
                self.edges.remove(edge)
        # print(f'Removed {count} unreached blocks')

    def thread(self, l1, l2):
        for edge in self.edges:
            if edge[0] == l1 and edge[1] == l2:
                c1 = edge[2]
            if edge[0] == l2 and edge[2]!=True:
                c2 = edge[2]
                l3 = edge[1]

        if c1[0]==c2[0] and c1[2]==c2[2]:
            if type(c1[2])==int:
                const = c1[2]
                var = c1[0]
            elif type(c1[0])== int:
                const = c1[0]
                var = c1[2]
            else:
                # print(("HELP1"))
                return
        elif c1[0]==c2[2] and c1[2]==c2[0]:
            if type(c1[2])==int:
                const = c1[2]
                var = c1[0]
            elif type(c1[0])== int:
                const = c1[0]
                var = c1[2]
            else:
                # print("HELP2")
                return
        else:
            # print("HELP3:", c1, c2)
            return
        # print("ALMOST THERE:", c1, c2)
        if c2[1] in compatible_jmps[c1[1]][0]:      # Condition always true (always take conditional jump)
            l4 = self.blocks[l2].content[-1]['args'][0]
            del self.blocks[l2].content[-2]
            # print(l1,l2,l3,l4)
            self.blocks[l2].content[-1]['args']=l3
            self.blocks[l2].next = [l3]
            self.blocks[l4].prev.remove(l2)

            # modify edges
            self.edges.remove((l2,l4,True))
            self.edges.remove((l2,l3,c2))
            self.edges.append((l2,l3,True))
            # print("THREADED A JUMP!!!")
            return True



        if c2[1] in compatible_jmps[c1[1]][1]:  # Condition never true (never take conditional jump)
            l4 = self.blocks[l2].content[-1]['args'][0]
            # print(l1,l2,l3,l4)

            del self.blocks[l2].content[-2]
            self.blocks[l2].next = [l4]
            self.blocks[l3].prev.remove(l2)

            # modify edges
            self.edges.remove((l2,l3,c2))
            # print("THREADED A JUMP!!!")
            return True

    def jump_threadingC(self):
        found = True
        count = 0
        while found:
            found = False
            possible = self.find_possible_threading()
            # print(possible)
            if not possible:
                continue
            # print('HELP')
            if self.thread(possible[0], possible[1]):
                found = True
            
        # print(f'Threaded {count} conditional jumps')

    def find_possible_threading(self):
        # print("HELP:", self.edges)
        for l1, b1 in self.blocks.items():
            # print("CRY:", l1)
            for edge in self.edges:
                # print("CRY MORE:", edge)
                if edge[0] != l1 or edge[2]==True:
                    continue
                # print("CRY1")
                if not (type(edge[2][0]) == int or type(edge[2][2]) == int):
                    continue
                # print("CRY2")
                if type(edge[2][0])==int: var = edge[2][2]
                else: var = edge[2][0]
                l2 = edge[1]
                b2 = self.blocks[l2]
                # print("CRY3")
                if len(b2.prev) != 1 or len(b2.next)!=2:
                    continue
                # print("CRY4")
                if check_no_change(b2,var):
                    return (l1, l2)
        return

    def print_blocks(self):
        for block in self.blocks.values():
            print(block)
            print()


def get_condition(block, i):
    if block.content[-i]['opcode'] == 'jmp': return True
    comparison = block.content[-i]['opcode']
    i+=1
    if block.content[-i]['opcode'] == 'cmpq':
        var1 = block.content[-i]['args'][0]
        var2 = block.content[-i]['args'][1]
    else: 
        self.reporter.report(f'Cannot find a condition for a jump', -1,  'Building Graph: getting condition')
        return
    i+=1
    # print("Getting condition:",var1, var2,i)
    # print(block.content)
    while i != len(block.content):
        if is_const(block, i):
            # print("Is const", var1, var2)
            if var1 == block.content[-i]['result']:
                var1 = block.content[-i]['args'][0]
                break
            elif var2 == block.content[-i]['result']:
                var2 = block.content[-i]['args'][0]
                break

        i+=1

    return (var1, comparison, var2)

def is_const(block,i):
    return block.content[-i]['opcode'] == 'const' and type(block.content[-i]['args'][0])==int

def check_no_change(block, var):
    for instruction in block.content:
        if instruction['result'] == var:
            return False
    return True



"""
OLD CONDITIONAL JUMP THREADING:




        for b1 in self.blocks.values():
            if b1.content[-2]['opcode'] in ['jl','jnl','jle','jnle','jz','jnz']:
                condition_var = b1.content[-3]['args'][0]
            else:
                continue
            for l2 in b1.next:
                if l2 == 'initial':
                    continue
                try:
                    b2 = self.blocks[l2]
                except:
                    self.reporter.report(f'Trying to access a block that is not in dictionary', -1,  'Optimisation: Conditional Jump Threading')
                print(l2)
                if len(b2.prev) == 1 and b2.prev[0] == b1.label and b2.content[-2]['opcode'] in compatible_jmps[b1.content[-2]['opcode']]:
                    if not any(inst['opcode'] == 'copy' and inst['args'][0] == condition_var for inst in b2.content[:-2]):

                        print(f"Conditional jump threading from {b1.label} to {b2.label}")

                        found = True
                        count += 1
                        break
                if found: break
            if found: break
"""