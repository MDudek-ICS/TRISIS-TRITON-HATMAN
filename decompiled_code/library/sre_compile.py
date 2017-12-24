# uncompyle6 version 2.14.1
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.12 (default, Nov 19 2016, 06:48:10) 
# [GCC 5.4.0 20160609]
# Embedded file name: sre_compile.pyc
# Compiled at: 2016-06-25 21:46:10
"""Internal support module for sre"""
import _sre, sys, sre_parse
from sre_constants import *
assert _sre.MAGIC == MAGIC, 'SRE module mismatch'
if _sre.CODESIZE == 2:
    MAXCODE = 65535
else:
    MAXCODE = 4294967295L
_LITERAL_CODES = set([LITERAL, NOT_LITERAL])
_REPEATING_CODES = set([REPEAT, MIN_REPEAT, MAX_REPEAT])
_SUCCESS_CODES = set([SUCCESS, FAILURE])
_ASSERT_CODES = set([ASSERT, ASSERT_NOT])
_equivalences = (
 (105, 305),
 (115, 383),
 (181, 956),
 (837, 953, 8126),
 (946, 976),
 (949, 1013),
 (952, 977),
 (954, 1008),
 (960, 982),
 (961, 1009),
 (962, 963),
 (966, 981),
 (7777, 7835))
_ignorecase_fixes = {i:tuple((j for j in t if i != j)) for t in _equivalences for i in t}

