from typing import Optional

from src.element.tree import Tree
from src.type.types import CommandHandler
from src.utils.utils import random_string


class Command:
    def __init__(self,
                 command: str,
                 command_handler: CommandHandler,
                 command_name: Optional[str] = None,
                 command_require_permission: Optional[Tree] = None,
                 command_docs: Optional[str] = None,
                 command_usage: Optional[str] = None):
        self._command = command
        self._command_name = command_name if command_name else f"{command_handler.__name__}_{random_string(8)}"
        self._command_handler = command_handler
        self._command_require_permission = command_require_permission
        self._command_docs = command_docs or "暂无"
        self._command_usage = command_usage or command

    @property
    def handler(self) -> CommandHandler:
        return self._command_handler

    @property
    def name(self) -> str:
        return self._command_name

    @property
    def permission(self) -> Optional[Tree]:
        return self._command_require_permission

    @property
    def docs(self) -> Optional[str]:
        return self._command_docs

    @property
    def usage(self) -> Optional[str]:
        return self._command_usage

    @property
    def command(self) -> str:
        return self._command
