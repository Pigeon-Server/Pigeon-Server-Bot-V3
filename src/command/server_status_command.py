from typing import List, Optional

from src.bot.mcsm import mcsm
from src.bot.server_status import server
from src.command.command_parser import CommandParser
from src.element.message import Message
from src.element.result import Result


class ServerStatusCommand(CommandParser):

    async def parse(self, message: Message, command: List[str]) -> Optional[Result]:
        await super().parse(message, command)
        if command[0] in ["info", "status"]:
            return Result.of_success(server.get_online_player())
        if command[0] in ["ping"]:
            match len(command):
                case 2:
                    return Result.of_success(server.check_ip(command[1]))
                case 3:
                    return Result.of_success(server.check_ip(f"{command[1]}:{command[2]}"))
        if command[0] in ["tps"] and (command_length := len(command)) >= 2:
            res = await mcsm.run_command(command[1], "forge tps")
            if command_length == 3 and command[2] == "full":
                return res
            tps = res.message.split("\n")
            return Result.of_success(tps[-1])
        return None
