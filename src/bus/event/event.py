from enum import Enum


class Event(Enum):
    pass


class ServerEvent(Event):
    INITIAL = "server_initial"
    STARTING = "server_starting"
    STARTED = "server_started"
    STOPPING = "server_stopping"
    STOPPED = "server_stopped"


class MessageEvent(Event):
    MESSAGE_CREATED = "message_created"
