class Parser:

    A_COMMAND = "A_COMMAND"
    C_COMMAND = "C_COMMAND"
    L_COMMAND = "L_COMMAND"

    def __init__(self, input_file: str):
        self.commands = []
        self.current_command = None
        self.current_index = -1

        with open(input_file, "r") as f:
            for line in f:
                clean = self._clean_line(line)
                if clean:
                    self.commands.append(clean)

    def _clean_line(self, line: str) -> str:
        line = line.split("//")[0]
        line = line.strip()
        return line

    def hasMoreCommands(self) -> bool:
        return self.current_index + 1 < len(self.commands)

    def advance(self) -> None:
        if self.hasMoreCommands():
            self.current_index += 1
            self.current_command = self.commands[self.current_index]

    def commandType(self) -> str:
        if self.current_command.startswith("@"):
            return self.A_COMMAND
        elif self.current_command.startswith("(") and self.current_command.endswith(")"):
            return self.L_COMMAND
        else:
            return self.C_COMMAND

    def symbol(self) -> str:
        ctype = self.commandType()
        if ctype == self.A_COMMAND:
            return self.current_command[1:]
        elif ctype == self.L_COMMAND:
            return self.current_command[1:-1]
        else:
            raise ValueError("symbol() called on non A/L command")

    def dest(self) -> str:
        if self.commandType() != self.C_COMMAND:
            return None
        if "=" in self.current_command:
            return self.current_command.split("=")[0]
        return None

    def comp(self) -> str:
        if self.commandType() != self.C_COMMAND:
            return None

        command = self.current_command
        if "=" in command:
            command = command.split("=")[1]
        if ";" in command:
            command = command.split(";")[0]
        return command

    def jump(self) -> str:
        if self.commandType() != self.C_COMMAND:
            return None
        if ";" in self.current_command:
            return self.current_command.split(";")[1]
        return None