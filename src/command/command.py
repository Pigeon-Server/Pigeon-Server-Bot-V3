from typing import List, Optional

from satori import Event
from satori.client import Account

from src.base.config import config
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
        async def send(_msg: str) -> None:
            if config.sys_config.dev:
                await account.send(event, f"{"-" * 5}Dev{"-" * 5}\n{_msg}")
                return
            await account.send(event, _msg)

        command = Command.command_split(message)

        if command is None:
            return

        per.create_player(str(event.user.id))

        for parser in command_parsers:
            result = await parser.parse(str(event.user.id), command, message)
            if result.is_success:
                await send(result.message)
                break

                # await send(f"Permission模块帮助: \n"
                #            f"/permission player (At | id) add (permission)\n"
                #            f"/permission player (At | id) remove (permission)\n"
                #            f"/permission player (At | id) clone (At | id)\n"
                #            f"/permission player (At | id) check (permission)\n"
                #            f"/permission player (At | id) inherit add (groupName)\n"
                #            f"/permission player (At | id) inherit remove (groupName)\n"
                #            f"/permission player (At | id) inherit set (groupName)\n"
                #            f"/permission player (At | id) del\n"
                #            f"/permission player (At | id) list\n"
                #            f"/permission player (At | id) info\n"
                #            f"/permission player (At | id) create [groupName]\n"
                #            f"/permission group (groupName) add (permission)\n"
                #            f"/permission group (groupName) remove (permission)\n"
                #            f"/permission group (groupName) clone (groupName)\n"
                #            f"/permission group (groupName) check (permission)\n"
                #            f"/permission group (groupName) inherit add (groupName)\n"
                #            f"/permission group (groupName) inherit remove (groupName)\n"
                #            f"/permission group (groupName) del\n"
                #            f"/permission group (groupName) list\n"
                #            f"/permission group (groupName) info\n"
                #            f"/permission group (groupName) create\n"
                #            f"/permission reload [force]\n"
                #            f"/permission list [word]")