def _compile(code, pattern, flags):
    emit = code.append
    _len = len
    LITERAL_CODES = _LITERAL_CODES
    REPEATING_CODES = _REPEATING_CODES
    SUCCESS_CODES = _SUCCESS_CODES
    ASSERT_CODES = _ASSERT_CODES
    if flags & SRE_FLAG_IGNORECASE and not flags & SRE_FLAG_LOCALE and flags & SRE_FLAG_UNICODE:
        fixes = _ignorecase_fixes
    else:
        fixes = None
    for op, av in pattern:
        if op in LITERAL_CODES:
            if flags & SRE_FLAG_IGNORECASE:
                lo = _sre.getlower(av, flags)
                if fixes and lo in fixes:
                    emit(OPCODES[IN_IGNORE])
                    skip = _len(code)
                    emit(0)
                    if op is NOT_LITERAL:
                        emit(OPCODES[NEGATE])
                    for k in (lo,) + fixes[lo]:
                        emit(OPCODES[LITERAL])
                        emit(k)

                    emit(OPCODES[FAILURE])
                    code[skip] = _len(code) - skip
                else:
                    emit(OPCODES[OP_IGNORE[op]])
                    emit(lo)
            else:
                emit(OPCODES[op])
                emit(av)
        elif op is IN:
            if flags & SRE_FLAG_IGNORECASE:
                emit(OPCODES[OP_IGNORE[op]])

                def fixup(literal, flags=flags):
                    return _sre.getlower(literal, flags)

            else:
                emit(OPCODES[op])
                fixup = None
            skip = _len(code)
            emit(0)
            _compile_charset(av, flags, code, fixup, fixes)
            code[skip] = _len(code) - skip
        elif op is ANY:
            if flags & SRE_FLAG_DOTALL:
                emit(OPCODES[ANY_ALL])
            else:
                emit(OPCODES[ANY])
        elif op in REPEATING_CODES:
            if flags & SRE_FLAG_TEMPLATE:
                raise error, 'internal: unsupported template operator'
                emit(OPCODES[REPEAT])
                skip = _len(code)
                emit(0)
                emit(av[0])
                emit(av[1])
                _compile(code, av[2], flags)
                emit(OPCODES[SUCCESS])
                code[skip] = _len(code) - skip
            elif _simple(av) and op is not REPEAT:
                if op is MAX_REPEAT:
                    emit(OPCODES[REPEAT_ONE])
                else:
                    emit(OPCODES[MIN_REPEAT_ONE])
                skip = _len(code)
                emit(0)
                emit(av[0])
                emit(av[1])
                _compile(code, av[2], flags)
                emit(OPCODES[SUCCESS])
                code[skip] = _len(code) - skip
            else:
                emit(OPCODES[REPEAT])
                skip = _len(code)
                emit(0)
                emit(av[0])
                emit(av[1])
                _compile(code, av[2], flags)
                code[skip] = _len(code) - skip
                if op is MAX_REPEAT:
                    emit(OPCODES[MAX_UNTIL])
                else:
                    emit(OPCODES[MIN_UNTIL])
        elif op is SUBPATTERN:
            if av[0]:
                emit(OPCODES[MARK])
                emit((av[0] - 1) * 2)
            _compile(code, av[1], flags)
            if av[0]:
                emit(OPCODES[MARK])
                emit((av[0] - 1) * 2 + 1)
        elif op in SUCCESS_CODES:
            emit(OPCODES[op])
        elif op in ASSERT_CODES:
            emit(OPCODES[op])
            skip = _len(code)
            emit(0)
            if av[0] >= 0:
                emit(0)
            else:
                lo, hi = av[1].getwidth()
                if lo != hi:
                    raise error, 'look-behind requires fixed-width pattern'
                emit(lo)
            _compile(code, av[1], flags)
            emit(OPCODES[SUCCESS])
            code[skip] = _len(code) - skip
        elif op is CALL:
            emit(OPCODES[op])
            skip = _len(code)
            emit(0)
            _compile(code, av, flags)
            emit(OPCODES[SUCCESS])
            code[skip] = _len(code) - skip
        elif op is AT:
            emit(OPCODES[op])
            if flags & SRE_FLAG_MULTILINE:
                av = AT_MULTILINE.get(av, av)
            if flags & SRE_FLAG_LOCALE:
                av = AT_LOCALE.get(av, av)
            else:
                if flags & SRE_FLAG_UNICODE:
                    av = AT_UNICODE.get(av, av)
            emit(ATCODES[av])
        elif op is BRANCH:
            emit(OPCODES[op])
            tail = []
            tailappend = tail.append
            for av in av[1]:
                skip = _len(code)
                emit(0)
                _compile(code, av, flags)
                emit(OPCODES[JUMP])
                tailappend(_len(code))
                emit(0)
                code[skip] = _len(code) - skip

            emit(0)
            for tail in tail:
                code[tail] = _len(code) - tail

        elif op is CATEGORY:
            emit(OPCODES[op])
            if flags & SRE_FLAG_LOCALE:
                av = CH_LOCALE[av]
            else:
                if flags & SRE_FLAG_UNICODE:
                    av = CH_UNICODE[av]
            emit(CHCODES[av])
        elif op is GROUPREF:
            if flags & SRE_FLAG_IGNORECASE:
                emit(OPCODES[OP_IGNORE[op]])
            else:
                emit(OPCODES[op])
            emit(av - 1)
        elif op is GROUPREF_EXISTS:
            emit(OPCODES[op])
            emit(av[0] - 1)
            skipyes = _len(code)
            emit(0)
            _compile(code, av[1], flags)
            if av[2]:
                emit(OPCODES[JUMP])
                skipno = _len(code)
                emit(0)
                code[skipyes] = _len(code) - skipyes + 1
                _compile(code, av[2], flags)
                code[skipno] = _len(code) - skipno
            else:
                code[skipyes] = _len(code) - skipyes + 1
        else:
            raise ValueError, ('unsupported operand type', op)

    return


