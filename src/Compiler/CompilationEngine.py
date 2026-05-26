from SymbolTable import SymbolTable, STATIC, FIELD, ARG, VAR, NONE
from VMWriter import VMWriter

_KW  = 'KEYWORD'
_SYM = 'SYMBOL'
_INT = 'INT_CONST'
_STR = 'STRING_CONST'
_ID  = 'IDENTIFIER'

_TAG = {_KW:  'keyword', _SYM: 'symbol', _INT: 'integerConstant', _STR: 'stringConstant', _ID:  'identifier'}
_OP_VM = {'+': 'add', '-': 'sub', '&': 'and', '|': 'or', '<': 'lt',  '>': 'gt', '=': 'eq', '*': None,  '/': None}
_KIND_SEG = {STATIC: 'STATIC', FIELD: 'THIS', ARG: 'ARG', VAR: 'LOCAL'}
_XML_ESCAPE = str.maketrans({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'})
def _escape(s): return s.translate(_XML_ESCAPE)

class JackSyntaxError(Exception): pass

class CompilationEngine:
    def __init__(self, tokens, output_base: str):
        self._tokens = tokens
        self._pos = 0
        self._xml_lines = []
        self._depth = 0
        self._symbols = SymbolTable()
        self._vm = VMWriter(output_base + '.vm')
        self._xml_path = output_base + '.xml'
        self._class_name = ''
        self._label_id = 0
    
    def compile_class(self):
        self._compile_class()
        self._flush_xml()
        self._vm.close()

    def _compile_class(self):
        self._open('class')
        self._eat_kw('class')
        self._class_name = self._eat_id()
        self._eat_sym('{')
        while self._cur_is(_KW, 'static', 'field'):
            self._compile_class_var_dec()
        while self._cur_is(_KW, 'constructor', 'function', 'method'):
            self._compile_subroutine()
        self._eat_sym('}')
        self._close('class')

    def _compile_class_var_dec(self):
        self._open('classVarDec')
        kind = self._eat_kw('static', 'field').upper()
        type_ = self._compile_type()
        name = self._eat_id()
        self._symbols.define(name, type_, kind)
        while self._cur_is(_SYM, ','):
            self._eat_sym(',')
            name = self._eat_id()
            self._symbols.define(name, type_, kind)
        self._eat_sym(';')
        self._close('classVarDec')
    
    def _compile_type(self, allow_void = False):
        allowed_kws = ('int', 'char', 'boolean', 'void') if allow_void else ('int', 'char', 'boolean')
        if self._cur_type() == _KW and self._cur_val() in allowed_kws:
            return self._eat_kw(*allowed_kws)
        return self._eat_id()
    
    def _compile_subroutine(self):
        self._open('subroutineDec')
        self._symbols.startSubroutine()
        sub_kind = self._eat_kw('constructor', 'function', 'method')
        if sub_kind == 'method':
            # arg 0 for this
            self._symbols.define('this', self._class_name, ARG)
        _return_type = self._compile_type(allow_void = True)
        sub_name = self._eat_id()
        self._eat_sym('(')
        self._compile_parameter_list()
        self._eat_sym(')')
        self._open('subroutineBody')
        self._eat_sym('{')
        while self._cur_is(_KW, 'var'):
            self._compile_var_dec()
        n_locals = self._symbols.varCount(VAR)
        full_name = f'{self._class_name}.{sub_name}'
        self._vm.writeFunction(full_name, n_locals)
        if sub_kind == 'constructor':
            n_fields = self._symbols.varCount(FIELD)
            self._vm.writePush('CONST', n_fields)
            self._vm.writeCall('Memory.alloc', 1)
            self._vm.writePop('POINTER', 0)
        elif sub_kind == 'method':
            self._vm.writePush('ARG', 0)
            self._vm.writePop('POINTER', 0)
        self._compile_statements()
        self._eat_sym('}')
        self._close('subroutineBody')
        self._close('subroutineDec')

    def _compile_parameter_list(self):
        self._open('parameterList')
        if not self._cur_is(_SYM, ')'):
            type_ = self._compile_type()
            name = self._eat_id()
            self._symbols.define(name, type_, ARG)
            while self._cur_is(_SYM, ','):
                self._eat_sym(',')
                type_ = self._compile_type()
                name = self._eat_id()
                self._symbols.define(name, type_, ARG)
        self._close('parameterList')
    
    def _compile_var_dec(self):
        self._open('varDec')
        self._eat_kw('var')
        type_ = self._compile_type()
        name = self._eat_id()
        self._symbols.define(name, type_, VAR)
        while self._cur_is(_SYM, ','):
            self._eat_sym(',')
            name = self._eat_id()
            self._symbols.define(name, type_, VAR)
        self._eat_sym(';')
        self._close('varDec')

    def _compile_statements(self):
        self._open('statements')
        _stype = {'let': self._compile_let, 'if': self._compile_if, 'while': self._compile_while, 'do': self._compile_do, 'return': self._compile_return}
        while self._cur_type() == _KW and self._cur_val() in _stype:
            _stype[self._cur_val()]()
        self._close('statements')
    
    def _compile_let(self):
        self._open('letStatement')
        self._eat_kw('let')
        var_name = self._eat_id()
        is_array = self._cur_is(_SYM, '[')
        if is_array:
            self._push_var(var_name)
            self._eat_sym('[')
            self._compile_expression()
            self._eat_sym(']')
            self._vm.writeArithmetic('add')
        self._eat_sym('=')
        self._compile_expression()
        self._eat_sym(';')
        if is_array:
            self._vm.writePop('TEMP', 0)
            self._vm.writePop('POINTER', 1)
            self._vm.writePush('TEMP', 0)
            self._vm.writePop('THAT', 0)
        else:
            kind = self._symbols.kindOf(var_name)
            idx = self._symbols.indexOf(var_name)
            self._vm.writePop(_KIND_SEG[kind], idx)
        self._close('letStatement')

    def _compile_if(self):
        self._open('ifStatement')
        label_else = self._new_label()
        label_end = self._new_label()
        self._eat_kw('if')
        self._eat_sym('(')
        self._compile_expression()
        self._eat_sym(')')
        self._vm.writeArithmetic('not')
        self._vm.writeIf(label_else)
        self._eat_sym('{')
        self._compile_statements()
        self._eat_sym('}')
        self._vm.writeGoto(label_end)
        self._vm.writeLabel(label_else)
        if self._cur_is(_KW, 'else'):
            self._eat_kw('else')
            self._eat_sym('{')
            self._compile_statements()
            self._eat_sym('}')
        self._vm.writeLabel(label_end)
        self._close('ifStatement')

    def _compile_while(self):
        self._open('whileStatement')
        label_start = self._new_label()
        label_end = self._new_label()
        self._vm.writeLabel(label_start)
        self._eat_kw('while')
        self._eat_sym('(')
        self._compile_expression()
        self._eat_sym(')')
        self._vm.writeArithmetic('not')
        self._vm.writeIf(label_end)
        self._eat_sym('{')
        self._compile_statements()
        self._eat_sym('}')
        self._vm.writeGoto(label_start)
        self._vm.writeLabel(label_end)
        self._close('whileStatement')

    def _compile_do(self):
        self._open('doStatement')
        self._eat_kw('do')
        self._compile_subroutine_call()
        self._vm.writePop('TEMP', 0)
        self._eat_sym(';')
        self._close('doStatement')
    
    def _compile_return(self):
        self._open('returnStatement')
        self._eat_kw('return')
        if not self._cur_is(_SYM, ';'):
            self._compile_expression()
        else:
            self._vm.writePush('CONST', 0)
        self._vm.writeReturn()
        self._eat_sym(';')
        self._close('returnStatement')

    def _compile_expression(self):
        self._open('expression')
        self._compile_term()
        while self._cur_type() == _SYM and self._cur_val() in _OP_VM:
            op = self._eat_sym_any()
            self._compile_term()
            vm_op = _OP_VM[op]
            if vm_op:
                self._vm.writeArithmetic(vm_op)
            elif op == '*':
                self._vm.writeCall('Math.multiply', 2)
            elif op == '/':
                self._vm.writeCall('Math.divide', 2)
        self._close('expression')

    def _compile_term(self):
        self._open('term')
        tok_type = self._cur_type()
        tok_val = self._cur_val()
        if tok_type == _INT:
            val = self._tokens[self._pos][1]
            self._advance_write()
            self._vm.writePush('CONST', val)
        elif tok_type == _STR:
            s = self._tokens[self._pos][1]
            self._advance_write()
            self._vm.writePush('CONST', len(s))
            self._vm.writeCall('String.new', 1)
            for ch in s:
                self._vm.writePush('CONST', ord(ch))
                self._vm.writeCall('String.appendChar', 2)
        elif tok_type == _KW and tok_val in ('true', 'false', 'null', 'this'):
            self._advance_write()
            if tok_val == 'true':
                self._vm.writePush('CONST', 0)
                self._vm.writeArithmetic('not')
            elif tok_val in ('false', 'null'):
                self._vm.writePush('CONST', 0)
            else:
                self._vm.writePush('POINTER', 0)
        elif tok_type == _SYM and tok_val == '(':
            self._eat_sym('(')
            self._compile_expression()
            self._eat_sym(')')
        elif tok_type == _SYM and tok_val in ('-', '~'):
            op = self._eat_sym_any()
            self._compile_term()
            self._vm.writeArithmetic('neg' if op == '-' else 'not')
        elif tok_type == _ID:
            next_tok = self._peek()
            if next_tok and next_tok[0] == _SYM and next_tok[1] == '[':
                var_name = self._eat_id()
                self._push_var(var_name)
                self._eat_sym('[')
                self._compile_expression()
                self._eat_sym(']')
                self._vm.writeArithmetic('add')
                self._vm.writePop('POINTER', 1)
                self._vm.writePush('THAT', 0)
            elif next_tok and next_tok[0] == _SYM and next_tok[1] in ('(', '.'):
                self._compile_subroutine_call()
            else:
                var_name = self._eat_id()
                self._push_var(var_name)
        else:
            raise JackSyntaxError("Invalid token")
        self._close('term')

    def _compile_subroutine_call(self):
        name = self._eat_id()
        n_args = 0
        if self._cur_is(_SYM, '.'):
            self._eat_sym('.')
            method_name = self._eat_id()
            kind = self._symbols.kindOf(name)
            if kind != NONE:
                obj_type = self._symbols.typeOf(name)
                self._push_var(name)
                full_name = f'{obj_type}.{method_name}'
                n_args = 1
            else:
                full_name = f'{name}.{method_name}'
                n_args = 0
        else:
            self._vm.writePush('POINTER', 0)
            full_name = f'{self._class_name}.{name}'
            n_args = 1
        self._eat_sym('(')
        n_args += self._compile_expression_list()
        self._eat_sym(')')
        self._vm.writeCall(full_name, n_args)
    
    def _compile_expression_list(self):
        self._open('expressionList')
        count = 0
        if not self._cur_is(_SYM, ')'):
            self._compile_expression()
            count = 1
            while self._cur_is(_SYM, ','):
                self._eat_sym(',')
                self._compile_expression()
                count += 1
        self._close('expressionList')
        return count
    
    def _cur(self):
        return self._tokens[self._pos] if self._pos < len(self._tokens) else None
    
    def _cur_type(self):
        tok = self._cur()
        return tok[0] if tok else ''
    
    def _cur_val(self):
        tok = self._cur()
        return tok[1] if tok else None
    
    def _peek(self, offset = 1):
        idx = self._pos + offset
        return self._tokens[idx] if idx < len(self._tokens) else None
    
    def _cur_is(self, ttype, *vals):
        tok = self._cur()
        if not tok or tok[0] != ttype:
            return False
        return (not vals) or (tok[1] in vals)
    
    def _advance_write(self):
        tok = self._tokens[self._pos]
        self._pos += 1
        self._write_token(tok)
        return tok
    
    def _eat_kw(self, *keywords):
        tok = self._cur()
        if not tok or tok[0] != _KW or (keywords and tok[1] not in keywords):
            raise JackSyntaxError('Keyword mismatch')
        self._advance_write()
        return tok[1]
    
    def _eat_sym(self, symbol):
        tok = self._cur()
        if not tok or tok[0] != _SYM or tok[1] != symbol:
            raise JackSyntaxError('Symbol mismatch')
        self._advance_write()
        return symbol
    
    def _eat_sym_any(self):
        tok = self._cur()
        if not tok or tok[0] != _SYM:
            raise JackSyntaxError('Symbol token mismatch')
        self._advance_write()
        return tok[1]
    
    def _eat_id(self):
        tok = self._cur()
        if not tok or tok[0] != _ID:
            raise JackSyntaxError('Identifier token mismatch')
        self._advance_write()
        return tok[1]
    
    def _push_var(self, name):
        kind = self._symbols.kindOf(name)
        idx = self._symbols.indexOf(name)
        if kind == NONE or idx is None:
            raise JackSyntaxError('Undefined variable')
        self._vm.writePush(_KIND_SEG[kind], idx)

    def _new_label(self):
        lbl = f'{self._class_name}_L{self._label_id}'
        self._label_id += 1
        return lbl
    
    def _open(self, tag):
        self._xml_lines.append(" " * self._depth + f'<{tag}>')
        self._depth += 1
    
    def _close(self, tag):
        self._depth -= 1
        self._xml_lines.append(' ' * self._depth + f'</{tag}>')

    def _write_token(self, tok):
        ttype, tval = tok
        tag = _TAG[ttype]
        val = _escape(str(tval))
        self._xml_lines.append(' ' * self._depth + f'<{tag}> {val} </{tag}>')
    
    def _flush_xml(self):
        with open(self._xml_path, 'w', encoding = 'utf-8') as fh:
            fh.write('\n'.join(self._xml_lines) + '\n')