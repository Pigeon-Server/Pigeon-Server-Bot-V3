from typing import List, Optional

from src.bot.plugin import ps_manager
from src.element.message import Message
from src.element.result import Result
from src.element.tree import Tree


class CommandParser:
    _message: Message
    _permission_reject: Result = Result.of_failure("你无权这么做")

    @staticmethod
    async def parse(message: Message, command: List[str]) -> Optional[Result]:
        CommandParser._message = message
        return Result.of_failure("Method not implemented")

    @staticmethod
    def _check_permission(permission: Tree) -> bool:
        return not ps_manager.check_player_permission(CommandParser._message.sender_id, permission).is_success
