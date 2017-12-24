# uncompyle6 version 2.14.1
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.12 (default, Nov 19 2016, 06:48:10) 
# [GCC 5.4.0 20160609]
# Embedded file name: textwrap.pyc
# Compiled at: 2016-06-25 21:46:20
"""Text wrapping and filling.
"""
__revision__ = '$Id$'
import string, re
try:
    _unicode = unicode
except NameError:

    class _unicode(object):
        pass


__all__ = [
 'TextWrapper', 'wrap', 'fill', 'dedent']
_whitespace = '\t\n\x0b\x0c\r '

class TextWrapper():
    """
    Object for wrapping/filling text.  The public interface consists of
    the wrap() and fill() methods; the other methods are just there for
    subclasses to override in order to tweak the default behaviour.
    If you want to completely replace the main wrapping algorithm,
    you'll probably have to override _wrap_chunks().
    
    Several instance attributes control various aspects of wrapping:
      width (default: 70)
        the maximum width of wrapped lines (unless break_long_words
        is false)
      initial_indent (default: "")
        string that will be prepended to the first line of wrapped
        output.  Counts towards the line's width.
      subsequent_indent (default: "")
        string that will be prepended to all lines save the first
        of wrapped output; also counts towards each line's width.
      expand_tabs (default: true)
        Expand tabs in input text to spaces before further processing.
        Each tab will become 1 .. 8 spaces, depending on its position in
        its line.  If false, each tab is treated as a single character.
      replace_whitespace (default: true)
        Replace all whitespace characters in the input text by spaces
        after tab expansion.  Note that if expand_tabs is false and
        replace_whitespace is true, every tab will be converted to a
        single space!
      fix_sentence_endings (default: false)
        Ensure that sentence-ending punctuation is always followed
        by two spaces.  Off by default because the algorithm is
        (unavoidably) imperfect.
      break_long_words (default: true)
        Break words longer than 'width'.  If false, those words will not
        be broken, and some lines might be longer than 'width'.
      break_on_hyphens (default: true)
        Allow breaking hyphenated words. If true, wrapping will occur
        preferably on whitespaces and right after hyphens part of
        compound words.
      drop_whitespace (default: true)
        Drop leading and trailing whitespace from lines.
    """
    whitespace_trans = string.maketrans(_whitespace, ' ' * len(_whitespace))
    unicode_whitespace_trans = {}
    uspace = ord(u' ')
    for x in map(ord, _whitespace):
        unicode_whitespace_trans[x] = uspace

    wordsep_re = re.compile('(\\s+|[^\\s\\w]*\\w+[^0-9\\W]-(?=\\w+[^0-9\\W])|(?<=[\\w\\!\\"\\\'\\&\\.\\,\\?])-{2,}(?=\\w))')
    wordsep_simple_re = re.compile('(\\s+)')
    sentence_end_re = re.compile('[%s][\\.\\!\\?][\\"\\\']?\\Z' % string.lowercase)

    def __init__(self, width=70, initial_indent='', subsequent_indent='', expand_tabs=True, replace_whitespace=True, fix_sentence_endings=False, break_long_words=True, drop_whitespace=True, break_on_hyphens=True):
        self.width = width
        self.initial_indent = initial_indent
        self.subsequent_indent = subsequent_indent
        self.expand_tabs = expand_tabs
        self.replace_whitespace = replace_whitespace
        self.fix_sentence_endings = fix_sentence_endings
        self.break_long_words = break_long_words
        self.drop_whitespace = drop_whitespace
        self.break_on_hyphens = break_on_hyphens
        self.wordsep_re_uni = re.compile(self.wordsep_re.pattern, re.U)
        self.wordsep_simple_re_uni = re.compile(self.wordsep_simple_re.pattern, re.U)

    def _munge_whitespace(self, text):
        r"""_munge_whitespace(text : string) -> string
        
        Munge whitespace in text: expand tabs and convert all other
        whitespace characters to spaces.  Eg. " foo\tbar\n\nbaz"
        becomes " foo    bar  baz".
        """
        if self.expand_tabs:
            text = text.expandtabs()
        if self.replace_whitespace:
            if isinstance(text, str):
                text = text.translate(self.whitespace_trans)
            elif isinstance(text, _unicode):
                text = text.translate(self.unicode_whitespace_trans)
        return text

    def _split(self, text):
        """_split(text : string) -> [string]
        
        Split the text to wrap into indivisible chunks.  Chunks are
        not quite the same as words; see _wrap_chunks() for full
        details.  As an example, the text
          Look, goof-ball -- use the -b option!
        breaks into the following chunks:
          'Look,', ' ', 'goof-', 'ball', ' ', '--', ' ',
          'use', ' ', 'the', ' ', '-b', ' ', 'option!'
        if break_on_hyphens is True, or in:
          'Look,', ' ', 'goof-ball', ' ', '--', ' ',
          'use', ' ', 'the', ' ', '-b', ' ', option!'
        otherwise.
        """
        if isinstance(text, _unicode):
            if self.break_on_hyphens:
                pat = self.wordsep_re_uni
            else:
                pat = self.wordsep_simple_re_uni
        else:
            if self.break_on_hyphens:
                pat = self.wordsep_re
            else:
                pat = self.wordsep_simple_re
        chunks = pat.split(text)
        chunks = filter(None, chunks)
        return chunks

    def _fix_sentence_endings(self, chunks):
        r"""_fix_sentence_endings(chunks : [string])
        
        Correct for sentence endings buried in 'chunks'.  Eg. when the
        original text contains "... foo.\nBar ...", munge_whitespace()
        and split() will convert that to [..., "foo.", " ", "Bar", ...]
        which has one too few spaces; this method simply changes the one
        space to two.
        """
        i = 0
        patsearch = self.sentence_end_re.search
        while i < len(chunks) - 1:
            if chunks[i + 1] == ' ' and patsearch(chunks[i]):
                chunks[i + 1] = '  '
                i += 2
            else:
                i += 1

    def _handle_long_word(self, reversed_chunks, cur_line, cur_len, width):
        """_handle_long_word(chunks : [string],
                             cur_line : [string],
                             cur_len : int, width : int)
        
        Handle a chunk of text (most likely a word, not whitespace) that
        is too long to fit in any line.
        """
        if width < 1:
            space_left = 1
        else:
            space_left = width - cur_len
        if self.break_long_words:
            cur_line.append(reversed_chunks[-1][:space_left])
            reversed_chunks[-1] = reversed_chunks[-1][space_left:]
        else:
            if not cur_line:
                cur_line.append(reversed_chunks.pop())

    def _wrap_chunks(self, chunks):
        """_wrap_chunks(chunks : [string]) -> [string]
        
        Wrap a sequence of text chunks and return a list of lines of
        length 'self.width' or less.  (If 'break_long_words' is false,
        some lines may be longer than this.)  Chunks correspond roughly
        to words and the whitespace between them: each chunk is
        indivisible (modulo 'break_long_words'), but a line break can
        come between any two chunks.  Chunks should not have internal
        whitespace; ie. a chunk is either all whitespace or a "word".
        Whitespace chunks will be removed from the beginning and end of
        lines, but apart from that whitespace is preserved.
        """
        lines = []
        if self.width <= 0:
            raise ValueError('invalid width %r (must be > 0)' % self.width)
        chunks.reverse()
        while chunks:
            cur_line = []
            cur_len = 0
            if lines:
                indent = self.subsequent_indent
            else:
                indent = self.initial_indent
            width = self.width - len(indent)
            if self.drop_whitespace and chunks[-1].strip() == '' and lines:
                del chunks[-1]
            while chunks:
                l = len(chunks[-1])
                if cur_len + l <= width:
                    cur_line.append(chunks.pop())
                    cur_len += l
                else:
                    break

            if chunks and len(chunks[-1]) > width:
                self._handle_long_word(chunks, cur_line, cur_len, width)
            if self.drop_whitespace and cur_line and cur_line[-1].strip() == '':
                del cur_line[-1]
            if cur_line:
                lines.append(indent + ('').join(cur_line))

        return lines

    def wrap(self, text):
        """wrap(text : string) -> [string]
        
        Reformat the single paragraph in 'text' so it fits in lines of
        no more than 'self.width' columns, and return a list of wrapped
        lines.  Tabs in 'text' are expanded with string.expandtabs(),
        and all other whitespace characters (including newline) are
        converted to space.
        """
        text = self._munge_whitespace(text)
        chunks = self._split(text)
        if self.fix_sentence_endings:
            self._fix_sentence_endings(chunks)
        return self._wrap_chunks(chunks)

    def fill(self, text):
        """fill(text : string) -> string
        
        Reformat the single paragraph in 'text' to fit in lines of no
        more than 'self.width' columns, and return a new string
        containing the entire wrapped paragraph.
        """
        return ('\n').join(self.wrap(text))


