from enum import Enum


class Event(Enum):
    pass


class ServerEvent(Event):
    INITIAL = "server_initial"
    STARTING = "server_starting"
    STARTED = "server_started"
    STOPPING = "server_stopping"
    STOPPED = "server_stopped"


class OperationEvent(Event):
    USER_MUTE = "user_mute"
    USER_UNMUTE = "user_unmute"


class MessageEvent(Event):
    MESSAGE_CREATED = "message_created"
    MESSAGE_DELETED = "message_deleted"
    MESSAGE_UPDATED = "message_updated"
