from re import Pattern, compile, search
from typing import Optional

from src.element.message import Message
from src.element.tree import Tree
from src.module.permission_manager import PermissionManager
from src.utils.message_helper import MessageHelper


class PermissionHelper:
    _match_user_id: Pattern = compile(r"\(\d*?\)")
    _permission_manager: PermissionManager

    @classmethod
    def get_permission_manager(cls) -> PermissionManager:
        return cls._permission_manager

    @classmethod
    def init_permission_helper(cls, permission_manager: PermissionManager):
        cls._permission_manager = permission_manager

    @classmethod
    async def require_permission(cls, message: Message, permission: Tree, fail_message: str = "你无权这么做") -> bool:
        if not message.is_command:
            return False
        if cls._permission_manager.check_player_permission(message.sender_id, permission).is_fail:
            await MessageHelper.send_message(message.group_id, fail_message)
            return False
        return True

    @classmethod
    def check_user_permission(cls, user_id: str, permission: str) -> bool:
        return cls._permission_manager.check_player_permission(user_id, permission).is_success

    @classmethod
    def check_group_permission(cls, group_id: str, permission: str) -> bool:
        return cls._permission_manager.check_group_permission(group_id, permission).is_success

    @classmethod
    def check_player(cls, message: Message) -> None:
        cls._permission_manager.create_player(str(message.sender_id))

    @classmethod
    def check_permission_node(cls, permission: str) -> bool:
        return permission in cls._permission_manager.permission_node

    @classmethod
    def get_user_id(cls, command: str) -> Optional[str]:
        if not command.startswith("@"):
            return command
        res = search(cls._match_user_id, command)
        if res is None:
            return None
        return res.group()[1:-1]
