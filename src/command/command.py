from typing import Optional

from satori import Event
from satori.client import Account

from src.bot.app import message_sender
from src.bot.command import cp_manager
from src.bot.permission import ps_manager
from src.element.message import Message


class Command:
    @staticmethod
    def command_split(message: Message) -> Optional[list[str]]:
        if message.message.startswith('/') or message.message.startswith('!'):
            return message.message[1:].removesuffix(" ").split(" ")
        return None

    @staticmethod
    async def command_parsing(message: Message, _: Account, event: Event) -> None:

        command = Command.command_split(message)

        if command is None:
            return

        ps_manager.create_player(str(event.user.id))

        for parser in list(cp_manager.command_parsers):
            result = await parser.parse(message, command)
            if result is not None:
                if result.has_message:
                    await message_sender.send_message(event, result.message)
                break
