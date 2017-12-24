# uncompyle6 version 2.14.1
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.12 (default, Nov 19 2016, 06:48:10) 
# [GCC 5.4.0 20160609]
# Embedded file name: encodings\utf_32.pyc
# Compiled at: 2016-06-25 21:46:06
"""
Python 'utf-32' Codec
"""
import codecs, sys
encode = codecs.utf_32_encode

def decode(input, errors='strict'):
    return codecs.utf_32_decode(input, errors, True)


class IncrementalEncoder(codecs.IncrementalEncoder):

    def __init__(self, errors='strict'):
        codecs.IncrementalEncoder.__init__(self, errors)
        self.encoder = None
        return

    def encode(self, input, final=False):
        if self.encoder is None:
            result = codecs.utf_32_encode(input, self.errors)[0]
            if sys.byteorder == 'little':
                self.encoder = codecs.utf_32_le_encode
            else:
                self.encoder = codecs.utf_32_be_encode
            return result
        return self.encoder(input, self.errors)[0]

    def reset(self):
        codecs.IncrementalEncoder.reset(self)
        self.encoder = None
        return

    def getstate(self):
        if self.encoder is None:
            return 2
        return 0

    def setstate(self, state):
        if state:
            self.encoder = None
        else:
            if sys.byteorder == 'little':
                self.encoder = codecs.utf_32_le_encode
            else:
                self.encoder = codecs.utf_32_be_encode
        return


class IncrementalDecoder(codecs.BufferedIncrementalDecoder):

    def __init__(self, errors='strict'):
        codecs.BufferedIncrementalDecoder.__init__(self, errors)
        self.decoder = None
        return

    def _buffer_decode(self, input, errors, final):
        if self.decoder is None:
            output, consumed, byteorder = codecs.utf_32_ex_decode(input, errors, 0, final)
            if byteorder == -1:
                self.decoder = codecs.utf_32_le_decode
            else:
                if byteorder == 1:
                    self.decoder = codecs.utf_32_be_decode
                else:
                    if consumed >= 4:
                        raise UnicodeError('UTF-32 stream does not start with BOM')
            return (
             output, consumed)
        return self.decoder(input, self.errors, final)

    def reset(self):
        codecs.BufferedIncrementalDecoder.reset(self)
        self.decoder = None
        return

    def getstate(self):
        state = codecs.BufferedIncrementalDecoder.getstate(self)[0]
        if self.decoder is None:
            return (state, 2)
        addstate = int((sys.byteorder == 'big') != (self.decoder is codecs.utf_32_be_decode))
        return (
         state, addstate)

    def setstate(self, state):
        codecs.BufferedIncrementalDecoder.setstate(self, state)
        state = state[1]
        if state == 0:
            self.decoder = codecs.utf_32_be_decode if sys.byteorder == 'big' else codecs.utf_32_le_decode
        else:
            if state == 1:
                self.decoder = codecs.utf_32_le_decode if sys.byteorder == 'big' else codecs.utf_32_be_decode
            else:
                self.decoder = None
        return


class StreamWriter(codecs.StreamWriter):

    def __init__(self, stream, errors='strict'):
        self.encoder = None
        codecs.StreamWriter.__init__(self, stream, errors)
        return

    def reset(self):
        codecs.StreamWriter.reset(self)
        self.encoder = None
        return

    def encode(self, input, errors='strict'):
        if self.encoder is None:
            result = codecs.utf_32_encode(input, errors)
            if sys.byteorder == 'little':
                self.encoder = codecs.utf_32_le_encode
            else:
                self.encoder = codecs.utf_32_be_encode
            return result
        return self.encoder(input, errors)
        return


class StreamReader(codecs.StreamReader):

    def reset(self):
        codecs.StreamReader.reset(self)
        try:
            del self.decode
        except AttributeError:
            pass

    def decode(self, input, errors='strict'):
        object, consumed, byteorder = codecs.utf_32_ex_decode(input, errors, 0, False)
        if byteorder == -1:
            self.decode = codecs.utf_32_le_decode
        else:
            if byteorder == 1:
                self.decode = codecs.utf_32_be_decode
            else:
                if consumed >= 4:
                    raise UnicodeError, 'UTF-32 stream does not start with BOM'
        return (
         object, consumed)


def getregentry():
    return codecs.CodecInfo(name='utf-32', encode=encode, decode=decode, incrementalencoder=IncrementalEncoder, incrementaldecoder=IncrementalDecoder, streamreader=StreamReader, streamwriter=StreamWriter)