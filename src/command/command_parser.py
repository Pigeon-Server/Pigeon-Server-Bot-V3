from typing import List, Optional

from src.bot.tools import ps_manager
from src.element.message import Message
from src.element.result import Result
from src.element.tree import Tree


class CommandParser:
    _message: Message

    async def parse(self, message: Message, command: List[str]) -> Optional[Result]:
        self._message = message
        return Result.of_failure("Method not implemented")

    @staticmethod
    def check_player(user_id: str, permission: Tree) -> bool:
        return ps_manager.check_player_permission(user_id, permission).is_success
