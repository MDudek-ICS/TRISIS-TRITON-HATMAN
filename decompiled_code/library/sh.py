# uncompyle6 version 2.14.1
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.12 (default, Nov 19 2016, 06:48:10) 
# [GCC 5.4.0 20160609]
# Embedded file name: sh.pyc
# Compiled at: 2017-07-13 14:30:44
import sys, struct

def dump(data, text=None):
    if isinstance(text, basestring):
        if len(text) > 0:
            print text
    if not isinstance(data, basestring):
        print 'BAD DATA'
        return
    for i in xrange(0, len(data) / 16 + 1):
        seq = data[i * 16:min(i * 16 + 16, len(data))]
        hexes = (' ').join((a.encode('hex').upper() for a in seq))
        sys.stdout.write(hexes)
        for i in xrange(0, 16 - len(seq)):
            sys.stdout.write('   ')

        sys.stdout.write('  ')
        for i in xrange(0, len(seq)):
            c = seq[i]
            sr = ''
            if ord(c) < 32 or ord(c) >= 128:
                c = '.'
            sys.stdout.write(c)

        sys.stdout.write('\n')

    sys.stdout.write('\n')


def chend(data):
    if len(data) % 4 != 0:
        return None
    res = ''
    for i in range(0, len(data) / 4):
        temp = struct.unpack('<I', data[i * 4:i * 4 + 4])[0]
        res += struct.pack('>I', temp)

    return res