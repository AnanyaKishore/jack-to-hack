import os
import sys
from Parser import Parser
from CodeWriter import CodeWriter

def get_vm_files(path):
    if os.path.isfile(path):
        if not path.endswith(".vm"):
            raise ValueError("Invalid input file")
        return [path]
    if os.path.isdir(path):
        return sorted(os.path.join(path, f) for f in os.listdir(path) if f.endswith(".vm"))
    raise ValueError("Invalid input path")

def get_output_path(path):
    if os.path.isfile(path):
        return path.replace(".vm", ".asm")
    folder = os.path.abspath(path)
    base = os.path.basename(folder)
    return os.path.join(folder, f"{base}.asm")

def translate(path):
    vm_files = get_vm_files(path)
    out_path = get_output_path(path)
    cw = CodeWriter(out_path, bootstrap=os.path.isdir(path))
    for vm_file in vm_files:
        p = Parser(vm_file)
        cw.setFileName(vm_file)
        while p.hasMoreLines():
            p.advance()
            ctype = p.commandType()
            if ctype == "C_ARITHMETIC":
                cw.writeArithmetic(p.arg1())
            if ctype in ["C_PUSH", "C_POP"]:
                cw.writePushPop(ctype, p.arg1(), p.arg2())
            if ctype == "C_LABEL":
                cw.writeLabel(p.arg1())
            if ctype == "C_GOTO":
                cw.writeGoto(p.arg1())
            if ctype == "C_IF":
                cw.writeIf(p.arg1())
            if ctype == "C_FUNCTION":
                cw.writeFunction(p.arg1(), p.arg2())
            if ctype == "C_CALL":
                cw.writeCall(p.arg1(), p.arg2())
            if ctype == "C_RETURN":
                cw.writeReturn()
    cw.close()
    print(f"    Output file at: {out_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(1)
    translate(sys.argv[1])