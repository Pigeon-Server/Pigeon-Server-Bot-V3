from typing import List, Optional

from src.command.command_parser import CommandParser


class CommandParserManager:
    _command_parsers: List[CommandParser]

    def __init__(self):
        self._command_parsers = []

    def add_command_parser(self, command_parser: CommandParser) -> 'CommandParserManager':
        self._command_parsers.append(command_parser)
        return self

    def remove_command_parser(self, command_parser: CommandParser) -> 'CommandParserManager':
        self._command_parsers.remove(command_parser)
        return self

    @property
    def command_parsers(self) -> List[CommandParser]:
        return self._command_parsers
