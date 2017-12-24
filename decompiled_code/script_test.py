# uncompyle6 version 2.14.1
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.12 (default, Nov 19 2016, 06:48:10) 
# [GCC 5.4.0 20160609]
# Embedded file name: script_test.py
# Compiled at: 2017-12-23 23:02:15
import TsHi, sh, struct, time, sys

def PresetStatusField(TsApi, value):
    if len(value) != 4:
        return -1
    script_code = '\x80\x00@<\x00\x00b\x80@\x00\x80<@ \x03|\x1c\x00\x82@\x04\x00b\x80`\x00\x80<@ \x03|\x0c\x00\x82@\x18\x00B8\x1c\x00\x00H\x80\x00\x80<\x00\x01\x84`@ \x02|\x18\x00\x80@\x04\x00B8\xc4\xff\xffK' + value[2:4] + '\x80<' + value[0:2] + '\x84`\x00\x00\x82\x90\xff\xff`8\x02\x00\x00D'
    AppendResult = TsApi.SafeAppendProgramMod(script_code)
    if not AppendResult:
        return -1
    cp_info = TsApi.GetCpStatus()
    status = cp_info[40:44]
    if status != value:
        return 0
    return 1


def UploadDummyForce(TsApi):
    empty_code = '\xff\xff`8\x02\x00\x00D \x00\x80N'
    return TsApi.SafeAppendProgramMod(empty_code, True)


test = TsHi.TsHi()
connect_result = test.connect(sys.argv[1])
if not connect_result:
    print 'unable to connect!'
    exit(0)
script_result = False
do_restore = False
while True:
    try:
        data = open('inject.bin', 'rb').read()
        data = sh.chend(data)
        payload = open('imain.bin', 'rb').read()
        payload = sh.chend(payload)
        payload = payload + struct.pack('<II', len(payload) + 8, 5666970)
        data = data + struct.pack('<II', 4660, len(payload)) + payload
    except:
        print 'module file read FAILURE'
        break

    print 'setting arguments...'
    result = PresetStatusField(test, '\x01\x80\x00\x00')
    if result >= 0:
        do_restore = True
    if result != 1:
        print 'Preset failure'
        break
    print 'uploading module'
    AppendResult2 = test.SafeAppendProgramMod(data)
    if not AppendResult2:
        print 'main code write FAILED!'
        break
    try:
        limit = 0
        prevdc = 0
        prevstatus = 0
        while limit < 4096:
            parsed_info = test.GetProjectInfo()
            if parsed_info == None:
                parsed_info = test.GetProjectInfo()
            if parsed_info == None or parsed_info['valid'] != 1 or parsed_info['run'] != 0:
                print 'MP Bad State!'
                break
            status = parsed_info['fstat']
            sh.dump(status)
            istatus = struct.unpack('<I', status)[0]
            istep = istatus & 15
            ival = istatus >> 4
            if istatus == prevstatus:
                limit += 1
            else:
                limit = 0
            if istep == 1:
                cdown = ival & 65535
                print 'countdown: %d' % cdown
                if cdown > 256:
                    if prevdc > 0:
                        t_sec = int(cdown / ((prevdc - cdown) / 5.0))
                        t_min = t_sec / 60
                        t_sec -= t_min * 60
                        print 'time left = ' + str(t_min) + ' min ' + str(t_sec) + ' sec'
                    time.sleep(5)
                prevdc = cdown
            if istep == 15:
                print 'Script has stopped'
                if ival == 0:
                    script_result = True
                break
            prevstep = istep

    except:
        print 'except'

    break

if not script_result:
    print 'Script FAILED'
    print 'DebugInfo:'
    test.print_last_error()
else:
    print 'Script SUCCESS'
if do_restore:
    print 'force removing the code, no checks'
    print UploadDummyForce(test)
else:
    print 'restore not required'
test.close()
# okay decompiling script_test.py.pyc
