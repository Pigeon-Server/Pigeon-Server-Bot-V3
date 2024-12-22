from typing import Union

from src.base.logger import logger
from src.bus.event.event import Event
from src.bus.event_bus import EventBus

event_bus = EventBus()


@event_bus.on_global_event_filter()
async def event_logger(event_type: Union[Event, str], *args, **kwargs) -> None:
    logger.trace(f"Event type: {event_type}, Args: {args}, Kwargs: {kwargs}")
