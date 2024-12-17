from os import getcwd
from os import getcwd
from os.path import join
from re import Pattern, compile
from typing import Optional

from src.base.config import main_config, sys_config
from src.command.command_manager import CommandManager
from src.database.server_model import Whitelist as WhitelistModel
from src.element.message import Message
from src.element.permissions import Other, Whitelist
from src.element.result import Result
from src.utils.message_helper import MessageHelper

pattern: Pattern = compile(r"(\[回复\([\s\S]+\)])?@[\s\S]+\(\d+\)( )?")
wordcloud_path = join(getcwd(), "image/wordcloud.png")


@CommandManager.register_command("/bot restart",
                                 command_require_permission=Other.Reboot,
                                 command_docs="重启插件")
async def bot_restart(_: Message, __: list[str]) -> None:
    if not sys_config.dev:
        await MessageHelper.send_message(main_config.group_config.admin_group, f"plugin offline")
    exit(0)


@CommandManager.register_command("/bot status",
                                 command_require_permission=Other.Status,
                                 command_docs="插件状态")
async def bot_status(_: Message, __: list[str]) -> Optional[Result]:
    return Result.of_success(f"插件状态:\n"
                             f"运行状态: 正常\n"
                             f"Mcsm模块: 正常\n"
                             f"MySQL状态: 正常")


@CommandManager.register_command("/whitelist add",
                                 command_require_permission=Whitelist.Add,
                                 command_docs="添加白名单")
async def whitelist_add(_: Message, command: list[str]) -> Optional[Result]:
    WhitelistModel.create(user=command[2])
    return Result.of_success(f"成功为{command[2]}添加白名单")


@CommandManager.register_command("/whitelist remove",
                                 command_require_permission=Whitelist.Del,
                                 command_docs="移除白名单")
async def whitelist_remove(_: Message, command: list[str]) -> Optional[Result]:
    WhitelistModel.get(WhitelistModel.user == command[2]).delete_instance()
    return Result.of_success(f"成功为{command[2]}移除白名单")
