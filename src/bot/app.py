from satori import LoginStatus, WebsocketsInfo
from satori.client import Account, App

from src.base.config import config
from src.base.logger import logger
from src.bot.message import MessageSender
from src.module.reply_message import ReplyManager

app = App(WebsocketsInfo(host=config.config.login_config.host, port=config.config.login_config.port,
                         token=config.config.login_config.token))

reply_manager = ReplyManager(app)

message_sender = MessageSender()


@app.lifecycle
async def on_startup(account: Account, status: LoginStatus):
    if account.self_id == config.config.login_config.qq:
        match status:
            case LoginStatus.CONNECT:
                logger.info(f"{account.self_id} Online")
                message_sender.set_account(account)
                # await account.send_message(config.config.group_config.admin_group, f"Plugin online")
            case LoginStatus.OFFLINE:
                logger.info(f"{account.self_id} Offline")
                # await account.send_message(config.config.group_config.admin_group, f"Plugin offline")
