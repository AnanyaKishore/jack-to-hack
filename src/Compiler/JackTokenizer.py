import re
KEYWORD = "KEYWORD"
SYMBOL = "SYMBOL"
INT_CONST = "INT_CONST"
STRING_CONST = "STRING_CONST"
IDENTIFIER = "IDENTIFIER"

TAG = {KEYWORD: "keyword", SYMBOL: "symbol", INT_CONST: "integerConstant", STRING_CONST: "stringConstant", IDENTIFIER: "identifier"}
KEYWORDS = {'class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char', 'boolean', 'void', 'true', 'false', 
'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return'}
SYMBOLS = set("[]{}().,;+-*/&|<>=~")
_XML_ESCAPE = str.maketrans({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'})

def escape(s): return s.translate(_XML_ESCAPE)

class JackTokenizer:
    def __init__(self, filename):
        self._filename = filename
        with open(filename, 'r', encoding='utf-8') as fh:
            raw = fh.read()
        self._tokens = []
        self._pos = -1
        self._lex(self._strip_comments(raw))
    
    def tokenize(self):
        return list(self._tokens)
    
    def writeXML(self, out_path):
        # Writes the <ClassName>T.xml tokenizer output
        lines = ['<tokens>']
        for ttype, tval in self._tokens:
            tag = TAG[ttype]
            val = escape(str(tval))
            lines.append(f'  <{tag}> {val} </{tag}>')
        lines.append('</tokens>')
        with open(out_path, 'w', encoding = 'utf-8') as fh:
            fh.write('\n'.join(lines) + '\n')

    def hasMoreTokens(self):
        return self._pos < len(self._tokens) - 1
    
    def advance(self):
        self._pos += 1
    
    def tokenType(self):
        return self._tokens[self._pos][0]
    
    def keyword(self):
        return self._tokens[self._pos][1]
    
    def symbol(self):
        return self._tokens[self._pos][1]
    
    def identifier(self):
        return self._tokens[self._pos][1]
    
    def intVal(self):
        return self._tokens[self._pos][1]
    
    def stringVal(self):
        return self._tokens[self._pos][1]
    
    def _strip_comments(self, src):
        src = re.sub(r'/\*.*?\*/', '', src, flags = re.DOTALL)
        src = re.sub(r'//[^\n]*', '', src)
        return src
    
    def _lex(self, src: str):
        i = 0
        n = len(src)
        while i < n:
            c = src[i]
            if c.isspace(): 
                i += 1
            elif c == '"':
                j = src.index('"', i + 1)
                self._tokens.append((STRING_CONST, src[i+1: j]))
                i = j + 1
            elif c in SYMBOLS:
                self._tokens.append((SYMBOL, c))
                i += 1
            elif c.isdigit():
                j = i
                while j < n and src[j].isdigit():
                    j += 1
                val = int(src[i: j])
                if not(0 <= val <= 32767):
                    raise ValueError(f"Integer {val} out of bounds")
                self._tokens.append((INT_CONST, val))
                i = j
            elif c.isalpha() or c == '_':
                j = i
                while j < n and (src[j].isalnum() or src[j] == '_'):
                    j += 1
                word = src[i: j]
                ttype = KEYWORD if word in KEYWORDS else IDENTIFIER
                self._tokens.append((ttype, word))
                i = j
            else:
                i += 1