from satori import Event
from satori.client import Account

from src.base.logger import logger
from src.bot.app import app
from src.utils.model_utils import ModelUtils

logger.debug("Register command handler...")

from src.command.mcsm_command import *
from src.command.other_command import *
from src.command.server_list_command import *
from src.command.server_status_command import *
from src.command.permission_command import *

logger.debug("Initializing message handler...")


@app.register
async def on_message(_: Account, event: Event):
    message = Message(event)
    if event.self_id == message.sender_id:
        return
    if not sys_config.dev:
        ModelUtils.translate_message_to_model(message).save(True)
    logger.info(
        f'[消息]<-{message.group_info}-{message.sender_info}:{message.message}')
    await CommandManager.message_listener(message, event)


logger.debug("Bot starting...")
app.run()
