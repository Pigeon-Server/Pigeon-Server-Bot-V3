from src.database.message_model import Message as MessageModel
from src.element.message import Message


class ModelUtils:
    @staticmethod
    def translate_message_to_model(message: Message) -> MessageModel:
        return MessageModel(
            group_id=message.group_id,
            group_name=message.group_name,
            is_command=message.is_command,
            message=message.message,
            message_id=message.message_id,
            send_time=message.send_time,
            sender_id=message.sender_id,
            sender_name=message.sender_name)