def _compile_charset--- This code section failed: ---

 230       0  LOAD_FAST             2  'code'
           3  LOAD_ATTR             0  'append'
           6  STORE_FAST            5  'emit'

 231       9  SETUP_LOOP          292  'to 304'
          12  LOAD_GLOBAL           1  '_optimize_charset'
          15  LOAD_FAST             0  'charset'
          18  LOAD_FAST             3  'fixup'
          21  LOAD_FAST             4  'fixes'

 232      24  LOAD_FAST             1  'flags'
          27  LOAD_GLOBAL           2  'SRE_FLAG_UNICODE'
          30  BINARY_AND       
          31  CALL_FUNCTION_4       4 
          34  GET_ITER         
          35  FOR_ITER            265  'to 303'
          38  UNPACK_SEQUENCE_2     2 
          41  STORE_FAST            6  'op'
          44  STORE_FAST            7  'av'

 233      47  LOAD_FAST             5  'emit'
          50  LOAD_GLOBAL           3  'OPCODES'
          53  LOAD_FAST             6  'op'
          56  BINARY_SUBSCR    
          57  CALL_FUNCTION_1       1 
          60  POP_TOP          

 234      61  LOAD_FAST             6  'op'
          64  LOAD_GLOBAL           4  'NEGATE'
          67  COMPARE_OP            8  'is'
          70  POP_JUMP_IF_FALSE    76  'to 76'

 235      73  CONTINUE             35  'to 35'

 236      76  LOAD_FAST             6  'op'
          79  LOAD_GLOBAL           5  'LITERAL'
          82  COMPARE_OP            8  'is'
          85  POP_JUMP_IF_FALSE   101  'to 101'

 237      88  LOAD_FAST             5  'emit'
          91  LOAD_FAST             7  'av'
          94  CALL_FUNCTION_1       1 
          97  POP_TOP          
          98  JUMP_BACK            35  'to 35'

 238     101  LOAD_FAST             6  'op'
         104  LOAD_GLOBAL           6  'RANGE'
         107  COMPARE_OP            8  'is'
         110  POP_JUMP_IF_FALSE   144  'to 144'

 239     113  LOAD_FAST             5  'emit'
         116  LOAD_FAST             7  'av'
         119  LOAD_CONST            1  ''
         122  BINARY_SUBSCR    
         123  CALL_FUNCTION_1       1 
         126  POP_TOP          

 240     127  LOAD_FAST             5  'emit'
         130  LOAD_FAST             7  'av'
         133  LOAD_CONST            2  1
         136  BINARY_SUBSCR    
         137  CALL_FUNCTION_1       1 
         140  POP_TOP          
         141  JUMP_BACK            35  'to 35'

 241     144  LOAD_FAST             6  'op'
         147  LOAD_GLOBAL           7  'CHARSET'
         150  COMPARE_OP            8  'is'
         153  POP_JUMP_IF_FALSE   172  'to 172'

 242     156  LOAD_FAST             2  'code'
         159  LOAD_ATTR             8  'extend'
         162  LOAD_FAST             7  'av'
         165  CALL_FUNCTION_1       1 
         168  POP_TOP          
         169  JUMP_BACK            35  'to 35'

 243     172  LOAD_FAST             6  'op'
         175  LOAD_GLOBAL           9  'BIGCHARSET'
         178  COMPARE_OP            8  'is'
         181  POP_JUMP_IF_FALSE   200  'to 200'

 244     184  LOAD_FAST             2  'code'
         187  LOAD_ATTR             8  'extend'
         190  LOAD_FAST             7  'av'
         193  CALL_FUNCTION_1       1 
         196  POP_TOP          
         197  JUMP_BACK            35  'to 35'

 245     200  LOAD_FAST             6  'op'
         203  LOAD_GLOBAL          10  'CATEGORY'
         206  COMPARE_OP            8  'is'
         209  POP_JUMP_IF_FALSE   291  'to 291'

 246     212  LOAD_FAST             1  'flags'
         215  LOAD_GLOBAL          11  'SRE_FLAG_LOCALE'
         218  BINARY_AND       
         219  POP_JUMP_IF_FALSE   243  'to 243'

 247     222  LOAD_FAST             5  'emit'
         225  LOAD_GLOBAL          12  'CHCODES'
         228  LOAD_GLOBAL          13  'CH_LOCALE'
         231  LOAD_FAST             7  'av'
         234  BINARY_SUBSCR    
         235  BINARY_SUBSCR    
         236  CALL_FUNCTION_1       1 
         239  POP_TOP          
         240  JUMP_ABSOLUTE       300  'to 300'

 248     243  LOAD_FAST             1  'flags'
         246  LOAD_GLOBAL           2  'SRE_FLAG_UNICODE'
         249  BINARY_AND       
         250  POP_JUMP_IF_FALSE   274  'to 274'

 249     253  LOAD_FAST             5  'emit'
         256  LOAD_GLOBAL          12  'CHCODES'
         259  LOAD_GLOBAL          14  'CH_UNICODE'
         262  LOAD_FAST             7  'av'
         265  BINARY_SUBSCR    
         266  BINARY_SUBSCR    
         267  CALL_FUNCTION_1       1 
         270  POP_TOP          
         271  JUMP_ABSOLUTE       300  'to 300'

 251     274  LOAD_FAST             5  'emit'
         277  LOAD_GLOBAL          12  'CHCODES'
         280  LOAD_FAST             7  'av'
         283  BINARY_SUBSCR    
         284  CALL_FUNCTION_1       1 
         287  POP_TOP          
         288  JUMP_BACK            35  'to 35'

 253     291  LOAD_GLOBAL          15  'error'
         294  LOAD_CONST            3  'internal: unsupported set operator'
         297  RAISE_VARARGS_2       2 
         300  JUMP_BACK            35  'to 35'
         303  POP_BLOCK        
       304_0  COME_FROM                '9'

 254     304  LOAD_FAST             5  'emit'
         307  LOAD_GLOBAL           3  'OPCODES'
         310  LOAD_GLOBAL          16  'FAILURE'
         313  BINARY_SUBSCR    
         314  CALL_FUNCTION_1       1 
         317  POP_TOP          

