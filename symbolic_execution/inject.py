#!/usr/bin/env python2


import angr
import archinfo

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

proj = angr.Project("../bin/inject.bin", load_options={
    'main_opts':{
        'backend': 'blob',
        'custom_arch': archinfo.arch_ppc32.ArchPPC32(endness="Iend_BE"),
        }
    })

def hook(s):
    pass

# hook mtspr instructions
proj.hook(0x77c, hook, length=4)
proj.hook(0x784, hook, length=4)

# hook external functions
proj.hook(0x818, hook, length=4) # 0xc20 

s = proj.factory.blank_state(addr=0x3e4)
s.options.add(angr.options.BYPASS_UNSUPPORTED_SYSCALL)

simgr = proj.factory.simgr(s)
#r = simgr.explore(find=0x674)
r = simgr.explore(find=0x63c)
