from typing import List

from src.bot.tools import server
from src.command.command_parser import CommandParser
from src.module.message import Message
from src.module.result import Result


class ServerStatusCommand(CommandParser):

    def __init__(self):
        CommandParser.__init__(self)

    async def parse(self, _: str, command: List[str], __: Message) -> Result:
        if command[0] in ["info", "status"]:
            return Result.of_success(await server.get_online_player())
        return Result.of_failure()
