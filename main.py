from satori import Event, WebsocketsInfo
from satori.client import Account, App
from src.module.server_status import ServerStatus

app = App(WebsocketsInfo(host='', port=5500,
                         token=''))

server = ServerStatus({
})


@app.register
async def on_message(account: Account, event: Event):
    message = event.message.content
    if message.startswith("/"):
        if message == "/status" or message == "/info":
            await account.send(event, await server.get_online_player())

app.run()
