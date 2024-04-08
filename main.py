from satori import Event
from satori.client import Account

from src.base.logger import logger
from src.bot.app import app
from src.command.command import Command
from src.element.message import Message


@app.register
async def on_message(account: Account, event: Event):
    message = Message(event)
    logger.debug(
        f'[消息]<-{message.group_info}-{message.sender_info}:{message.message}')
    await Command.command_parsing(message, account, event)


app.run()
