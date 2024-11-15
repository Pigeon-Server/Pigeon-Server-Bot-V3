from typing import Optional

from src.bot.plugin import mcsm
from src.command.command_manager import CommandManager
from src.element.message import Message
from src.element.result import Result
from src.module.server_status import ServerStatus


@CommandManager.add_command("/info",
                            command_docs="获取服务器状态",
                            alia_list=["/status"])
async def info_command(_: Message, __: list[str]) -> Optional[Result]:
    return Result.of_success(ServerStatus.get_online_player())


@CommandManager.add_command("/ping",
                            command_docs="ping一个地址，并获取在线人数和基础信息",
                            command_usage="/ping (ip:port) 或者 /ping (ip) (port)")
async def ping_command(_: Message, command: list[str]) -> Optional[Result]:
    match len(command):
        case 2:
            return Result.of_success(ServerStatus.check_ip(command[1]))
        case 3:
            return Result.of_success(ServerStatus.check_ip(f"{command[1]}:{command[2]}"))


@CommandManager.add_command("/tps",
                            command_docs="获取服务器tps信息",
                            command_usage="/tps (ServerName)")
async def tps_command(_: Message, command: list[str]) -> Optional[Result]:
    res = await mcsm.run_command(command[1], "forge tps")
    if len(command) == 3 and command[2] == "full":
        return res
    tps = res.message.split("\n")
    return Result.of_success(tps[-1])
