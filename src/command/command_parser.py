from typing import List

from src.bot.tools import per
from src.module.message import Message
from src.module.result import Result


class CommandParser:
    def __init__(self):
        pass

    async def parse(self, sender: str, command: List[str], message: Message) -> Result:
        return Result.of_failure("Method not implemented")

    @staticmethod
    def check_player(user_id: str, permission: str) -> bool:
        return per.check_player_permission(user_id, permission).is_success
