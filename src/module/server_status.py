from mcstatus import JavaServer

from src.base.logger import logger
from src.bot.database import database
from src.exception.exception import IncomingParametersError, NoParametersError
from src.type.types import ReturnType


class ServerStatus:
    _server: dict
    _output_message: str
    _player_online: int = 0
    _player_max: int = 0

    def __init__(self) -> None:
        self.reload_server_list()

    def reload_server_list(self) -> None:
        self._server = self.get_server_list()

    @staticmethod
    def get_server_list() -> dict:
        res = database.run_command("""SELECT `server_name`, `server_ip` FROM server_list WHERE `enable` = 1;""",
                                   return_type=ReturnType.ALL)
        server_list = {}
        for server in res:
            server_list[server[0]] = server[1]
        return server_list

    async def _check_server(self, full: bool = False) -> None:
        self._output_message = "[服务器状态]\n在线人数: {online}/{max}\n在线玩家列表: \n"
        self._player_max = 0
        self._player_online = 0
        server_name: str
        for raw in self._server:
            server_name = raw
            try:
                server_status = JavaServer.lookup(self._server[raw]).status()
                self._player_max += server_status.players.max
                self._player_online += server_status.players.online
                output_message = server_name + f"({server_status.players.online}): "
                if server_status.players.sample is None or len(server_status.players.sample) == 0:
                    output_message += ""
                else:
                    count = 0
                    for player in server_status.players.sample:
                        count += 1
                        output_message += f"[{player.name}] "
                        if count == 10 and not full:
                            output_message += " ... "
                            break
                output_message += "\n"
                self._output_message += output_message
                del server_status, output_message
            except Exception as error:
                logger.error(server_name)
                logger.error(error)
                self._output_message += server_name + "(0): 服务器连接失败\n"
            del server_name

    async def get_online_player(self, full: bool = False) -> str:
        await self._check_server(full)
        return self._output_message.format(online=self._player_online, max=self._player_max).removesuffix("\n")
