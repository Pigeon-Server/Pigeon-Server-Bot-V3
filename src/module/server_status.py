from re import sub

from mcstatus import JavaServer

from src.base.logger import logger
from src.database.server_model import ServerList


class ServerStatus:
    _server: dict

    def __init__(self) -> None:
        self.reload_server_list()

    def reload_server_list(self) -> None:
        self._server = self.get_server_list()

    @staticmethod
    def get_server_list() -> dict:
        return {server.server_name: server.server_ip for server in
                ServerList.select().where(ServerList.enable == 1).order_by(ServerList.priority.desc())}

    @staticmethod
    def check_ip(ip: str) -> str:
        try:
            server = JavaServer.lookup(ip)
            server_status = server.status()
            players = server_status.players
            version = server_status.version
            return (f"Server Version: {version.name}\n"
                    f"Server IP: {ip}\n"
                    f"Server Desc: {sub(r'§\w', '', server_status.description).replace("\n", " ")}\n"
                    f"Server Ping: {server_status.latency:.2f}ms\n"
                    f"Server Player: {players.online}/{players.max}\n"
                    f"Server Players: {'No data' if players.sample is None else ','.join([player.name for player in players.sample])}")
        except Exception as error:
            logger.error(f"Can't connect to server: {ip}")
            logger.error(error)
            return f"Can't connect to server: {ip}"

    def get_online_player(self, full: bool = False) -> str:
        output_message = ["[服务器状态]", "", "在线玩家列表: "]
        player_max = 0
        player_online = 0
        for server_name in self._server:
            try:
                server_status = JavaServer.lookup(self._server[server_name]).status()
                player_max += server_status.players.max
                player_online += server_status.players.online
                message = f"{server_name}({server_status.players.online}): "
                if server_status.players.sample:
                    if full:
                        message += f"{','.join([player.name for player in server_status.players.sample])}"
                    else:
                        message += (f"{','.join([player.name for player in server_status.players.sample[:10]])}"
                                    f"{' ... ' if len(server_status.players.sample) > 10 else ''}")
                output_message.append(message)
            except Exception as error:
                logger.error(f"Can't check server: {server_name}")
                logger.error(error)
                output_message.append(f"{server_name}(0): 服务器连接失败")

        output_message[1] = f"在线人数: {player_online}/{player_max}"
        return "\n".join(output_message)
