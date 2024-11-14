from os import getcwd, getpid

from satori import LoginStatus, WebsocketsInfo
from satori.client import Account, App

from src.base.config import main_config, sys_config
from src.base.logger import logger
from src.bot.thread import update_mcsm_info_thread
from src.utils.life_cycle_manager import LifeCycleEvent, LifeCycleManager
from src.utils.message_sender import MessageSender
from src.utils.reply_message import ReplyMessageSender

LifeCycleManager.emit_life_cycle_event(LifeCycleEvent.STARTING)

logger.debug("Initializing Bot...")

logger.debug("Initializing App...")
app = App(WebsocketsInfo(host=main_config.login_config.host, port=main_config.login_config.port,
                         token=main_config.login_config.token))

ReplyMessageSender.set_app(app)


@app.lifecycle
async def on_startup(account: Account, status: LoginStatus):
    if account.self_id == main_config.login_config.qq:
        match status:
            case LoginStatus.CONNECT:
                LifeCycleManager.emit_life_cycle_event(LifeCycleEvent.STARTED)
                MessageSender.set_account(account)
                update_mcsm_info_thread.start()
                if not sys_config.dev:
                    await MessageSender.send_message(main_config.group_config.admin_group, f"plugin online")
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
                LifeCycleManager.emit_life_cycle_event(LifeCycleEvent.STOPPING)
                logger.success(f"{account.self_id} Offline")
                if not sys_config.dev:
                    await account.send_message(main_config.group_config.admin_group, f"plugin offline")
                LifeCycleManager.emit_life_cycle_event(LifeCycleEvent.STOPPED)


logger.debug("Bot initialized, ready to start.")
