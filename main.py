from satori import Event
from satori.client import Account

from src.base.config import config
from src.base.logger import logger
from src.bot.app import app
from src.bot.database import database
from src.command.command import Command
from src.element.message import Message


@app.register
async def on_message(account: Account, event: Event):
    message = Message(event)
    if not config.sys_config.dev:
        database.insert_message(message.model)
    logger.info(
        f'[消息]<-{message.group_info}-{message.sender_info}:{message.message}')
    await Command.command_parsing(message, account, event)


app.run()
