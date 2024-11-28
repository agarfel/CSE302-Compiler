import tac as taclib
import cfg as cfglib
import ssagen as ssagenlib
import sys
import json

# ------------------------------------------------------------------------------
# Global Dead Store Elimination (DSE)

def dead_store_elimination(cfg):
    livein, liveout = dict(), dict()
    cfglib.recompute_liveness(cfg, livein, liveout)
    found = False
    # print('# ------------------------------------------------------------------------------')

    for bl in cfg._blockmap.values():
        to_remove = []
        for i,instr in enumerate(bl.body):
            # print(instr.opcode, instr.dest, liveout[instr])
            if instr.opcode not in ['div','mod','call','param'] and instr.dest not in liveout[instr]:
                to_remove.append(i)
                # print('found')
                found = True

        # if len(to_remove) != 0:
        #     print(f'Removed {len(to_remove)} instructions: {to_remove}')
        for i in reversed(to_remove):
            bl.body.pop(i)

    cfglib.recompute_liveness(cfg, livein, liveout)
    if found:
        dead_store_elimination(cfg)




# ------------------------------------------------------------------------------
# Copy Propagation

def gcp(proc : taclib.Proc, cfg: cfglib.CFG):
    ssagenlib.crude_ssagen(proc, cfg)
    refs = {}
    for bl in cfg._blockmap.values():
        to_remove = []
        for i,instr in enumerate(bl.body):
            if type(instr.arg1) != str or type(instr.dest) != str: continue
            if instr.arg1 in refs.keys():
                instr.arg1 = refs[instr.arg1]
            if instr.arg2 in refs.keys():
                instr.arg2 = refs[instr.arg2]
            if instr.opcode == 'copy' and type(instr.arg1) == str:
                to_remove.append(i)
                refs[instr.dest] = instr.arg1
                # print("Removing: ", instr)

        for i in reversed(to_remove):
            bl.body.pop(i)

# ------------------------------------------------------------------------------
# Destructing SSA

def destruct(tac):
    phi = dict()
    for decl in tac:
        if type(decl) != taclib.Proc: continue
        for instruction in decl.body:
            if instruction.opcode != 'phi': continue
            for label, x in instruction.arg1.items():
                if label not in phi.keys():
                    phi[label]=[]
                phi[label].append((instruction.dest, x))
    found = True
    while found:
        found = False
        for decl in tac:
            if type(decl) != taclib.Proc: continue
            for i, instruction in enumerate(decl.body):
                if instruction.opcode == 'label'  and instruction.arg1 in phi.keys():
                    j = i
                    while decl.body[j].opcode not in taclib.jumps and decl.body[j].opcode != 'ret':

                        j +=1
                    for dest, arg in phi[instruction.arg1]:
                        decl.body.insert(j,taclib.Instr(dest, 'copy', [arg]))
                    del phi[instruction.arg1]
                    found = True
                    break
            if found: break
    found = True
    while found:
        found = False
        for decl in tac:
            if type(decl) != taclib.Proc: continue
            for i, instruction in enumerate(decl.body):
                if instruction.opcode != 'phi': continue
                decl.body.pop(i)
                found = True
                break
            if found: break

# ------------------------------------------------------------------------------
def run(tac):
    gvars, procs = dict(), dict()
    for decl in tac:
        if isinstance(decl, taclib.Gvar): gvars[decl.name] = decl
        else: procs[decl.name] = decl
    taclib.execute(gvars, procs, '@main', [])

def print_tac(tac):
    for decl in tac:
        print(decl)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: ./myprogram.py <filename>")
    else:
        tac = taclib.load_tac(sys.argv[1])
        # run(tac)
        # print('-------------------')
        # print_tac(tac)
        opt_tac = []

        for proc in tac:
            if type(proc) == taclib.Gvar:
                opt_tac.append(proc)
                continue
            name = proc.name
            body = proc.body
            t_args = proc.t_args
            cfg = cfglib.infer(proc)
            tmp = taclib.Proc(name, t_args, body)
            gcp(tmp, cfg)
            dead_store_elimination(cfg)
            dead_store_elimination(cfg)
            cfglib.linearize(tmp, cfg)
            opt_tac.append(tmp)
        # destruct(opt_tac)

        # print('# ------------------------------------------------------------------------------')
        print_tac(opt_tac)
        # print('# ------------------------------------------------------------------------------')
        # run(opt_tac)