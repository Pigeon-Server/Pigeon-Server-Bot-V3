from os import getcwd
from os.path import join

from satori import Image, LoginStatus, WebsocketsInfo
from satori.client import Account, App

from src.base.config import config
from src.base.logger import logger
from src.bot.message import MessageSender
from src.module.permissions import Root
from src.module.reply_message import ReplyManager
from src.utils.file_utils import check_directory, check_file, text_to_image

app = App(WebsocketsInfo(host=config.config.login_config.host, port=config.config.login_config.port,
                         token=config.config.login_config.token))

reply_manager = ReplyManager(app)

message_sender = MessageSender()

image_dir = join(getcwd(), "image")
permission_image_dir = join(image_dir, "permissions.png")
check_directory(image_dir, True)
if not check_file(permission_image_dir):
    text_to_image(Root.instance, permission_image_dir)


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
