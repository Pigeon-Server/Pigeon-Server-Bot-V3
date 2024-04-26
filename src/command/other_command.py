from os import getcwd
from os.path import join
from typing import List, Optional
from datetime import datetime
from re import Pattern, compile, sub

from satori import Image

from src.bot.app import message_sender
from src.bot.database import database
from src.command.command_parser import CommandParser
from src.element.message import Message
from src.element.result import Result
from src.module.message_wordcloud import MessageWordCloud
from src.type.types import ReturnType

pattern: Pattern = compile(r"(\[回复\([\s\S]+\)])?@[\s\S]+\(\d+\)( )?")


class OtherCommand(CommandParser):
    async def parse(self, message: Message, command: List[str]) -> Optional[Result]:
        await super().parse(message, command)
        if command[0] == "word":
            res = database.run_command("""SELECT
                                                message.message
                                            FROM
                                                message
                                            WHERE
                                                message.is_command = FALSE
                                                AND
                                                message.group_id = %s 
                                                AND
                                                DATE(message.send_time) = %s
                                            GROUP BY
                                                message.message""",
                                       [message.group_id, datetime.now().strftime("%Y-%m-%d")],
                                       ReturnType.ALL)
            temp = []
            for message in res:
                tmp: str = (message[0]
                            .replace("[图片]", "")
                            .replace("[语音]", "")
                            .replace("[视频]", "")
                            .replace("[文件]", ""))
                tmp = sub(pattern, "", tmp)
                if tmp == "":
                    continue
                temp.append(tmp)
            message = "".join(temp)
            wordcloud_path = join(getcwd(), "image/wordcloud.png")
            MessageWordCloud.wordcloud(message, wordcloud_path)
            with open(wordcloud_path, "rb") as f:
                await message_sender.send_message(self._message.group_id, [Image.of(raw=f.read(), mime="image/png")])
            return Result.of_success()
        return None
