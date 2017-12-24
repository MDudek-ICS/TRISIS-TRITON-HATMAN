# uncompyle6 version 2.14.1
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.12 (default, Nov 19 2016, 06:48:10) 
# [GCC 5.4.0 20160609]
# Embedded file name: crc.pyc
# Compiled at: 2017-06-19 19:13:07
import zlib

def crc32(buffer):
    return zlib.crc32(buffer) & 4294967295L


__author__ = 'Kotov Alaxander'
CRC16 = 0
CRC16_CCITT = 1
CRC_CCITT_XMODEM = 2
CRC16_CCITT_x1D0F = 3
CRC16_MODBUS = 4

def crc16(buffer, mode=CRC16):
    if mode == CRC16_CCITT:
        polynom = 4129
        crc16ret = 65535
    if mode == CRC16_CCITT_x1D0F:
        polynom = 4129
        crc16ret = 7439
    if mode == CRC_CCITT_XMODEM:
        polynom = 4129
        crc16ret = 0
    if mode == CRC16:
        polynom = 40961
        crc16ret = 0
    if mode == CRC16_MODBUS:
        polynom = 40961
        crc16ret = 65535
    if mode != CRC16 and mode != CRC16_MODBUS:
        for l in buffer:
            crc16ret ^= ord(l) << 8
            crc16ret &= 65535
            for i in xrange(0, 8):
                if crc16ret & 32768:
                    crc16ret = crc16ret << 1 ^ polynom
                else:
                    crc16ret = crc16ret << 1
                crc16ret &= 65535

    else:
        for l in buffer:
            crc16ret ^= ord(l)
            crc16ret &= 65535
            for i in xrange(8):
                if crc16ret & 1:
                    crc16ret = crc16ret >> 1 ^ polynom
                else:
                    crc16ret = crc16ret >> 1
                crc16ret &= 65535

    return crc16ret


POLY64REVh = 3623878656L
CRCTableh = [0] * 256
CRCTablel = [0] * 256
isInitialized = False

def CRC64(aString):
    global isInitialized
    crcl = 0
    crch = 0
    if isInitialized is not True:
        isInitialized = True
        for i in xrange(256):
            partl = i
            parth = 0L
            for j in xrange(8):
                rflag = partl & 1L
                partl >>= 1L
                if parth & 1:
                    partl |= 2147483648L
                parth >>= 1L
                if rflag:
                    parth ^= POLY64REVh

            CRCTableh[i] = parth
            CRCTablel[i] = partl

    for item in aString:
        shr = 0L
        shr = (crch & 255) << 24
        temp1h = crch >> 8L
        temp1l = crcl >> 8L | shr
        tableindex = (crcl ^ ord(item)) & 255
        crch = temp1h ^ CRCTableh[tableindex]
        crcl = temp1l ^ CRCTablel[tableindex]

    return (crch, crcl)


def CRC64digest(aString):
    return '%08X%08X' % CRC64(aString)