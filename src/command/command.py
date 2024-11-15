from satori import Event
from satori.client import Account

from src.base.logger import logger
from src.bot.plugin import ps_manager
from src.command.command_manager import CommandManager
from src.element.message import Message
from src.exception.exception import CustomError
from src.utils.command_utils import command_split
from src.utils.message_sender import MessageSender


class Command:

    @staticmethod
    async def command_parsing(message: Message, _: Account, event: Event) -> None:

        try:
            command = command_split(message)
        except CustomError as e:
            logger.error(e)
            await MessageSender.send_message(event, f"无法解析此命令,{e.info}")
            return

        if command is None:
            return

        ps_manager.create_player(str(event.user.id))

        result = await CommandManager.parse_command(message, command)
        if result is not None and result.has_message:
            await MessageSender.send_message(event, result.message)
