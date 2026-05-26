import sys
from Parser import Parser
from Code import Code
from SymbolTable import SymbolTable

def first_pass(input_file, symbol_table):
    parser = Parser(input_file)
    rom_address = 0
    while parser.hasMoreCommands():
        parser.advance()
        cmd_type = parser.commandType()
        if cmd_type == "L_COMMAND":
            label = parser.symbol()
            if not symbol_table.contains(label):
                symbol_table.addEntry(label, rom_address)
        elif cmd_type in ("A_COMMAND", "C_COMMAND"):
            rom_address += 1

def second_pass(input_file, output_file, symbol_table):
    # L_COMMAND is ignored in second pass
    parser = Parser(input_file)
    code = Code()
    next_variable_address = 16

    with open(output_file, "w") as out:
        while parser.hasMoreCommands():
            parser.advance()
            cmd_type = parser.commandType()

            if cmd_type == "A_COMMAND":
                symbol = parser.symbol()

                if symbol.isdigit():
                    address = int(symbol)
                else:
                    if not symbol_table.contains(symbol):
                        symbol_table.addEntry(symbol, next_variable_address)
                        next_variable_address += 1
                    address = symbol_table.getAddress(symbol)

                # converting address to 16-bit binary string
                out.write(f"{address:016b}\n")

            elif cmd_type == "C_COMMAND":
                dest_mnemonic = parser.dest()
                comp_mnemonic = parser.comp()
                jump_mnemonic = parser.jump()

                comp_bits = code.comp(comp_mnemonic)
                dest_bits = code.dest(dest_mnemonic)
                jump_bits = code.jump(jump_mnemonic)

                out.write(f"111{comp_bits}{dest_bits}{jump_bits}\n")

def assemble(input_file):
    if not input_file.endswith(".asm"):
        raise ValueError("Input file must have .asm extension")
    output_file = input_file[:-4] + ".hack"
    symbol_table = SymbolTable()
    first_pass(input_file, symbol_table)
    second_pass(input_file, output_file, symbol_table)
    return output_file

def main():
    if len(sys.argv) != 2:
        sys.exit(1)
    input_file = sys.argv[1]
    try:
        output_file = assemble(input_file)
        print(f"    Output file at: {output_file}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()