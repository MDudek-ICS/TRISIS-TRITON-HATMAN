# uncompyle6 version 2.14.1
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.12 (default, Nov 19 2016, 06:48:10) 
# [GCC 5.4.0 20160609]
# Embedded file name: TsLow.pyc
# Compiled at: 2017-08-03 16:46:51
import socket, select, struct, sh, crc, TS_cnames
NvTs_err = {-1: 'UNKNOWN ERROR',
   0: 'NO ERROR',
   1: 'CONNECTION FAILURE',
   2: 'RECEIVE FAILURE',
   3: 'SEND FAILURE',
   4: 'NOT CONNECTED',
   5: 'BAD DATA',
   6: 'TIMEOUT',
   7: 'BAD TS_SIZE',
   8: 'BAD TS_CHECKSUM',
   9: 'BAD TS_CNT',
   10: 'BAD TCM_SIZE',
   11: 'BAD TCM_CHECKSUM',
   11: 'BAD REPLY_CODE'
   }

def crc16_append(packet):
    return packet + struct.pack('<H', crc.crc16(packet))


def cksum(data, init=0):
    summ = init
    for i in data:
        summ += ord(i)

    return summ & 65535


def pdict(text, num, dict):
    try:
        phr = dict[num]
        print text, hex(num), '(', num, ')', '[', phr, ']'
    except KeyError:
        print text, hex(num), '(', num, ')', '[', 'UNKNOWN', ']'


