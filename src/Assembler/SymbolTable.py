class SymbolTable:
    def __init__(self):
        self.table = {}
        
        # R0-R15
        for i in range(16):
            self.table[f"R{i}"] = i
            
        # Predefined pointers
        self.table["SP"] = 0
        self.table["LCL"] = 1
        self.table["ARG"] = 2
        self.table["THIS"] = 3
        self.table["THAT"] = 4

        # I/O pointers
        self.table["SCREEN"] = 16384
        self.table["KBD"] = 24576

    def addEntry(self, symbol: str, address: int) -> None:
        self.table[symbol] = address

    def contains(self, symbol: str) -> bool:
        return symbol in self.table

    def getAddress(self, symbol: str) -> int:
        if symbol not in self.table:
            raise KeyError(f"Symbol not found: {symbol}")
        return self.table[symbol]