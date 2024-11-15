from re import Pattern, compile, search
from typing import Optional

from src.element.message import Message
from src.element.tree import Tree
from src.module.permission_manager import PermissionManager
from src.utils.message_sender import MessageSender


class PermissionHelper:
    _match_user_id: Pattern = compile(r"\(\d*?\)")
    _permission_manager: PermissionManager

    @staticmethod
    def get_permission_manager() -> PermissionManager:
        return PermissionHelper._permission_manager

    @staticmethod
    def init_permission_helper(permission_manager: PermissionManager):
        PermissionHelper._permission_manager = permission_manager

    @staticmethod
    def require_permission(message: Message, permission: Tree, fail_message: str = "你无权这么做") -> bool:
        if not message.is_command:
            return False
        if PermissionHelper._permission_manager.check_player_permission(message.sender_id, permission).is_fail:
            MessageSender.send_message(message.group_id, fail_message)
            return False
        return True

    @staticmethod
    def check_user_permission(user_id: str, permission: str) -> bool:
        return PermissionHelper._permission_manager.check_player_permission(user_id, permission).is_success

    @staticmethod
    def check_group_permission(group_id: str, permission: str) -> bool:
        return PermissionHelper._permission_manager.check_group_permission(group_id, permission).is_success

    @staticmethod
    def check_player(message: Message) -> None:
        PermissionHelper._permission_manager.create_player(str(message.sender_id))

    @staticmethod
    def check_permission_node(permission: str) -> bool:
        return permission in PermissionHelper._permission_manager.permission_node

    @staticmethod
    def get_user_id(command: str) -> Optional[str]:
        if not command.startswith("@"):
            return command
        res = search(PermissionHelper._match_user_id, command)
        if res is None:
            return None
        return res.group()[1:-1]
