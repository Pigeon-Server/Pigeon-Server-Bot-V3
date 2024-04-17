from datetime import datetime

from src.model.model import Model


class MessageModel(Model):
    _message_id: str
    _sender_id: str
    _sender_name: str
    _group_id: str
    _group_name: str
    _message: str
    _send_time: str

    def __init__(self, message_id: str, sender_id: str, sender_name: str, group_id: str,
                 group_name: str, message: str, send_time: str):
        self._message_id = message_id
        self._sender_id = sender_id
        self._sender_name = sender_name
        self._group_id = group_id
        self._group_name = group_name
        self._message = message
        self._send_time = send_time

    def insert(self) -> tuple[str, list[str]]:
        return (("INSERT INTO `message` (message_id, sender_id, sender_name, "
                 "group_id, group_name, message, send_time) VALUES (%s, %s, %s, %s, %s, %s, %s)"),
                [self._message_id, self._sender_id, self._sender_name,
                 self._group_id, self._group_name, self._message, self._send_time])

    def select(self) -> tuple[str, list[str]]:
        pass

    def delete(self) -> tuple[str, list[str]]:
        pass

    def update(self) -> tuple[str, list[str]]:
        pass

    @property
    def message_id(self) -> str:
        return self._message_id

    @property
    def sender_id(self) -> str:
        return self._sender_id

    @property
    def sender_name(self) -> str:
        return self._sender_name

    @property
    def group_id(self) -> str:
        return self._group_id

    @property
    def group_name(self) -> str:
        return self._group_name

    def __repr__(self):
        return f"MessageModel(message_id={self._message_id})"
