from satori import WebsocketsInfo
from satori.client import App

from src.base.config import config
from src.module.reply_message import ReplyManager

app = App(WebsocketsInfo(host=config.config.login_config.host, port=config.config.login_config.port,
                         token=config.config.login_config.token))

reply_manager = ReplyManager(app)
