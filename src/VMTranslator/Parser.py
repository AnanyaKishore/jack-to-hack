class Parser:
    def __init__(self, filename):
        self.index = 0
        self.lines = []
        self.current = None
        with open(filename) as f:
            for line in f:
                if self.clean(line): self.lines.append(self.clean(line))
    
    def clean(self, line):
        # Extracting the portion of the line without the comment
        # Also removes white spaces
        line = line.split("//")[0].strip()
        return line
    
    def hasMoreLines(self):
        return self.index < len(self.lines)
    
    def advance(self):
        self.current = self.lines[self.index]
        self.index += 1

    def commandType(self):
        cmd = self.current.split()[0]
        if cmd == "push": return "C_PUSH"
        if cmd == "pop": return "C_POP"
        if cmd == "label": return "C_LABEL"
        if cmd == "goto": return "C_GOTO"
        if cmd == "if-goto": return "C_IF"
        if cmd == "function": return "C_FUNCTION"
        if cmd == "return": return "C_RETURN"
        if cmd == "call": return "C_CALL"
        return "C_ARITHMETIC"
    
    def arg1(self):
        ctype = self.commandType()
        if ctype == "C_RETURN": raise ValueError("Must not call arg1() when commandType is C_RETURN")
        if ctype == "C_ARITHMETIC": return self.current.split()[0]
        return self.current.split()[1]
    
    def arg2(self):
        ctype = self.commandType()
        if ctype not in ["C_PUSH", "C_POP", "C_FUNCTION", "C_CALL"]: 
            raise ValueError('''Must not call arg2() unless commandType is in ["C_PUSH", "C_POP", "C_FUNCTION", "C_CALL"]''')
        return int(self.current.split()[2])