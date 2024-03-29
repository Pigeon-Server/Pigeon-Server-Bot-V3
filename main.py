from re import Pattern, compile, search, sub

from satori import Event, LoginStatus, WebsocketsInfo
from satori.client import Account, App

from src.base.config import config
from src.base.logger import logger
from src.module.server_status import ServerStatus

app = App(WebsocketsInfo(host=config.config.login_config.host, port=config.config.login_config.port,
                         token=config.config.login_config.token))

server = ServerStatus(config.config.server_list)

face_pattern: Pattern = compile(r"<chronocat:face[\s\S]*?>")
face_name_pattern: Pattern = compile(r"\[[\s\S]*\]")
image_pattern: Pattern = compile(r"<img[\s\S]*?>")
file_pattern: Pattern = compile(r"<file[\s\S]*?>")


@app.register
async def on_message(account: Account, event: Event):
    message = event.message.content
    message = sub(face_pattern, lambda t: search(face_name_pattern, t.group()).group(), message)
    message = sub(image_pattern, "[图片]", message)
    message = sub(file_pattern, "[文件]", message)
    logger.debug(
        f'[消息]<-{event.guild.name}({event.guild.id})-{event.member.nick if event.member.nick else event.user.name}({event.user.id}):{message}')
    if message.startswith("/"):
        if message == "/status" or message == "/info":
            await account.send(event, f"{"-" * 5}Dev{"-" * 5}\n{await server.get_online_player()}")
        if event.guild.id == config.config.group_config.admin_group:
            pass


@app.lifecycle
async def on_startup(account: Account, status: LoginStatus):
    if account.self_id == config.config.login_config.qq and status == LoginStatus.CONNECT:
        logger.info(f"{account.self_id} Online")


app.run()
