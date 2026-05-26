from dataclasses import dataclass

STATIC = 'STATIC'
FIELD = 'FIELD'
ARG = 'ARG'
VAR = 'VAR'
NONE = 'NONE'
KIND_TO_SEGMENT = {STATIC: 'static', FIELD: 'this', ARG: 'argument', VAR: 'local'}
@dataclass
class _Entry:
    type_: str
    kind: str
    index: int

class SymbolTable:
    def __init__(self):
        self._class_scope = {}
        self._sub_scope = {}
        self._counters = {STATIC: 0, FIELD: 0, ARG: 0, VAR: 0}

    def startSubroutine(self):
        self._sub_scope = {}
        self._counters[ARG] = 0
        self._counters[VAR] = 0
    
    def define(self, name, type_, kind):
        if kind not in (STATIC, FIELD, ARG, VAR):
            raise ValueError('Unknown symbol kind')
        entry = _Entry(type_ = type_, kind = kind, index = self._counters[kind])
        self._counters[kind] += 1
        if kind in (STATIC, FIELD):
            self._class_scope[name] = entry
        else:
            self._sub_scope[name] = entry
    
    def varCount(self, kind):
        return self._counters.get(kind, 0)
    
    def kindOf(self, name):
        entry = self._lookup(name)
        return entry.kind if entry else NONE
    
    def typeOf(self, name):
        entry = self._lookup(name)
        return entry.type_ if entry else None
    
    def indexOf(self, name):
        entry = self._lookup(name)
        return entry.index if entry else None

    def segment(self, name):
        kind = self.kindOf(name)
        return KIND_TO_SEGMENT.get(kind)
    
    def _lookup(self, name):
        return self._sub_scope.get(name) or self._class_scope.get(name)
    
    def __repr__(self):
        return (f'SymbolTable(\n' 
                f'  class={list(self._class_scope)},\n'
                f'  sub={list(self._sub_scope)},\n'
                f'  counters={self._counters}\n'
                f')'
            )