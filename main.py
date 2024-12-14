from satori import Event
from satori.client import Account

from src.base.logger import logger
from src.bot.app import app
from src.utils.model_utils import ModelUtils

logger.debug("Register command handler...")

from src.command.command import *

logger.debug("Initializing message handler...")


async def message_logger(message: Message, **_) -> None:
    logger.info(f'[消息]<-{message.group_info}-{message.sender_info}:{message.message}')


event_bus.add_aspect(MessageEvent.MESSAGE_CREATED, message_logger)


@app.register
async def on_message(_: Account, event: Event):
    message = Message(event)
    if event.self_id == message.sender_id:
        return
    if not sys_config.dev:
        ModelUtils.translate_message_to_model(message).save(True)
    await event_bus.publish(MessageEvent.MESSAGE_CREATED, message, event)


logger.debug("Bot starting...")
app.run()
