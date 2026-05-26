_SEG = {'CONST': 'constant', 'ARG': 'argument', 'LOCAL': 'local', 'STATIC': 'static', 'THIS': 'this', 'THAT': 'that', 'POINTER': 'pointer', 'TEMP': 'temp',
        'constant': 'constant', 'argument': 'argument', 'local': 'local', 'static': 'static', 'this': 'this', 'that': 'that', 'pointer': 'pointer', 'temp': 'temp'}
_ARITH = {'add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not'}

class VMWriter:
    def __init__(self, filename):
        self._file = open(filename, 'w', encoding = 'utf-8')

    def writePush(self, segment, index):
        self._emit(f'push {_SEG[segment]} {index}')
    
    def writePop(self, segment, index):
        if segment in ('CONST', 'constant'):
            raise ValueError('Cannot pop to const segment')
        self._emit(f'pop {_SEG[segment]} {index}')
    
    def writeArithmetic(self, command):
        if command not in _ARITH:
            raise ValueError('Invalid arithmetic command')
        self._emit(command)
    
    def writeLabel(self, label):
        self._emit(f'label {label}')
    
    def writeGoto(self, label):
        self._emit(f'goto {label}')
    
    def writeIf(self, label):
        self._emit(f'if-goto {label}')

    def writeCall(self, name, n_args):
        self._emit(f'call {name} {n_args}')
    
    def writeFunction(self, name, n_locals):
        self._emit(f'function {name} {n_locals}')
    
    def writeReturn(self):
        self._emit('return')
    
    def close(self):
        self._file.close()
    
    def _emit(self, line):
        self._file.write(line + '\n')
    
    def __enter__(self):
        return self
    
    def __exit__(self, *_):
        self.close()