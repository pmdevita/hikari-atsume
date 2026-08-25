from typing import Optional


class CommandNotFound(Exception):
    def __init__(self, command: Optional[str] = None):
        self.command = []

        if command:
            self.command.append(command)

    def prepend_command_word(self, command: str) -> None:
        self.command.insert(0, command)

    @property
    def name(self) -> str:
        return " ".join(self.command)
