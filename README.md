This project performs full-stack compilation by translating Jack source code to Hack binary. The Jack programming language is an educational computer programming language designed as part of the NAND2Tetris course. It is simple to write a compiler for, but at the same time, has the major features of an object-oriented programming language.

```
Jack (.jack) -> Hack VM (.vm) -> Hack Assembly (.asm) -> Binary (.hack)
           Compiler        VM Translator             Assembler
```

---

## Structure

```
jack-to-hack/
│
├── pipeline.py
│
├── src/
│   ├── Assembler/
│   │   ├── Assembler.py
│   │   ├── Parser.py
│   │   ├── Code.py
│   │   └── SymbolTable.py
│   │
│   ├── Compiler/
│   │   ├── JackCompiler.py
│   │   ├── JackTokenizer.py
│   │   ├── CompilationEngine.py
│   │   ├── SymbolTable.py
│   │   └── VMWriter.py
│   │
│   └── VMTranslator/
│       ├── main.py
│       ├── Parser.py
│       └── CodeWriter.py
│
├── jack/
│   ├── test_1/
│   │   ├── Main.jack
│   │   └── Conv.jack
│   └── test_2/
│       └── Main.jack
│
└── out/
    ├── test_1/
    │   ├── Conv.vm (Compiler)
    │   ├── Conv.xml (parse tree from Compiler)
    │   ├── ConvT.xml (intermediate semantic output from Compiler)
    │   ├── Main.vm   
    │   ├── Main.xml
    │   ├── MainT.xml
    │   ├── test_1.asm (VMTranslator)
    │   └── test_1.hack (Assembler)
    └── test_2/
        ├── ...
```

---

## Pipeline

```bash
python pipeline.py jack/test_1
```
This runs all three stages automatically and places all output under `out/test_1/`.  
The final binary is at `out/test_1/test_1.hack`.

### Multiple programs

Each program gets its own isolated output folder:

```bash
python pipeline.py jack/test_1
python pipeline.py jack/test_2
```

---

## Running Individual Stages

### Stage 1: Jack -> Hack VM (Compiler)

```bash
# Compile a whole directory (outputs to out/ by default)
python Compiler/JackCompiler.py jack/test_1/

# Compile to a specific output directory
python Compiler/JackCompiler.py jack/test_1/ out/test_1/

# Compile a single file
python Compiler/JackCompiler.py jack/test_1/Main.jack out/test_1/
```

### Stage 2: Hack VM -> Hack Assembly (VMTranslator)

```bash
# Translate a directory of .vm files
python VMTranslator/main.py out/test_1/

# Translate a single .vm file
python VMTranslator/main.py out/test_1/Main.vm
```

### Stage 3: Hack Assembly -> Hack Machine Language (Assembler)

```bash
python Assembler/assembler.py out/test_1/test_1.asm
```

---

## Testing on the CPU Emulator

1. Open the **CPU Emulator** from [here](https://nand2tetris.github.io/web-ide/cpu)
2. Load `out/<program>/test_1.hack` into the ROM.
3. Run or step through the program.

---

## Requirements

- Python 3.13

---