Parse error at or near `JUMP_BACK' instruction at offset 300


def _optimize_charset(charset, fixup, fixes, isunicode):
    out = []
    tail = []
    charmap = bytearray(256)
    for op, av in charset:
        while True:
            try:
                if op is LITERAL:
                    if fixup:
                        i = fixup(av)
                        charmap[i] = 1
                        if fixes and i in fixes:
                            for k in fixes[i]:
                                charmap[k] = 1

                    else:
                        charmap[av] = 1
                else:
                    if op is RANGE:
                        r = range(av[0], av[1] + 1)
                        if fixup:
                            r = map(fixup, r)
                        if fixup and fixes:
                            for i in r:
                                charmap[i] = 1
                                if i in fixes:
                                    for k in fixes[i]:
                                        charmap[k] = 1

                        else:
                            for i in r:
                                charmap[i] = 1

                    else:
                        if op is NEGATE:
                            out.append((op, av))
                        else:
                            tail.append((op, av))
            except IndexError:
                if len(charmap) == 256:
                    charmap += '\x00' * 65280
                    continue
                if fixup and isunicode and op is RANGE:
                    lo, hi = av
                    ranges = [av]
                    _fixup_range(max(65536, lo), min(73727, hi), ranges, fixup)
                    for lo, hi in ranges:
                        if lo == hi:
                            tail.append((LITERAL, hi))
                        else:
                            tail.append((RANGE, (lo, hi)))

                else:
                    tail.append((op, av))

            break

    runs = []
    q = 0
    while True:
        p = charmap.find('\x01', q)
        if p < 0:
            break
        if len(runs) >= 2:
            runs = None
            break
        q = charmap.find('\x00', p)
        if q < 0:
            runs.append((p, len(charmap)))
            break
        runs.append((p, q))

    if runs is not None:
        for p, q in runs:
            if q - p == 1:
                out.append((LITERAL, p))
            else:
                out.append((RANGE, (p, q - 1)))

        out += tail
        if fixup or len(out) < len(charset):
            return out
        return charset
    if len(charmap) == 256:
        data = _mk_bitmap(charmap)
        out.append((CHARSET, data))
        out += tail
        return out
    charmap = bytes(charmap)
    comps = {}
    mapping = bytearray(256)
    block = 0
    data = bytearray()
    for i in range(0, 65536, 256):
        chunk = charmap[i:i + 256]
        if chunk in comps:
            mapping[i // 256] = comps[chunk]
        else:
            mapping[i // 256] = comps[chunk] = block
            block += 1
            data += chunk

    data = _mk_bitmap(data)
    data[0:0] = [block] + _bytes_to_codes(mapping)
    out.append((BIGCHARSET, data))
    out += tail
    return out


def _fixup_range(lo, hi, ranges, fixup):
    for i in map(fixup, range(lo, hi + 1)):
        for k, (lo, hi) in enumerate(ranges):
            if i < lo:
                if l == lo - 1:
                    ranges[k] = (
                     i, hi)
                else:
                    ranges.insert(k, (i, i))
                break
            elif i > hi:
                if i == hi + 1:
                    ranges[k] = (
                     lo, i)
                    break
            else:
                break
        else:
            ranges.append((i, i))


_CODEBITS = _sre.CODESIZE * 8
_BITS_TRANS = '0' + '1' * 255

def _mk_bitmap(bits, _CODEBITS=_CODEBITS, _int=int):
    s = bytes(bits).translate(_BITS_TRANS)[::-1]
    return [ _int(s[i - _CODEBITS:i], 2) for i in range(len(s), 0, -_CODEBITS)
           ]


def _bytes_to_codes(b):
    import array
    if _sre.CODESIZE == 2:
        code = 'H'
    else:
        code = 'I'
    a = array.array(code, bytes(b))
    assert a.itemsize == _sre.CODESIZE
    assert len(a) * a.itemsize == len(b)
    return a.tolist()


def _simple(av):
    lo, hi = av[2].getwidth()
    return lo == hi == 1 and av[2][0][0] != SUBPATTERN


def _compile_info(code, pattern, flags):
    lo, hi = pattern.getwidth()
    if lo == 0:
        return
    prefix = []
    prefixappend = prefix.append
    prefix_skip = 0
    charset = []
    charsetappend = charset.append
    if not flags & SRE_FLAG_IGNORECASE:
        for op, av in pattern.data:
            if op is LITERAL:
                if len(prefix) == prefix_skip:
                    prefix_skip = prefix_skip + 1
                prefixappend(av)
            elif op is SUBPATTERN and len(av[1]) == 1:
                op, av = av[1][0]
                if op is LITERAL:
                    prefixappend(av)
                else:
                    break
            else:
                break

        if not prefix and pattern.data:
            op, av = pattern.data[0]
            if op is SUBPATTERN and av[1]:
                op, av = av[1][0]
                if op is LITERAL:
                    charsetappend((op, av))
                elif op is BRANCH:
                    c = []
                    cappend = c.append
                    for p in av[1]:
                        if not p:
                            break
                        op, av = p[0]
                        if op is LITERAL:
                            cappend((op, av))
                        else:
                            break
                    else:
                        charset = c

            elif op is BRANCH:
                c = []
                cappend = c.append
                for p in av[1]:
                    if not p:
                        break
                    op, av = p[0]
                    if op is LITERAL:
                        cappend((op, av))
                    else:
                        break
                else:
                    charset = c

            elif op is IN:
                charset = av
    emit = code.append
    emit(OPCODES[INFO])
    skip = len(code)
    emit(0)
    mask = 0
    if prefix:
        mask = SRE_INFO_PREFIX
        if len(prefix) == prefix_skip == len(pattern.data):
            mask = mask + SRE_INFO_LITERAL
    else:
        if charset:
            mask = mask + SRE_INFO_CHARSET
    emit(mask)
    if lo < MAXCODE:
        emit(lo)
    else:
        emit(MAXCODE)
        prefix = prefix[:MAXCODE]
    if hi < MAXCODE:
        emit(hi)
    else:
        emit(0)
    if prefix:
        emit(len(prefix))
        emit(prefix_skip)
        code.extend(prefix)
        table = [
         -1] + [0] * len(prefix)
        for i in xrange(len(prefix)):
            table[i + 1] = table[i] + 1
            while table[i + 1] > 0 and prefix[i] != prefix[table[i + 1] - 1]:
                table[i + 1] = table[table[i + 1] - 1] + 1

        code.extend(table[1:])
    else:
        if charset:
            _compile_charset(charset, flags, code)
    code[skip] = len(code) - skip


try:
    unicode
except NameError:
    STRING_TYPES = (
     type(''),)
else:
    STRING_TYPES = (
     type(''), type(unicode('')))

def isstring(obj):
    for tp in STRING_TYPES:
        if isinstance(obj, tp):
            return 1

    return 0


def _code(p, flags):
    flags = p.pattern.flags | flags
    code = []
    _compile_info(code, p, flags)
    _compile(code, p.data, flags)
    code.append(OPCODES[SUCCESS])
    return code


def compile(p, flags=0):
    if isstring(p):
        pattern = p
        p = sre_parse.parse(p, flags)
    else:
        pattern = None
    code = _code(p, flags)
    if p.pattern.groups > 100:
        raise AssertionError('sorry, but this version only supports 100 named groups')
    groupindex = p.pattern.groupdict
    indexgroup = [None] * p.pattern.groups
    for k, i in groupindex.items():
        indexgroup[i] = k

    return _sre.compile(pattern, flags | p.pattern.flags, code, p.pattern.groups - 1, groupindex, indexgroup)