import os

class CodeWriter:
    def __init__(self, out_file, bootstrap = True):
        self.f = open(out_file, "w", encoding = "utf-8")
        self.filename = ""
        self.current_function = ""
        self.label_count = 0
        self.call_count = 0

        if bootstrap:
            self._w("@256")
            self._w("D=A")
            self._w("@SP")
            self._w("M=D")
            self.writeCall("Sys.init", 0)

    def setFileName(self, filename):
        self.filename = os.path.splitext(os.path.basename(filename))[0]

    def _w(self, s): self.f.write(s + '\n')
    
    def writeArithmetic(self, command):
        if command in ["add", "sub", "and", "or"]:
            self._w("@SP")
            self._w("AM=M-1")
            self._w("D=M")
            self._w("A=A-1")
            if command == "add": self._w("M=D+M")
            if command == "sub": self._w("M=M-D")
            if command == "and": self._w("M=D&M")
            if command == "or": self._w("M=D|M")
            return
        if command in ["neg", "not"]:
            self._w("@SP")
            self._w("A=M-1")
            if command == "neg": self._w("M=-M")
            else: self._w("M=!M")
            return
        
        true_label = self._scoped(f"BOOL_TRUE{self.label_count}")
        end_label = self._scoped(f"BOOL_END{self.label_count}")
        self.label_count += 1
        jump = {"eq": "JEQ", "gt": "JGT", "lt": "JLT"}[command]
        self._w("@SP")
        self._w("AM=M-1")
        self._w("D=M")
        self._w("A=A-1")
        self._w("D=M-D")
        self._w(f"@{true_label}")
        self._w(f"D;{jump}")
        self._w("@SP")
        self._w("A=M-1")
        # false is implemented as 0
        self._w("M=0")
        self._w(f"@{end_label}")
        self._w("0;JMP")
        self._w(f"({true_label})")
        self._w("@SP")
        self._w("A=M-1")
        # true is implemented as -1
        self._w("M=-1")
        self._w(f"({end_label})")

    def writePushPop(self, command, segment, index):
        if command == "C_PUSH": self._push(segment, index)
        else: self._pop(segment, index)

    def _push_repeated(self):
        self._w("@SP")
        self._w("A=M")
        self._w("M=D")
        self._w("@SP")
        self._w("M=M+1")
    
    def _push(self, segment, i):
        if segment == "constant":
            self._w(f"@{i}")
            self._w("D=A")
            self._push_repeated()
            return
        
        if segment in ["local", "argument", "this", "that"]:
            instruc = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT"}[segment]
            self._w(f"@{i}")
            self._w("D=A")
            self._w(f"@{instruc}")
            self._w("A=D+M")
            self._w("D=M")
            self._push_repeated()
            return
        
        if segment == "temp":
            self._w("@5")
            self._w("D=A")
            self._w(f"@{i}")
            self._w("A=D+A")
            self._w("D=M")
            self._push_repeated()
            return
        
        if segment == "pointer":
            if(i == 0): self._w("@THIS")
            else: self._w("@THAT")
            self._w("D=M")
            self._push_repeated()
            return
        
        if segment == "static":
            self._w(f"@{self.filename}.{i}")
            self._w("D=M")
            self._push_repeated()
            return
        return ValueError(f"{segment} is not a valid segment")
    
    def _pop_repeated(self):
        self._w("@SP")
        self._w("AM=M-1")
        self._w("D=M")
    
    def _pop(self, segment, i):
        if segment in ["local", "argument", "this", "that"]:
            instruc = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT"}[segment]
            self._w(f"@{i}")
            self._w("D=A")
            self._w(f"@{instruc}")
            self._w("D=D+M")
            self._w("@13")
            self._w("M=D")
            self._pop_repeated()
            self._w("@13")
            self._w("A=M")
            self._w("M=D")
            return
        
        if segment == "temp":
            self._w("@5")
            self._w("D=A")
            self._w(f"@{i}")
            self._w("D=D+A")
            self._w("@13")
            self._w("M=D")
            self._pop_repeated()
            self._w("@13")
            self._w("A=M")
            self._w("M=D")
            return
        
        if segment == "pointer":
            self._pop_repeated()
            if(i == 0): self._w("@THIS")
            else: self._w("@THAT")
            self._w("M=D")
            return
        
        if segment == "static":
            self._pop_repeated()
            self._w(f"@{self.filename}.{i}")
            self._w("M=D")
            return
        return ValueError(f"{segment} is not a valid segment")
    
    def _scoped(self, label):
        if self.current_function:
            return f"{self.current_function}${label}"
        return f"{self.filename}${label}"

    def writeLabel(self, label): 
        self._w(f"({self._scoped(label)})")

    def writeGoto(self, label):
        self._w(f"@{self._scoped(label)}")
        self._w("0;JMP")
    
    def writeIf(self, label):
        self._pop_repeated()
        self._w(f"@{self._scoped(label)}")
        self._w("D;JNE")

    def writeFunction(self, functionName, nVars):
        self.current_function = functionName
        self._w(f"({functionName})")
        for _ in range(nVars):
            self._w("@0")
            self._w("D=A")
            self._push_repeated()


    def writeCall(self, functionName, nArgs):
        ret = f"{functionName}$ret.{self.call_count}"
        self.call_count += 1
        # Pushing return address to stack
        self._w(f"@{ret}")
        self._w("D=A")
        self._push_repeated()
        # Pushing current LCL, ARG, THIS, THAT to stack
        for seg in ["LCL", "ARG", "THIS", "THAT"]:
            self._w(f"@{seg}")
            self._w("D=M")
            self._push_repeated()

        # Setting ARG as SP-nArgs-5
        self._w("@5")
        self._w("D=A")
        self._w(f"@{nArgs}")
        self._w("D=D+A")
        self._w("@SP")
        self._w("D=M-D")
        self._w("@ARG")
        self._w("M=D")

        # Setting LCL as SP
        self._w("@SP")
        self._w("D=M")
        self._w("@LCL")
        self._w("M=D")

        # Setting goto function
        self._w(f"@{functionName}")
        self._w("0;JMP")
        # Return address
        self._w(f"({ret})")
    
    def writeReturn(self):
        self._w("@LCL")
        self._w("D=M")
        self._w("@R13")
        self._w("M=D") # stores current LCL

        # Getting return address
        self._w("@5")
        self._w("A=D-A")
        self._w("D=M")
        self._w("@R14")
        self._w("M=D") # stores return address

        self._pop_repeated()
        self._w("@ARG")
        self._w("A=M")
        self._w("M=D")

        self._w("@ARG")
        self._w("D=M+1")
        self._w("@SP")
        self._w("M=D")

        self._restore(1, "THAT")
        self._restore(2, "THIS")
        self._restore(3, "ARG")
        self._restore(4, "LCL")

        self._w("@R14")
        self._w("A=M")
        self._w("0;JMP")

    def _restore(self, i, segment):
        # R13 stores current LCL
        self._w("@R13")
        self._w("D=M")
        self._w(f"@{i}")
        self._w("A=D-A")
        self._w("D=M")
        self._w(f"@{segment}")
        self._w("M=D")

    def close(self): 
        self.f.close()