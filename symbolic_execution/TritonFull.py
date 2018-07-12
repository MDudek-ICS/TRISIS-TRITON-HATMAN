#!/usr/bin/env python2

import struct
import angr
import cle
from claripy import BVS
import archinfo
from networkx import DiGraph
from networkx.drawing.nx_pydot import write_dot
from io import BytesIO
import archinfo
import time
def load_bins(inject, imain):
    data = open(inject, 'rb').read()
    #data = chend(data)
    payload = open(imain, 'rb').read()
    #payload = chend(payload)
    payload = payload + struct.pack('>II', len(payload) + 8, 5666970)
    data = data + struct.pack('>II', 4660, len(payload)) + payload
    return BytesIO(data)

BASE = 0x10000000


#added for syscall number tracing in the 0x1000000
#START = BASE

#MainRoutine in inject.bin
START = BASE+0x678


#imain mainroutine
#START = BASE+0x844


#imain END
#END = BASE+0x894

# case 1
#END = BASE+0x6e4

# case 2
#END = BASE+0x6f8

# case 3
#END = BASE+0x70c

# case 4
#END = BASE+0x720

# case 5
END = BASE+0x748

#check syscall 
#END = BASE+0x498


#check second syscall in case2
#END = BASE+0x24


#check third syscall
#END = BASE+0x8

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
addrs = set()
merged_payload = load_bins('../Tribin/inject.bin', '../Tribin/imain.bin')
loader = cle.loader.Loader(merged_payload, main_opts={
        'backend': 'blob',
        'custom_arch': archinfo.arch_ppc32.ArchPPC32(endness="Iend_BE"),
        'custom_base_addr': BASE,
        'custom_entry_point': BASE
        })
proj = angr.Project(loader) 




#create buffer for Triton network-base emulator payload. Will finish it in the next variant.
#s = proj.factory.blank_state()
#s.memory.store(0x4000, 0x0123456789abcdef0123456789abcdef)
#s.memory.store(0x4000, s.solver.BVV(0xAAAABBBBCCCCDDDD, 32))
#s.memory.load(0x4004, 6)
#s.memory.load(0x4000, 4, endness=archinfo.Endness.LE)
#print 'Created buffer content is:', s.memory.load(0x4000, 8, endness=archinfo.Endness.BE)





def mem_read_hook(s):
    addr = s.inspect.mem_read_address
    if not addr.concrete:
        return
    addr = addr.args[0]
    if True or (addr&0x7ffe0000) != 0x7ffe0000:
        addrs.add(addr)
        ins_addr = s.regs.ip.args[0]
        inst = proj.factory.block(addr=ins_addr).capstone.insns[0]
        print 'Read addr=0x{:x}, value={}\t{}'.format(addr, 
                s.inspect.mem_read_expr, inst)

    if  addr == 0x199400:
        print('\x1b[6;30;42m' + 'Triconex Mem Read!' + '\x1b[0m')
        print 'Special Memory Read addr=0x{:x}, value={}\t{}'.format(addr,
                s.inspect.mem_read_expr, inst)

    if  addr == 0x19AC68:
        print('\x1b[6;30;42m' + 'Triconex Mem Read!' + '\x1b[0m')
        print 'Special Memory Read addr=0x{:x}, value={}\t{}'.format(addr,
                s.inspect.mem_read_expr, inst)

    if  addr == 0xFFB104:
        print('\x1b[6;30;42m' + 'Triconex Mem Read!' + '\x1b[0m')
        print 'Special Memory Read addr=0x{:x}, value={}\t{}'.format(addr,
                s.inspect.mem_read_expr, inst)

    if  addr == 0xFFD232:
        print('\x1b[6;30;42m' + 'Triconex Mem Read!' + '\x1b[0m')
        print 'Special Memory Read addr=0x{:x}, value={}\t{}'.format(addr,
                s.inspect.mem_read_expr, inst)

def mem_write_hook(s):
    addr = s.inspect.mem_write_address
    if not addr.concrete:
        return
    addr = addr.args[0]
    if True or (addr&0x7ffe0000) != 0x7ffe0000:
        addrs.add(addr)
        ins_addr = s.regs.ip.args[0]
        inst = proj.factory.block(addr=ins_addr).capstone.insns[0]
        print 'Write addr=0x{:x}, value={}\t{}'.format(addr,
                s.inspect.mem_write_expr, inst)

    if  addr == 0x199400:
        print('\x1b[6;30;42m' + 'Triconex Mem Write!' + '\x1b[0m')
        print 'Special Memory Read addr=0x{:x}, value={}\t{}'.format(addr,
                s.inspect.mem_write_expr, inst)

    if  addr == 0x19AC68:
        print('\x1b[6;30;42m' + 'Triconex Mem Write!' + '\x1b[0m')
        print 'Special Memory Read addr=0x{:x}, value={}\t{}'.format(addr,
                s.inspect.mem_write_expr, inst)

    if  addr == 0xFFB104:
        print('\x1b[6;30;42m' + 'Triconex Mem Write!' + '\x1b[0m')
        print 'Special Memory Read addr=0x{:x}, value={}\t{}'.format(addr,
                s.inspect.mem_write_expr, inst)

    if  addr == 0xFFD232:
        print('\x1b[6;30;42m' + 'Tirconex Mem Write!' + '\x1b[0m')
        print 'Special Memory Read addr=0x{:x}, value={}\t{}'.format(addr,
                s.inspect.mem_write_expr, inst)


def nop_hook(s):
    pass





## hook mtspr instructions
#proj.hook(0x77c, hook, length=4)
#proj.hook(0x784, hook, length=4)
#
# hook external functions
proj.hook(BASE+0x9C8, nop_hook, length=4) # 0x68f0c 
#proj.hook(0x1a0, nop_hook, length=4) # 0x68f0c

s = proj.factory.blank_state(addr=START)
mem_location = BVS('mem_199400_location', 8)
s.memory.store(0x199400, mem_location)
s.options.add(angr.options.BYPASS_UNSUPPORTED_SYSCALL)
s.options.add(angr.options.TRACK_MEMORY_ACTIONS)

s.inspect.b('mem_read', when=angr.BP_BEFORE, action=mem_read_hook)
s.inspect.b('mem_write', when=angr.BP_BEFORE, action=mem_write_hook)


simgr = proj.factory.simgr(s)
#r = simgr.explore(find=0x674)
#r = simgr.explore(find=0x16c)
#number of path to search
r = simgr.explore(find=END, num_find=4)

for save in r.found:
#added later for syscall vals
#    print r.found
#    print r.found[0]
#    save =r.found[0]
    print 'printing register r0', save.regs.r0
    print 'printing register r1', save.regs.r1
    print 'printing register r2', save.regs.r2
    print 'printing register r3', save.regs.r3


print map(hex, addrs)

