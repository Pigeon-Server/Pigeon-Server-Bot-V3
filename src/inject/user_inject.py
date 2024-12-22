from typing import Any

from src.base.event_bus import event_bus
from src.bus.event.event import MessageEvent
from src.database.message_model import Message
from src.database.punish_model import Punishment


@event_bus.on_event_inject(MessageEvent.MESSAGE_CREATED)
def check_user_exist(message: Message, *_, **__) -> dict[str, Any]:
    return {"user": Punishment.get_or_create(message)}
