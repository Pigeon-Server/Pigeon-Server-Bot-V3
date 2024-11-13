from datetime import datetime, timedelta
from os import getcwd
from os.path import join
from re import Pattern, compile, sub
from typing import List, Optional

from peewee import fn
from satori import Image

from src.base.config import config
from src.bot.app import message_sender
from src.database.server_model import Whitelist as WhitelistModel
from src.database.message_model import Message as MessageModel
from src.command.command_parser import CommandParser
from src.element.message import Message
from src.element.permissions import Other, Whitelist
from src.element.result import Result
from src.module.message_wordcloud import MessageWordCloud

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
                res: list[MessageModel] = (MessageModel.select(MessageModel.message)
                                           .where((MessageModel.is_command == 0) &
                                                  (MessageModel.group_id == message.group_id) &
                                                  (fn.DATE(MessageModel.send_time) == time)))
                temp = []
                for message in res:
                    tmp: str = (message.message
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
                WhitelistModel.create(user=command[2])
                await message_sender.send_message(self._message.group_id, f"成功为{command[2]}添加白名单")
                return Result.of_success()
            if command[1] == "del":
                if self._check_permission(Whitelist.Del):
                    return self._permission_reject
                WhitelistModel.get(WhitelistModel.user == command[2]).delete_instance()
                await message_sender.send_message(self._message.group_id, f"成功为{command[2]}移除白名单")
            return Result.of_success()
        return None
