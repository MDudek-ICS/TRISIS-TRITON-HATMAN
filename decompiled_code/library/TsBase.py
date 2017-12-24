# uncompyle6 version 2.14.1
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.12 (default, Nov 19 2016, 06:48:10) 
# [GCC 5.4.0 20160609]
# Embedded file name: TsBase.pyc
# Compiled at: 2017-08-03 16:52:33
import TsLow, struct, time

def ts_cut_reply(result):
    if result[0] != 0:
        return
    res_data = result[1]
    if res_data == None or len(res_data) < 2:
        return
    return res_data[2:]


def ts_nocut_reply(result):
    if result[0] != 0:
        return
    res_data = result[1]
    if res_data == None or len(res_data) == 0:
        return
    return res_data


class TsBase(TsLow.TsLow):

    def GetCpStatus(self):
        result = self.ts_exec((19, 108))
        return ts_cut_reply(result)

    def GetModuleVersions(self):
        request = struct.pack('<H', 1)
        result = self.ts_exec((54, 151), request)
        return ts_cut_reply(result)

    def UploadProgram(self, id, offset=0):
        request = struct.pack('<HHHH', id, 0, 0, offset)
        result = self.ts_exec((65, 162), request)
        return ts_cut_reply(result)

    def UploadFunction(self, id, offset=0):
        request = struct.pack('<HHHH', id, 0, 0, offset)
        result = self.ts_exec((66, 163), request)
        return ts_cut_reply(result)

    def AllocateProgram(self, id, next, full_chunks=0, offset=0, data=''):
        request = struct.pack('<HHHHH', id, next, full_chunks, offset, len(data) / 4) + data
        result = self.ts_exec((55, 153), request)
        return result[0] == 0

    def AllocateFunction(self, id, next, full_chunks, offset=0, data=''):
        request = struct.pack('<HHHHH', id, next, full_chunks, offset, len(data) / 4) + data
        result = self.ts_exec((56, 154), request)
        return result[0] == 0

    def RunProgram(self):
        result = self.ts_exec((20, 109))
        return result[0] == 0

    def HaltProgram(self):
        result = self.ts_exec((21, 110))
        return result[0] == 0

    def StartDownloadChange(self, (old_name, old_maj_ver, old_min_ver, old_ts), (new_name, new_maj_ver, new_min_ver, new_ts), func_cnt, prog_cnt):
        old_name = (old_name + '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')[0:10]
        new_name = (new_name + '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')[0:10]
        request = old_name + struct.pack('<HHIHHI', old_min_ver, old_maj_ver, old_ts, new_min_ver, new_maj_ver, new_ts) + new_name + struct.pack('<HHH', 0, func_cnt, prog_cnt)
        attempts = 0
        while attempts < 120:
            attempts += 1
            result = self.ts_exec((1, 102), request)
            if result[0] == 214:
                print 'load said bad sequence, assuming success'
                return True
            if result[0] == 233:
                print 'load is busy, attempt #' + str(attempts)
                time.sleep(5)
                continue
            break

        return result[0] == 0

    def StartDownloadAll(self, (name, maj_ver, min_ver, ts), func_cnt, prog_cnt):
        name = (name + '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')[0:10]
        request = struct.pack('<HHHI', 0, 0, 13, ts) + name + struct.pack('<HHH', func_cnt, prog_cnt, 0)
        attempts = 0
        while attempts < 120:
            attempts += 1
            result = self.ts_exec((59, 101), request)
            if result[0] == 214:
                print 'load said bad sequence, assuming success'
                return True
            if result[0] == 233:
                print 'load is busy, attempt #' + str(attempts)
                time.sleep(5)
                continue
            break

        return result[0] == 0

    def CancelDownload(self):
        result = self.ts_exec((12, 104))
        return result[0] == 0

    def EndDownloadChange(self):
        result = self.ts_exec((11, 103))
        return result[0] == 0

    def EndDownloadAll(self):
        result = self.ts_exec((10, 105))
        return result[0] == 0

    def ExecuteExploit(self, cmd, data='', mp=255):
        request = struct.pack('<BB', cmd, mp) + data
        result = self.ts_exec((29, 150), request)
        return ts_nocut_reply(result)