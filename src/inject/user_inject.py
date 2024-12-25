from typing import Any

from src.base.event_bus import event_bus
from src.bus.event.event import MessageEvent
from src.database.message_model import Message
from src.database.user_model import User


@event_bus.on_event_inject(MessageEvent.MESSAGE_CREATED)
def inject_user(message: Message, *_, **__) -> dict[str, Any]:
    return {"user": User.get_or_create(message)}
