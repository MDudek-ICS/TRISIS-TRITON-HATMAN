#!/usr/bin/env python2


import angr
import archinfo
from networkx import DiGraph
from networkx.drawing.nx_pydot import write_dot

print''
print ''
print '######## ########  #### ########  #######  ##    ##                    '
print '   ##    ##     ##  ##     ##    ##     ## ###   ##                    '
print '   ##    ##     ##  ##     ##    ##     ## ####  ##                    '
print '   ##    ########   ##     ##    ##     ## ## ## ##                    '
print '   ##    ##   ##    ##     ##    ##     ## ##  ####                    '
print '   ##    ##    ##   ##     ##    ##     ## ##   ###                    '
print '   ##    ##     ## ####    ##     #######  ##    ##                    '
print ' ######  ##    ## ##     ## ########   #######  ##       ####  ######  '
print '##    ##  ##  ##  ###   ### ##     ## ##     ## ##        ##  ##    ## '
print '##         ####   #### #### ##     ## ##     ## ##        ##  ##       '
print ' ######     ##    ## ### ## ########  ##     ## ##        ##  ##       '
print '      ##    ##    ##     ## ##     ## ##     ## ##        ##  ##       '
print '##    ##    ##    ##     ## ##     ## ##     ## ##        ##  ##    ## '
print ' ######     ##    ##     ## ########   #######  ######## ####  ######  '
print ''
print ''
print('\x1b[6;30;42m' + '..:: TRITON Symbolic by Ali Abbasi ::..' + '\x1b[0m')

# unpack imain.7z in original_samples folder first
proj = angr.Project("../original_samples/imain.bin", load_options={
    'main_opts':{
        'backend': 'blob',
        'custom_arch': archinfo.arch_ppc32.ArchPPC32(endness="Iend_BE"),
        }
    })

def hook(s):
    pass

## hook mtspr instructions
#proj.hook(0x77c, hook, length=4)
#proj.hook(0x784, hook, length=4)
#
# hook external functions
proj.hook(0x18c, hook, length=4) # 0x68f0c 
proj.hook(0x1a0, hook, length=4) # 0x68f0c

s = proj.factory.blank_state(addr=0x0)
s.options.add(angr.options.BYPASS_UNSUPPORTED_SYSCALL)
s.options.add(angr.options.TRACK_MEMORY_ACTIONS)

simgr = proj.factory.simgr(s)
#r = simgr.explore(find=0x674)
r = simgr.explore(find=0x16c)

# get constraint for mem_199400
rr = r.found[0]
constraint = list(rr.actions)[-1]
ast = constraint.all_objects[0].ast

# crate graph out of mem_199400 constraint
def not_concrete(obj):
    return a != None and not isinstance(a, (int, long, str)) and not a.concrete

g = DiGraph()
nid = 0
worker = [ast]
p_nid = "root"
while worker:
    x = worker.pop(0)
    g.add_edge(p_nid, nid)
    p_nid = nid
    g.add_node(nid, label=x.op)
    nid+=1

    for a in x.args:
        if a is None:
            continue
        if not_concrete(a):
            worker.append(a)

        c_nid = nid
        if not not_concrete(a):
            g.add_node(nid, label=str(a))
        else:
            g.add_node(nid, label="...")
        nid+=1
        g.add_edge(p_nid, c_nid)
#writing Triton Control-Flow Graph to a dot file, change as needed
write_dot(g, "/Users/ali/Triton-Symbolic/TritonCFG.dot")

