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

    def optimise(self):
        optimised = True
        cycles = 0
        count = 0
        while optimised and cycles < 10:
            optimised = False
            tmp = self.useless()
            count += tmp
            if tmp != 0: optimised = True
            tmp = self.coalesce()
            count += tmp
            if tmp != 0: optimised = True
            tmp = self.unreachable()
            count += tmp
            if tmp != 0: optimised = True
            count += tmp
            if tmp != 0: optimised = True
            tmp = self.jump_threadingC()
            count += tmp
            if tmp != 0: optimised = True
            tmp = self.coalesce()
            count += tmp
            cycles += 1
        return count

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
    
# ----------------  Optimisation Functions  ------------------


    def coalesce(self):
        # self.print_blocks()
        count = 0
        found = True
        while found:
            found = False
            for l1, b1 in self.blocks.items():
                if len(b1.next) != 1:
                    continue
                l2 = b1.next[0]
                b2 = self.blocks[l2]
                if len(b2.prev) != 1 or l2 == 'initial':
                    continue
                # print(f'Attempting to coalesce blocks {l1} and {l2}')
                self.aux_coalesce(l1,b1,l2,b2)
                found = True
                count += 1
                break
        return count
                
    def aux_coalesce(self,l1,b1,l2,b2):
        #Change next
        for l in b2.next:
            try:
                self.blocks[l].prev.remove(l2)
            except:
                # print(f'Issue when coalescing blocks {l1} and {l2}.')
                self.reporter.report(f'Trying to remove node {l2} from list ({self.blocks[l].prev}) of previous blocks of {l}', -1,  'Optimisation: coalescing')
            self.blocks[l].prev.append(l1)
        
            # Change label
            to_remove = [edge for edge in self.edges if edge[0] == l2 and edge[1] == l]
            for edge in to_remove:
                self.edges.append((l1, l, edge[2]))
                self.edges.remove(edge)


        b1.next = b2.next

        # Change content
        b1.content = b1.content[:-1] + b2.content
        del self.blocks[l2]

    def unreachable(self):
        count = 0
        not_visited = set([str(b) for b in self.blocks.keys()])
        stack = ['initial']

        while stack != []:
            node = stack.pop()
            not_visited.remove(node)
            stack.extend(str(n) for n in self.blocks[node].next if (str(n) in not_visited and str(n) not in stack))
        
        for l in not_visited:
            count += 1
            del self.blocks[l]

            # Modify Edges
            removable_edges = []
            for edge in self.edges:
                if edge[0] == l or edge[1] == l:
                    removable_edges.append(edge)
            for edge in removable_edges:
                self.edges.remove(edge)

        return count

    def useless(self):  # Remove Blocks consisting of only a label and an unconditional jump
        found = True
        count = 0
        while found:
            found = False
            for label, block in self.blocks.items():
                if len(block.content) == 2 and block.next != [] and label != 'initial':
                    n = self.blocks[label].next[0]
                    for prev in self.blocks[label].prev:
                        self.replace_label(self.blocks[prev], label, n)

                        # Modify Edges
                        tmp = tuple()
                        for edge in self.edges:
                            if edge[0] == prev and edge[1] == label:
                                tmp = edge
                                break
                        self.edges.remove(tmp)
                        self.edges.append((tmp[0],n,tmp[2]))

                    self.blocks[n].prev.remove(label)
                    self.blocks[n].prev.extend(block.prev)

                    found = True
                    count += 1
                    del self.blocks[label]
                    break
        return count

    def replace_label(self, block, old_l, new_l):
        for instruction in block.content:
            if instruction['opcode'][0] == 'j' and str(instruction['args'][0]) == old_l:
                instruction['args'][0] = new_l
        block.next = [l if old_l != l else new_l for l in block.next]

    def thread(self, l1, l2):
        for edge in self.edges:
            if edge[0] == l1 and edge[1] == l2:
                c1 = edge[2]
            if edge[0] == l2 and edge[2]!=True:
                c2 = edge[2]
                l3 = edge[1]

        if (c1[0]==c2[0] and c1[2]==c2[2]) or ( c1[0]==c2[2] and c1[2]==c2[0] ):
                
            if c2[1] in compatible_jmps[c1[1]][0]:      # Condition always true (always take conditional jump)
                l4 = self.blocks[l2].content[-1]['args'][0]
                del self.blocks[l2].content[-2]
                self.blocks[l2].content[-1]['args']=l3
                self.blocks[l2].next = [l3]
                self.blocks[l4].prev.remove(l2)

                # modify edges
                self.edges.remove((l2,l4,True))
                self.edges.remove((l2,l3,c2))
                self.edges.append((l2,l3,True))
                return True


            if c2[1] in compatible_jmps[c1[1]][1]:  # Condition never true (never take conditional jump)
                l4 = self.blocks[l2].content[-1]['args'][0]
                # print(l1,l2,l3,l4)

                del self.blocks[l2].content[-2]
                self.blocks[l2].next = [l4]
                self.blocks[l3].prev.remove(l2)

                # modify edges
                self.edges.remove((l2,l3,c2))
                return True

    def jump_threadingC(self):
        found = True
        count = 0
        while found:
            found = False
            possible = self.find_possible_threading()
            if not possible:
                continue
            if self.thread(possible[0], possible[1]):
                count += 1
                found = True
        return count

    def find_possible_threading(self):
        # Identify potential blocks for threading
        for l1, b1 in self.blocks.items():
            for edge in self.edges:
                if edge[0] != l1 or edge[2]==True: continue

                l2 = edge[1]
                b2 = self.blocks[l2]

                if len(b2.prev) != 1 or len(b2.next)!=2: continue
                
                if check_no_change(b2,edge[2][0]) and check_no_change(b2, edge[2][2]):
                    return (l1, l2)
        return

# ----------------  Debugging Functions  ------------------

    def print_blocks(self):
        for block in self.blocks.values():
            print(block)
            print()

    def check_blocks(self):
        defined = set(self.blocks.keys())
        called = set()
        for b in self.blocks.values():
            called = called.union(set(b.next))
            called = called.union(set(b.prev))
        return called == defined
    
    def check_edges(self):
        for edge in self.edges:
            if edge[1] not in self.blocks[edge[0]].next or edge[0] not in self.blocks[edge[1]].prev:
                print("NOT GOOD:", edge)
                return False

        for label, block in self.blocks.items():
            for n in block.next:
                found = False
                for edge in self.edges:
                    if edge[0]==label and edge[1]==n:
                        found = True
                if not found:
                    print("NOT GOOD:", label, n)
                    return False
        print("ALL EDGES GOOD")


# ----------------  Helper Functions  ------------------

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
    while i != len(block.content):
        if is_const(block, i):
            if var1 == block.content[-i]['result']:
                var1 = block.content[-i]['args'][0]
                break
            elif var2 == block.content[-i]['result']:
                var2 = block.content[-i]['args'][0]
                break
        i+=1
    return (var1, comparison, var2)

def is_const(block,i):  # Check if the temporary is an int
    return block.content[-i]['opcode'] == 'const' and type(block.content[-i]['args'][0])==int

def check_no_change(block, var):    # Check a temporary is not modified in a block
    for instruction in block.content:
        if instruction['result'] == var:
            return False
    return True