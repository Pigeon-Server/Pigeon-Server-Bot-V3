from datetime import datetime
from typing import Optional


class MessageModel:
    message_id: Optional[str]
    sender_id: Optional[str]
    sender_name: Optional[str]
    group_id: Optional[str]
    group_name: Optional[str]
    is_command: Optional[bool]
    message: Optional[str]
    send_time: Optional[datetime]

    def __init__(self, message_id: Optional[str] = None, sender_id: Optional[str] = None,
                 sender_name: Optional[str] = None, group_id: Optional[str] = None,
                 group_name: Optional[str] = None, is_command: Optional[bool] = None,
                 message: Optional[str] = None, send_time: Optional[datetime] = None):
        self.message_id = message_id
        self.sender_id = sender_id
        self.sender_name = sender_name
        self.group_id = group_id
        self.group_name = group_name
        self.is_command = is_command
        self.message = message
        self.send_time = send_time

    @classmethod
    def from_message_id(cls, message_id: str) -> 'MessageModel':
        return cls(message_id=message_id)

    @classmethod
    def from_sender_info(cls, sender_id: str, sender_name: str) -> 'MessageModel':
        return cls(sender_id=sender_id, sender_name=sender_name)

    @classmethod
    def from_group_info(cls, group_id: str, group_name: str) -> 'MessageModel':
        return cls(group_id=group_id, group_name=group_name)

    @classmethod
    def from_database(cls, data: tuple[int, str, str, str, str, str, int, str, datetime]) -> 'MessageModel':
        return cls(data[1], data[2], data[3], data[4],
                   data[5], True if data[6] else False, data[7], data[8])

    @staticmethod
    def insert(model: 'MessageModel') -> tuple[str, list[str]]:
        return (("INSERT INTO `message` (message_id, sender_id, sender_name, "
                 "group_id, group_name, is_command, message, send_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"),
                [model.message_id, model.sender_id, model.sender_name, model.group_id,
                 model.group_name, model.is_command, model.message, model.send_time.strftime("%Y-%m-%dT%H:%M:%S")])

    @staticmethod
    def select(model: 'MessageModel') -> tuple[str, list[str]]:
        if model.message_id is not None:
            return ("SELECT * FROM `message` WHERE `message_id` = %s",
                    [model.message_id])
        if model.sender_id is not None and model.sender_name is not None:
            return ("SELECT * FROM `message` WHERE `sender_id` = %s AND `sender_name` = %s",
                    [model.sender_id, model.sender_name])
        if model.group_id is not None and model.group_name is not None:
            return ("SELECT * FROM `message` WHERE `group_id` = %s AND `group_name` = %s",
                    [model.group_id, model.group_name])

    @staticmethod
    def delete(model: 'MessageModel') -> tuple[str, list[str]]:
        if model.message_id is not None:
            return ("DELETE FROM `message` WHERE `message_id` = %s",
                    [model.message_id])
        if model.sender_id is not None and model.sender_name is not None:
            return ("DELETE FROM `message` WHERE `sender_id` = %s AND `sender_name` = %s",
                    [model.sender_id, model.sender_name])
        if model.group_id is not None and model.group_name is not None:
            return ("DELETE FROM `message` WHERE `group_id` = %s AND `group_name` = %s",
                    [model.group_id, model.group_name])

    @staticmethod
    def update(model: 'MessageModel') -> tuple[str, list[str]]:
        sql = "UPDATE `message` SET "
        args = []
        if model.sender_id is not None:
            sql += "`sender_id` = %s,"
            args.append(model.sender_id)
        if model.sender_name is not None:
            sql += "`sender_name` = %s,"
            args.append(model.sender_name)
        if model.group_name is not None:
            sql += "`group_name` = %s,"
            args.append(model.group_name)
        if model.group_id is not None:
            sql += "`group_id` = %s,"
            args.append(model.group_id)
        if model.is_command is not None:
            sql += "`is_command` = %s,"
            args.append(model.is_command)
        if model.message is not None:
            sql += "`message` = %s,"
            args.append(model.message)
        if model.send_time is not None:
            sql += "`send_time` = %s,"
            args.append(model.send_time.strftime("%Y-%m-%dT%H:%M:%S"))
        sql.removesuffix(',')
        sql += " WHERE `message_id` = %s"
        args.append(model.message_id)
        return sql, args
