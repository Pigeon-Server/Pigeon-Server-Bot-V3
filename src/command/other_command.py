from datetime import datetime, timedelta
from os import getcwd
from os.path import join
from re import Pattern, compile, sub
from typing import List, Optional

from satori import Image

from src.base.config import config
from src.bot.app import message_sender
from src.bot.database import database
from src.bot.permission import ps_manager
from src.command.command_parser import CommandParser
from src.element.message import Message
from src.element.permissions import Other
from src.element.result import Result
from src.module.message_wordcloud import MessageWordCloud
from src.type.types import ReturnType

pattern: Pattern = compile(r"(\[回复\([\s\S]+\)])?@[\s\S]+\(\d+\)( )?")
wordcloud_path = join(getcwd(), "image/wordcloud.png")


class OtherCommand(CommandParser):
    async def parse(self, message: Message, command: List[str]) -> Optional[Result]:
        await super().parse(message, command)
        if command[0] == "word":
            match len(command):
                case 1:
                    time = datetime.now().strftime("%Y-%m-%d")
                case 2:
                    time = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d") \
                        if command[1] == "last" else command[1]
                case 3:
                    time = (datetime.now() - timedelta(days=int(command[2]))).strftime("%Y-%m-%d") \
                        if command[1] == "last" else command[1]
            if ps_manager.check_player_permission(self._message.sender_id, Other.Word).is_fail:
                return self._permission_reject
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
                                       [message.group_id, time],
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
            MessageWordCloud.wordcloud(message, wordcloud_path)
            await message_sender.send_message(self._message.group_id, f"以下为日期{time}的图云")
            with open(wordcloud_path, "rb") as f:
                await message_sender.send_message(self._message.group_id,
                                                  [Image.of(raw=f.read(), mime="image/png")])
            return Result.of_success()
        if command[0] == "reboot":
            if ps_manager.check_player_permission(self._message.sender_id, Other.Reboot).is_fail:
                return self._permission_reject
            if not config.sys_config.dev:
                await message_sender.send_message(config.config.group_config.admin_group, f"plugin offline")
            exit(0)
        return None
