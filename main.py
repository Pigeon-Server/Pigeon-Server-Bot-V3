from satori import Event
from satori.client import Account

from src.base.config import sys_config
from src.base.logger import logger
from src.bot.app import app
from src.command.command_manager import CommandManager
from src.element.message import Message
from src.utils.model_utils import ModelUtils

logger.debug("Initializing message handler...")


@app.register
async def on_message(_: Account, event: Event):
    message = Message(event)
    if event.self_id == message.sender_id:
        return
    if not sys_config.dev:
        ModelUtils.translate_message_to_model(message).save()
    logger.info(
        f'[消息]<-{message.group_info}-{message.sender_info}:{message.message}')
    await CommandManager.message_listener(message, event)


logger.debug("Bot starting...")
app.run()
