from os import getcwd, getpid

from satori import LoginStatus, WebsocketsInfo
from satori.client import Account, App

from src.base.config import config
from src.base.logger import logger
from src.bot.message import MessageSender
from src.bot.thread import update_mcsm_info_thread
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
                logger.info(f"Process PID: {getpid()}")
                logger.info(f"Process WorkDir: {getcwd()}")
                logger.success(f"{account.self_id} Online")
            case LoginStatus.OFFLINE:
                logger.success(f"{account.self_id} Offline")
                if not config.sys_config.dev:
                    await account.send_message(config.config.group_config.admin_group, f"plugin offline")
