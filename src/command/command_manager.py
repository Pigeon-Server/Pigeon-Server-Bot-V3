from itertools import zip_longest
from typing import Callable, Dict, Optional, Union

from satori import Event, Image

from src.base.logger import logger
from src.element.command import Command
from src.element.message import Message
from src.element.result import Result
from src.element.tree import Tree
from src.exception.exception import CustomError
from src.type.types import CommandHandler
from src.utils.command_utils import command_split
from src.utils.image_utils import text_to_image
from src.utils.message_sender import MessageSender
from src.utils.permission_helper import PermissionHelper


class CommandManager:
    _command_tree = Tree("/")
    _command_store: Dict[Tree, Command] = {}

    @staticmethod
    def register_command(command: str, alias_list: list[str]) -> Tree:
        command_parts = command_split(command)
        current_node = CommandManager._command_tree
        alias_lists: list[list[str]] = [command_split(alias) for alias in alias_list]

        for part, *alias in zip_longest(command_parts, *alias_lists):
            child_found = False
            for child in current_node.children:
                if child.root == part:
                    current_node = child
                    child_found = True
                    break

            if not child_found:
                new_node = Tree(part)
                current_node.insert(new_node)
                current_node = new_node
            if alias:
                current_node.add_alias(alias)

        return current_node

    @staticmethod
    def add_command(command: Union[str, Command],
                    command_name: Optional[str] = None,
                    command_require_permission: Optional[Tree] = None,
                    command_docs: Optional[str] = None,
                    command_usage: Optional[str] = None,
                    *,
                    alia_list: Optional[list[str]] = None) -> Optional[Callable]:
        if alia_list is None:
            alia_list = []
        if isinstance(command, Command):
            command_node = CommandManager.register_command(command.command, alia_list)
            CommandManager._command_store[command_node] = command
            logger.debug(f"Register command {command.command}, register name: {command.name}")
            return None

        def decorator(func: CommandHandler):
            command_instance = Command(command, func, command_name,
                                       command_require_permission, command_docs,
                                       command_usage)
            node = CommandManager.register_command(command, alia_list)
            CommandManager._command_store[node] = command_instance
            logger.debug(f"Register command {command}, register name: {command_instance.name}")

        return decorator

    @staticmethod
    async def message_listener(message: Message, event: Event) -> None:
        if not message.is_command:
            return
        try:
            command = command_split(message)
        except CustomError as e:
            logger.error(e)
            await MessageSender.send_message(event, f"无法解析此命令,{e.info}")
            return

        if command is None:
            return

        PermissionHelper.check_player(message)

        result = await CommandManager.parse_command(message, command)
        if result and result.has_message:
            await MessageSender.send_message(event, result.message)

    @staticmethod
    async def parse_command(message: Message, command: list[str]) -> Optional[Result]:
        try:
            command_node = CommandManager._command_tree.get_node(command, match_most=True)
            if command_node == CommandManager._command_tree:
                return Result.of_failure(f"未知命令 {message.message}")
            command_instance = CommandManager._command_store[command_node]
            if (command_instance.permission and
                    not PermissionHelper.require_permission(message, command_instance.permission)):
                return None
            result = await command_instance.handler(message, command)
            if result is None:
                return Result.of_failure(command_instance.usage)
            return result
        except Exception as e:
            logger.error(e)
            return Result.of_failure(f"An error occurred while handling command: {e}")

    @staticmethod
    async def help_command(_: Message, command: list[str]) -> Optional[Result]:
        require_command = command[1:]
        command_node = CommandManager._command_tree.get_node(require_command)
        if command_node is None:
            return Result.of_failure(f"无法找到该命令{require_command}")
        command_instance = CommandManager._command_store[command_node]
        return Result.of_success(f"命令：{command_instance.command}\n"
                                 f"注册名：{command_instance.name}\n"
                                 f"使用：{command_instance.usage}\n"
                                 f"文档：{command_instance.docs}")

    @staticmethod
    async def command_list(message: Message, _: list[str]) -> Optional[Result]:
        text_to_image(Tree.get_tree(CommandManager._command_tree), "./image/command_list.png")
        with open("./image/command_list.png", "rb") as f:
            await MessageSender.send_message(message.group_id,
                                             [Image.of(raw=f.read(), mime="image/png")])
        return Result.of_success()


help_command = Command("/help", CommandManager.help_command)
CommandManager.add_command(help_command)

command_list = Command("/command list", CommandManager.command_list)
CommandManager.add_command(command_list)
