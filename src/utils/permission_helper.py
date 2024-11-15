from src.element.message import Message
from src.element.tree import Tree
from src.module.permission_manager import PermissionManager
from src.utils.message_sender import MessageSender


class PermissionHelper:
    _permission_manager: PermissionManager

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
    def check_player(message: Message) -> None:
        PermissionHelper._permission_manager.create_player(str(message.sender_id))
