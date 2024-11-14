from typing import Optional

from satori import Event
from satori.client import Account

from src.base.logger import logger
from src.bot.command import cp_manager
from src.bot.plugin import ps_manager
from src.element.message import Message
from src.utils.message_sender import MessageSender


class Command:
    @staticmethod
    def command_split(message: Message) -> Optional[list[str]]:
        if not message.is_command:
            return None
        res = []
        stack = []
        msg = message.message[1:]
        temp = ""
        for i in msg:
            if i in ['"', "'"]:
                if stack == [] or stack[-1] != i:
                    stack.append(i)
                else:
                    stack.pop()
                continue
            if stack == [] and i.isspace():
                if len(temp) != 0:
                    res.append(temp)
                    temp = ""
                continue
            temp += i
        if temp != "":
            res.append(temp)
        return res

    @staticmethod
    async def command_parsing(message: Message, _: Account, event: Event) -> None:

        command = Command.command_split(message)

        if command is None:
            return

        ps_manager.create_player(str(event.user.id))

        try:
            for parser in list(cp_manager.command_parsers):
                result = await parser.parse(message, command)
                if result is not None:
                    if result.has_message:
                        await MessageSender.send_message(event, result.message)
                    break
        except Exception as e:
            logger.error(e)
            await MessageSender.send_message(event, "命令解析过程发生致命错误,请查看日志")
