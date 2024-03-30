from satori import Event, LoginStatus, WebsocketsInfo
from satori.client import Account, App

from src.base.config import config
from src.base.logger import logger
from src.module.command import Command
from src.module.message import Message

app = App(WebsocketsInfo(host=config.config.login_config.host, port=config.config.login_config.port,
                         token=config.config.login_config.token))


@app.register
async def on_message(account: Account, event: Event):
    message = Message(event)
    logger.debug(
        f'[消息]<-{message.group_info}-{message.sender_info}:{message.message}')
    await Command.command_parsing(message, account, event)


@app.lifecycle
async def on_startup(account: Account, status: LoginStatus):
    if account.self_id == config.config.login_config.qq:
        match status:
            case LoginStatus.CONNECT:
                logger.info(f"{account.self_id} Online")
                # await account.send_message(config.config.group_config.admin_group, f"Plugin online")
            case LoginStatus.OFFLINE:
                logger.info(f"{account.self_id} Offline")
                # await account.send_message(config.config.group_config.admin_group, f"Plugin offline")


app.run()