class TsLow(object):

    def __init__(self):
        self._sock = None
        self._timeout = 3
        self._uerror = 0
        self._perror = 0
        self._ldout = None
        self._ldin = None
        self._tcm_result = None
        self._ts_result = None
        self._qcnt = 0
        self._lcnt = 0
        self._exreply = 0
        return

    def udp_close(self):
        if self._sock != None:
            self._sock.close()
        self._sock = None
        return True

    def close(self):
        if self._sock != None:
            self.tcm_disconnect()
            self.udp_close()
        return True

    def detect_ip(self):
        ip_list = set()
        bc_sock = None
        try:
            bc_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            bc_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            bc_sock.settimeout(0.25)
            TS_PORT = 1502
            ping_message = '\x06\x00\x00\x00\x00\x88'
            close_message = '\x04\x00\x00\x00\x010'
            bc_sock.sendto(ping_message, ('255.255.255.255', TS_PORT))
            while True:
                try:
                    data, addr = bc_sock.recvfrom(1024)
                except:
                    break

                if data != ping_message:
                    continue
                try:
                    if addr[1] == TS_PORT:
                        ip_list.add(addr[0])
                        bc_sock.sendto(close_message, (addr[0], TS_PORT))
                except:
                    continue

        except:
            print 'exception while detect ip'

        if bc_sock != None:
            bc_sock.close()
        if len(ip_list) == 0:
            print 'no TCM found'
            return
        if len(ip_list) > 1:
            print 'more than one TCM found:'
            for ip in ip_list:
                print ip

        for ip in ip_list:
            return ip

        return

    def connect(self, address=None):
        self._uerror = -1
        if address == None:
            print 'using IP auto-detection'
            address = self.detect_ip()
        if address == None:
            self._uerror = 1
            return False
        self.close()
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self._sock.connect((address, 1502))
        except socket.error:
            self._uerror = 1

        connect_result = self.tcm_connect()
        if not connect_result:
            self.udp_close()
            return False
        return True

    def udp_send(self, data, timeout=-1):
        self._uerror = -1
        self._ldout = data
        if timeout < 0:
            timeout = self._timeout
        if self._sock == None:
            self._uerror = 4
            return False
        if data == None or len(data) == 0 or len(data) > 65000:
            self._uerror = 5
            return False
        try:
            self._sock.settimeout(timeout)
            self._sock.send(data)
        except socket.timeout:
            self._uerror = 6
            return False
        except socket.error:
            self._uerror = 2
            return False

        self._uerror = 0
        return True

    def udp_flush(self, timeout=0.1):
        flushcount = 0
        while self.udp_recv(timeout) != False:
            flushcount += 1

        return flushcount != 0

    def udp_recv(self, timeout=-1):
        self._ldin = None
        if self._sock == False:
            self._uerror = 4
            return False
        if timeout < 0:
            timeout = self._timeout
        r_data = None
        try:
            self._sock.settimeout(timeout)
            r_data = self._sock.recv(65000)
        except socket.timeout:
            self._uerror = 6
            return False
        except socket.error:
            self._uerror = 2
            return False

        self._uerror = 0
        self._ldin = r_data
        return True

    def udp_exec(self, data, timeout=-1):
        send_result = self.udp_send(data, timeout)
        if not send_result:
            return False
        return self.udp_recv(timeout)

    def udp_result(self):
        if self._uerror != 0:
            return None
        return self._ldin

    def tcm_result(self):
        if self._tcm_result != None:
            return self._tcm_result
        self._perror = -1
        data_received = self.udp_result()
        while True:
            self._tcm_result = (0, None)
            if data_received == None or len(data_received) < 6:
                print 'bad tcm size'
                self._perror = 10
                break
            type, size = struct.unpack('<HH', data_received[0:4])
            packet = data_received[4:-2]
            if len(packet) != size:
                print 'bad tcm size'
                self._perror = 10
                break
            checksum = struct.unpack('<H', data_received[-2:])[0]
            test_cksum = crc.crc16(data_received[:-2])
            if checksum != test_cksum:
                print 'bad tcm crc'
                self._perror = 11
                break
            self._perror = 0
            self._tcm_result = (type, packet)
            break

        return self._tcm_result

    def tcm_exec(self, type, data='', timeout=-1):
        self._tcm_result = None
        packet = struct.pack('<HH', type, len(data)) + data
        packet = crc16_append(packet)
        self.udp_exec(packet, timeout)
        return self.tcm_result()

    def tcm_ping(self):
        ping_result = self.tcm_exec(6)[0]
        if ping_result != 6:
            return False
        return True

    def tcm_connect(self):
        connect_result = self.tcm_exec(1)[0]
        if connect_result != 2:
            if connect_result == 7:
                print 'tcm connect err: connect limit reached'
            else:
                if connect_result == 9:
                    print 'tcm connect err: no MP active'
                else:
                    if connect_result == 10:
                        print 'tcm connect err: access denied'
            return False
        self._qcnt = 0
        return True

    def tcm_disconnect(self):
        disconnect_result = self.tcm_exec(4)[0]
        if disconnect_result != 3:
            return False
        return True

    def tcm_reconnect(self):
        disconnect_result = self.tcm_disconnect()
        connect_result = self.tcm_connect()
        return connect_result

    def ts_update_cnt(self):
        self._qcnt += 1
        if self._qcnt >= 256:
            self._qcnt = 1
        return True

    def ts_result(self):
        if self._ts_result != None:
            return self._ts_result
        self._ts_result = (-1, None, 0)
        self._perror = -1
        while True:
            tcm_reply = self.tcm_result()
            if tcm_reply[0] != 5:
                self._perror = 0
                break
            ts_packet = tcm_reply[1]
            if len(ts_packet) < 10:
                print 'bad ts size'
                self._perror = 7
                break
            dir, cid, cmd, cnt, unk, cks, siz = struct.unpack('<BBBBHHH', ts_packet[0:10])
            if cnt != self._lcnt:
                print 'bad ts cnt'
                self._perror = 9
                self.udp_flush()
                break
            if siz != len(ts_packet):
                print 'bad ts size'
                break
            packet_to_check = ts_packet[0:6] + struct.pack('<H', 0) + ts_packet[8:]
            test_cksum = cksum(packet_to_check, siz)
            if test_cksum != cks:
                print 'bad ts cksum'
                self._perror = 8
                break
            data_size = siz - 10
            reply_data = ts_packet[10:]
            errcode = 0
            if cmd == 100:
                if data_size > 0:
                    errcode = ord(reply_data[0])
                else:
                    errcode = -1
            else:
                if cmd != self._exreply and self._exreply != -1:
                    print 'unexpected reply'
                    self._perror = 12
                    break
            self._perror = 0
            self._ts_result = (errcode, reply_data, cmd)
            break

        return self._ts_result

    def ts_exec(self, (cmd, reply), data='', timeout=-1):
        self._exreply = reply
        ts_len = len(data) + 10
        unchecked = struct.pack('<HBBIH', 0, cmd, self._qcnt, 0, ts_len) + data
        sum_val = cksum(unchecked, ts_len)
        packet = unchecked[0:6] + struct.pack('<H', sum_val) + unchecked[8:]
        attempts = 0
        while attempts < 3:
            self._ts_result = None
            attempts += 1
            self._lcnt = self._qcnt
            exec_result = self.tcm_exec(5, packet, timeout)[0]
            self.ts_update_cnt()
            if exec_result == 8:
                reconnect_result = self.tcm_reconnect()
                return reconnect_result or False
                continue
            break

        return self.ts_result()

    def print_last_error(self):
        if self._uerror != 0:
            pdict('UDP Error:', self._uerror, NvTs_err)
        tcm_err = self.tcm_result()[0]
        if tcm_err >= 7:
            pdict('TCM Error ', tcm_err, TS_cnames.TS_cst)
        ts_err = self.ts_result()[0]
        if ts_err != 0:
            pdict('TS Error ', ts_err, TS_cnames.TS_names)
        if self._perror != 0:
            pdict('Parse Error:', self._perror, NvTs_err)
        print 'last data out:'
        sh.dump(self._ldout)
        print 'last data in:'
        sh.dump(self._ldin)