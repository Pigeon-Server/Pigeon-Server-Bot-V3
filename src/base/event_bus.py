from typing import Union

from src.base.logger import logger
from src.bus.event.event import Event
from src.bus.event_bus import EventBus

event_bus = EventBus()


async def log_aspect(event_type: Union[Event, str], *args, **kwargs) -> None:
    logger.trace(f"Event type: {event_type}, Args: {args}, Kwargs: {kwargs}")


event_bus.add_global_aspect(log_aspect)
