from typing import List, Optional

from satori import Event
from satori.client import Account

from src.bot.app import message_sender
from src.bot.tools import per
from src.command.command_parser import CommandParser
from src.command.permission_command import PermissionCommand
from src.command.server_status_command import ServerStatusCommand
from src.module.message import Message

command_parsers: List[CommandParser] = [
    ServerStatusCommand(),
    PermissionCommand()
]


class Command:
    @staticmethod
    def command_split(message: Message) -> Optional[list[str]]:
        if message.message.startswith('/') or message.message.startswith('!'):
            return message.message[1:].removesuffix(" ").split(" ")
        return None

    @staticmethod
    async def command_parsing(message: Message, account: Account, event: Event) -> None:

        command = Command.command_split(message)

        if command is None:
            return

        per.create_player(str(event.user.id))

        for parser in command_parsers:
            result = await parser.parse(message, command)
            if result is not None:
                if result.has_message:
                    await message_sender.send_message(event, result.message)
                break
