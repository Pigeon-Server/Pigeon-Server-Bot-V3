from typing import List, Optional

from src.bot.permission import ps_manager
from src.element.message import Message
from src.element.result import Result
from src.element.tree import Tree


class CommandParser:
    _message: Message
    _permission_reject: Result = Result.of_failure("你无权这么做")

    async def parse(self, message: Message, command: List[str]) -> Optional[Result]:
        self._message = message
        return Result.of_failure("Method not implemented")

    def _check_permission(self, permission: Tree) -> bool:
        return not ps_manager.check_player_permission(self._message.sender_id, permission).is_success
