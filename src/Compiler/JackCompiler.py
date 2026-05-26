import sys
import os
from JackTokenizer import JackTokenizer
from CompilationEngine import CompilationEngine

_DEFAULT_OUT_DIR = "out"
def compile_file(jack_path: str, out_dir: str) -> None:
    if not jack_path.endswith(".jack"):
        print(f"Not a .jack file")
        return
    class_name = os.path.basename(jack_path)[:-5]
    out_base = os.path.join(out_dir, class_name)
    tokenizer = JackTokenizer(jack_path)
    tokenizer.writeXML(out_base + "T.xml")
    tokens = tokenizer.tokenize()
    engine = CompilationEngine(tokens, out_base)
    engine.compile_class()
    print(f"    Compiled {class_name}.jack")

def main() -> None:
    if not (2 <= len(sys.argv) <= 3):
        print("Usage: python Compiler/JackCompiler.py <file.jack | directory> [out_dir]")
        sys.exit(1)
    target  = sys.argv[1].rstrip(os.sep)
    out_dir = sys.argv[2] if len(sys.argv) == 3 else _DEFAULT_OUT_DIR
    os.makedirs(out_dir, exist_ok=True)
    if os.path.isdir(target):
        jack_files = sorted(os.path.join(target, f) for f in os.listdir(target) if f.endswith(".jack"))
        if not jack_files:
            print("No .jack files in directory")
            sys.exit(1)
        for jf in jack_files:
            compile_file(jf, out_dir)
    elif os.path.isfile(target):
        compile_file(target, out_dir)
    else:
        print(f"Invalid path: {target}")
        sys.exit(1)

if __name__ == "__main__":
    main()