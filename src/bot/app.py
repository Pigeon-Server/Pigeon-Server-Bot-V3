from os import getcwd
from os.path import join
from threading import Thread
from time import sleep

from satori import LoginStatus, WebsocketsInfo
from satori.client import Account, App

from src.base.config import config
from src.base.logger import logger
from src.bot.mcsm import mcsm
from src.bot.message import MessageSender
from src.element.permissions import Root
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


def update_mcsm_info_thread_handler():
    while True:
        logger.debug("Update MCSM info")
        mcsm.update_instance_status()
        sleep(config.config.mcsm_config.update_time)


update_mcsm_info_thread = Thread(target=update_mcsm_info_thread_handler, daemon=True)


@app.lifecycle
async def on_startup(account: Account, status: LoginStatus):
    if account.self_id == config.config.login_config.qq:
        match status:
            case LoginStatus.CONNECT:
                logger.info(f"{account.self_id} Online")
                message_sender.set_account(account)
                update_mcsm_info_thread.start()
                if not config.sys_config.dev:
                    await account.send_message(config.config.group_config.admin_group, f"plugin online")
                logger.info("\n  _____  _                               _____                               \n"
                            " |  __ \\(_)                             / ____|                              \n"
                            " | |__) |_   __ _   ___   ___   _ __   | (___    ___  _ __ __   __ ___  _ __ \n"
                            " |  ___/| | / _` | / _ \\ / _ \\ | '_ \\   \\___ \\  / _ \\| '__|\\ \\ / // _ \\| '__|\n"
                            " | |    | || (_| ||  __/| (_) || | | |  ____) ||  __/| |    \\ V /|  __/| |   \n"
                            " |_|    |_| \\__, | \\___| \\___/ |_| |_| |_____/  \\___||_|     \\_/  \\___||_|   \n"
                            "             __/ |                                                           \n"
                            "            |___/                                                            "
                            "\n\n[Github源码库地址，欢迎贡献&完善&Debug]\nhttps://github.com/Pigeon-Server/Pigeon-Server-Bot-V3")
            case LoginStatus.OFFLINE:
                logger.info(f"{account.self_id} Offline")
                if not config.sys_config.dev:
                    await account.send_message(config.config.group_config.admin_group, f"plugin offline")
