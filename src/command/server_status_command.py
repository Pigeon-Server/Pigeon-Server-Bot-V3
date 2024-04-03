from typing import List, Optional

from src.bot.tools import server
from src.command.command_parser import CommandParser
from src.module.message import Message
from src.module.result import Result


class ServerStatusCommand(CommandParser):

    async def parse(self, message: Message, command: List[str]) -> Optional[Result]:
        await super().parse(message, command)
        if command[0] in ["info", "status"]:
            return Result.of_success(await server.get_online_player())
        return None
