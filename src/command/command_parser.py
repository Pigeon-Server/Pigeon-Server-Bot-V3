from typing import List, Optional

from src.bot.tools import per
from src.module.message import Message
from src.module.result import Result


class CommandParser:
    _message: Message

    async def parse(self, message: Message, command: List[str]) -> Optional[Result]:
        self._message = message
        return Result.of_failure("Method not implemented")

    @staticmethod
    def check_player(user_id: str, permission: str) -> bool:
        return per.check_player_permission(user_id, permission).is_success
