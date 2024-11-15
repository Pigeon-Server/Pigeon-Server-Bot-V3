from typing import Callable, Dict, Optional, Union

from satori import Event

from src.base.logger import logger
from src.element.command import Command
from src.element.message import Message
from src.element.result import Result
from src.element.tree import Tree
from src.exception.exception import CustomError
from src.type.types import CommandHandler
from src.utils.command_utils import command_split
from src.utils.message_sender import MessageSender
from src.utils.permission_helper import PermissionHelper


class CommandManager:
    _command_tree = Tree("/")
    _command_store: Dict[Tree, Command] = {}

    @staticmethod
    def register_command(command: str) -> Tree:
        command_parts = command_split(command)
        current_node = CommandManager._command_tree

        for part in command_parts:
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
            command_node = CommandManager.register_command(command.command)
            CommandManager._command_store[command_node] = command
            logger.debug(f"Register command {command.command}, register name: {command.name}")
            for alias in alia_list:
                logger.debug(f"Register alias {alias} for command {command.command}")
                command_node = CommandManager.register_command(alias)
                CommandManager._command_store[command_node] = command
            return None

        def decorator(func: CommandHandler):
            command_instance = Command(command, func, command_name,
                                       command_require_permission, command_docs,
                                       command_usage)
            node = CommandManager.register_command(command)
            CommandManager._command_store[node] = command_instance
            logger.debug(f"Register command {command}, register name: {command_instance.name}")
            for alias_ in alia_list:
                logger.debug(f"Register alias {alias_} for command {command}")
                node = CommandManager.register_command(alias_)
                CommandManager._command_store[node] = command_instance

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

        await CommandManager.parse_command(message, command)

    @staticmethod
    async def parse_command(message: Message, command: list[str]):
        try:
            command_node = CommandManager._command_tree.get_node(command, match_most=True)
            command_instance = CommandManager._command_store[command_node]
            if (command_instance.permission and
                    not PermissionHelper.require_permission(message, command_instance.permission)):
                return None
            result = await command_instance.handler(message, command)
            if result and result.has_message:
                await MessageSender.send_message(message.group_id, result.message)
        except Exception as e:
            logger.error(e)
            await MessageSender.send_message(message.group_id, f"An error occurred while handling command: {e}")

    @staticmethod
    async def help_command(message: Message, command: list[str]) -> Result:
        require_command = command[1:]
        command_node = CommandManager._command_tree.get_node(require_command)
        if command_node is None:
            return Result.of_failure(f"无法找到该命令{require_command}")
        command_instance = CommandManager._command_store[command_node]
        return Result.of_success(f"命令：{command_instance.command}\n"
                                 f"注册名：{command_instance.name}\n"
                                 f"使用：{command_instance.usage}\n"
                                 f"文档：{command_instance.docs}")


help_command = Command("/help", CommandManager.help_command)
CommandManager.add_command(help_command)
