import os
import sys
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
COMPILER = os.path.join(ROOT, "src", "Compiler", "JackCompiler.py")
TRANSLATOR = os.path.join(ROOT, "src", "VMTranslator", "main.py")
ASSEMBLER = os.path.join(ROOT, "src", "Assembler", "Assembler.py")

def _run(cmd, step):
    print(f"{step}")
    result = subprocess.run(cmd, text = True)
    if result.returncode != 0:
        print(f"Step failed with exit code {result.returncode}")
        sys.exit(result.returncode)

def run_pipeline(jack_dir: str) -> None:
    jack_dir = os.path.normpath(jack_dir)
    if not os.path.isdir(jack_dir):
        print(f"{jack_dir} is not a valid directory")
        sys.exit(1)
    jack_files = [f for f in os.listdir(jack_dir) if f.endswith(".jack")]
    if not jack_files:
        print(f"No .jack files found in {jack_dir}")
        sys.exit(1)
    program_name = os.path.basename(jack_dir)
    out_dir = os.path.join(ROOT, "out", program_name)
    os.makedirs(out_dir, exist_ok=True)
    asm_path  = os.path.join(out_dir, f"{program_name}.asm")
    hack_path = os.path.join(out_dir, f"{program_name}.hack")

    _run([sys.executable, COMPILER, jack_dir, out_dir], f"(1/3) Jack -> Hack VM")
    _run([sys.executable, TRANSLATOR, out_dir], f"(2/3) Hack VM -> Hack ASM")
    _run([sys.executable, ASSEMBLER, asm_path], f"(3/3) Hack ASM -> Hack Machine Language")
    print(f"Binary output is at: {hack_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    run_pipeline(sys.argv[1])