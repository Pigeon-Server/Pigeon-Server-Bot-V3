from os import getcwd
from os.path import join
from typing import List, Optional
from datetime import datetime

from satori import Image

from src.bot.app import message_sender
from src.bot.database import database
from src.command.command_parser import CommandParser
from src.element.message import Message
from src.element.result import Result
from src.module.message_wordcloud import MessageWordCloud
from src.type.types import ReturnType


class OtherCommand(CommandParser):
    async def parse(self, message: Message, command: List[str]) -> Optional[Result]:
        await super().parse(message, command)
        if command[0] == "词云":
            res = database.run_command("""SELECT
                                                message.message
                                            FROM
                                                message
                                            WHERE
                                                message.group_id = %s 
                                                AND
                                                DATE(message.send_time) = %s
                                            GROUP BY
                                                message.message""",
                                       [message.group_id, datetime.now().strftime("%Y-%m-%d")],
                                       ReturnType.ALL)
            temp = []
            for message in res:
                temp.append(message[0])
            message = "".join(temp)
            wordcloud_path = join(getcwd(), "image/wordcloud.png")
            MessageWordCloud.wordcloud(message, wordcloud_path)
            with open(wordcloud_path, "rb") as f:
                await message_sender.send_message(self._message.group_id, [Image.of(raw=f.read(), mime="image/png")])
            return Result.of_success()
        return None
