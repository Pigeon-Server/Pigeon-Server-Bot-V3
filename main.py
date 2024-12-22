from satori import Event
from satori.client import Account

from src.base.config import sys_config
from src.base.event_bus import event_bus
from src.base.logger import logger
from src.bot.app import app
from src.bus.event.event import MessageEvent
from src.element.message import Message
from src.utils.model_utils import ModelUtils
from src.utils.module_utils import dynamic_import, dynamic_import_all

logger.debug("Register command handler...")

dynamic_import_all("src/command", ["command_manager"])

logger.debug("Register event handler...")

dynamic_import_all("src/filter")
dynamic_import("src/module", "block_message")

logger.debug("Initializing message handler...")


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