def wrap(text, width=70, **kwargs):
    """Wrap a single paragraph of text, returning a list of wrapped lines.
    
    Reformat the single paragraph in 'text' so it fits in lines of no
    more than 'width' columns, and return a list of wrapped lines.  By
    default, tabs in 'text' are expanded with string.expandtabs(), and
    all other whitespace characters (including newline) are converted to
    space.  See TextWrapper class for available keyword args to customize
    wrapping behaviour.
    """
    w = TextWrapper(width=width, **kwargs)
    return w.wrap(text)


def fill(text, width=70, **kwargs):
    """Fill a single paragraph of text, returning a new string.
    
    Reformat the single paragraph in 'text' to fit in lines of no more
    than 'width' columns, and return a new string containing the entire
    wrapped paragraph.  As with wrap(), tabs are expanded and other
    whitespace characters converted to space.  See TextWrapper class for
    available keyword args to customize wrapping behaviour.
    """
    w = TextWrapper(width=width, **kwargs)
    return w.fill(text)


_whitespace_only_re = re.compile('^[ \t]+$', re.MULTILINE)
_leading_whitespace_re = re.compile('(^[ \t]*)(?:[^ \t\n])', re.MULTILINE)

def dedent--- This code section failed: ---

 389       0  LOAD_CONST            6  ''
           3  STORE_FAST            1  'margin'

 390       6  LOAD_GLOBAL           1  '_whitespace_only_re'
           9  LOAD_ATTR             2  'sub'
          12  LOAD_CONST            1  ''
          15  LOAD_FAST             0  'text'
          18  CALL_FUNCTION_2       2 
          21  STORE_FAST            0  'text'

 391      24  LOAD_GLOBAL           3  '_leading_whitespace_re'
          27  LOAD_ATTR             4  'findall'
          30  LOAD_FAST             0  'text'
          33  CALL_FUNCTION_1       1 
          36  STORE_FAST            2  'indents'

 392      39  SETUP_LOOP          163  'to 205'
          42  LOAD_FAST             2  'indents'
          45  GET_ITER         
          46  FOR_ITER            155  'to 204'
          49  STORE_FAST            3  'indent'

 393      52  LOAD_FAST             1  'margin'
          55  LOAD_CONST            6  ''
          58  COMPARE_OP            8  'is'
          61  POP_JUMP_IF_FALSE    73  'to 73'

 394      64  LOAD_FAST             3  'indent'
          67  STORE_FAST            1  'margin'
          70  JUMP_BACK            46  'to 46'

 398      73  LOAD_FAST             3  'indent'
          76  LOAD_ATTR             5  'startswith'
          79  LOAD_FAST             1  'margin'
          82  CALL_FUNCTION_1       1 
          85  POP_JUMP_IF_FALSE    91  'to 91'

 399      88  CONTINUE             46  'to 46'

 403      91  LOAD_FAST             1  'margin'
          94  LOAD_ATTR             5  'startswith'
          97  LOAD_FAST             3  'indent'
         100  CALL_FUNCTION_1       1 
         103  POP_JUMP_IF_FALSE   115  'to 115'

 404     106  LOAD_FAST             3  'indent'
         109  STORE_FAST            1  'margin'
         112  JUMP_BACK            46  'to 46'

 409     115  SETUP_LOOP           83  'to 201'
         118  LOAD_GLOBAL           6  'enumerate'
         121  LOAD_GLOBAL           7  'zip'
         124  LOAD_FAST             1  'margin'
         127  LOAD_FAST             3  'indent'
         130  CALL_FUNCTION_2       2 
         133  CALL_FUNCTION_1       1 
         136  GET_ITER         
         137  FOR_ITER             44  'to 184'
         140  UNPACK_SEQUENCE_2     2 
         143  STORE_FAST            4  'i'
         146  UNPACK_SEQUENCE_2     2 
         149  STORE_FAST            5  'x'
         152  STORE_FAST            6  'y'

 410     155  LOAD_FAST             5  'x'
         158  LOAD_FAST             6  'y'
         161  COMPARE_OP            3  '!='
         164  POP_JUMP_IF_FALSE   137  'to 137'

 411     167  LOAD_FAST             1  'margin'
         170  LOAD_FAST             4  'i'
         173  SLICE+2          
         174  STORE_FAST            1  'margin'

 412     177  BREAK_LOOP       
         178  JUMP_BACK           137  'to 137'
         181  JUMP_BACK           137  'to 137'
         184  POP_BLOCK        

 414     185  LOAD_FAST             1  'margin'
         188  LOAD_GLOBAL           8  'len'
         191  LOAD_FAST             3  'indent'
         194  CALL_FUNCTION_1       1 
         197  SLICE+2          
         198  STORE_FAST            1  'margin'
       201_0  COME_FROM                '115'
         201  JUMP_BACK            46  'to 46'
         204  POP_BLOCK        
       205_0  COME_FROM                '39'

 417     205  LOAD_CONST            2  ''
         208  POP_JUMP_IF_FALSE   290  'to 290'
         211  LOAD_FAST             1  'margin'
       214_0  COME_FROM                '208'
         214  POP_JUMP_IF_FALSE   290  'to 290'

 418     217  SETUP_LOOP           70  'to 290'
         220  LOAD_FAST             0  'text'
         223  LOAD_ATTR             9  'split'
         226  LOAD_CONST            3  '\n'
         229  CALL_FUNCTION_1       1 
         232  GET_ITER         
         233  FOR_ITER             50  'to 286'
         236  STORE_FAST            7  'line'

 419     239  LOAD_FAST             7  'line'
         242  UNARY_NOT        
         243  POP_JUMP_IF_TRUE    233  'to 233'
         246  LOAD_FAST             7  'line'
         249  LOAD_ATTR             5  'startswith'
         252  LOAD_FAST             1  'margin'
         255  CALL_FUNCTION_1       1 
         258  POP_JUMP_IF_TRUE    233  'to 233'
         261  LOAD_ASSERT          10  'AssertionError'

 420     264  LOAD_CONST            4  'line = %r, margin = %r'
         267  LOAD_FAST             7  'line'
         270  LOAD_FAST             1  'margin'
         273  BUILD_TUPLE_2         2 
         276  BINARY_MODULO    
         277  CALL_FUNCTION_1       1 
         280  RAISE_VARARGS_1       1 
         283  JUMP_BACK           233  'to 233'
         286  POP_BLOCK        
       287_0  COME_FROM                '217'
         287  JUMP_FORWARD          0  'to 290'
       290_0  COME_FROM                '217'

 422     290  LOAD_FAST             1  'margin'
         293  POP_JUMP_IF_FALSE   324  'to 324'

 423     296  LOAD_GLOBAL          11  're'
         299  LOAD_ATTR             2  'sub'
         302  LOAD_CONST            5  '(?m)^'
         305  LOAD_FAST             1  'margin'
         308  BINARY_ADD       
         309  LOAD_CONST            1  ''
         312  LOAD_FAST             0  'text'
         315  CALL_FUNCTION_3       3 
         318  STORE_FAST            0  'text'
         321  JUMP_FORWARD          0  'to 324'
       324_0  COME_FROM                '321'

 424     324  LOAD_FAST             0  'text'
         327  RETURN_VALUE     

Parse error at or near `JUMP_BACK' instruction at offset 201


if __name__ == '__main__':
    print dedent('Hello there.\n  This is indented.')