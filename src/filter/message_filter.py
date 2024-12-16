from src.base.event_bus import event_bus
from src.base.logger import logger
from src.bus.event.event import MessageEvent
from src.element.message import Message
from src.module.blockmessage import BlockMessage


def message_logger(message: Message, *_, **__) -> None:
    logger.info(f'[消息]<-{message.group_info}-{message.sender_info}:{message.message}')


event_bus.add_filter(MessageEvent.MESSAGE_CREATED, message_logger)
event_bus.add_filter(MessageEvent.MESSAGE_CREATED, BlockMessage.checkMessage)
