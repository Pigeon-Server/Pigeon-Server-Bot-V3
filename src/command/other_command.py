from datetime import datetime, timedelta
from os import getcwd
from os.path import join
from re import Pattern, compile, sub
from typing import List, Optional

from satori import Image

from src.base.logger import logger
from src.base.config import config
from src.bot.app import message_sender
from src.bot.database import database
from src.command.command_parser import CommandParser
from src.element.message import Message
from src.element.permissions import Other, Whitelist
from src.element.result import Result
from src.module.message_wordcloud import MessageWordCloud
from src.type.types import ReturnType

pattern: Pattern = compile(r"(\[回复\([\s\S]+\)])?@[\s\S]+\(\d+\)( )?")
wordcloud_path = join(getcwd(), "image/wordcloud.png")


class OtherCommand(CommandParser):
    async def parse(self, message: Message, command: List[str]) -> Optional[Result]:
        await super().parse(message, command)
        if (command_length := len(command)) == 1:
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
                if self._check_permission(Other.Word):
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
                if self._check_permission(Other.Reboot):
                    return self._permission_reject
                if not config.sys_config.dev:
                    await message_sender.send_message(config.config.group_config.admin_group, f"plugin offline")
                exit(0)
            if command[0] == "bot_status":
                if self._check_permission(Other.Status):
                    return self._permission_reject
                await message_sender.send_message(self._message.group_id, f"插件状态:\n"
                                                                          f"运行状态: 正常\n"
                                                                          f"Mcsm模块: 正常\n"
                                                                          f"MySQL状态: 正常")
                return Result.of_success()
        if command_length > 2 and command[0] == "whitelist":
            if command[1] == "add":
                if self._check_permission(Whitelist.Add):
                    return self._permission_reject
                database.run_command("""INSERT INTO `whitelist` (`user`) VALUES (%s)""", [command[2]])
                await message_sender.send_message(self._message.group_id, f"成功为{command[2]}添加白名单")
                return Result.of_success()
            if command[1] == "del":
                if self._check_permission(Whitelist.Del):
                    return self._permission_reject
                database.run_command("""DELETE FROM `whitelist` WHERE `user` = %s""", [command[2]])
                await message_sender.send_message(self._message.group_id, f"成功为{command[2]}移除白名单")
            return Result.of_success()
        return None
