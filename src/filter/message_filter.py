from src.base.event_bus import event_bus
from src.base.logger import logger
from src.bus.event.event import MessageEvent
from src.element.message import Message


@event_bus.on_event_filter(MessageEvent.MESSAGE_CREATED)
def message_logger(message: Message, *_, **__) -> None:
    logger.info(f'[消息]<-{message.group_info}-{message.sender_info}:{message.message}')
