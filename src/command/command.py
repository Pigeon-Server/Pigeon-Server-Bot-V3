from satori import Event
from satori.client import Account

from src.base.logger import logger
from src.bot.plugin import ps_manager
from src.command.command_parser_manager import CommandParserManager
from src.element.message import Message
from src.exception.exception import CustomError
from src.utils.message_sender import MessageSender
from src.command.other_command import OtherCommand
from src.command.permission_command import PermissionCommand
from src.command.server_status_command import ServerStatusCommand
from src.command.server_list_command import ServerListCommand
from src.command.mcsm_command import McsmCommand


class Command:

    @staticmethod
    async def command_parsing(message: Message, _: Account, event: Event) -> None:

        try:
            command = message.command_split()
        except CustomError as e:
            logger.error(e)
            await MessageSender.send_message(event, f"无法解析此命令,{e.info}")
            return

        if command is None:
            return

        ps_manager.create_player(str(event.user.id))

        result = await CommandParserManager.parse_command(message, command)
        if result is not None and result.has_message:
            await MessageSender.send_message(event, result.message)
