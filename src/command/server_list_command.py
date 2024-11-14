from typing import List, Optional

from peewee import DoesNotExist

from src.bot.plugin import server
from src.command.command_parser import CommandParser
from src.database.server_model import ServerList as ServerListModel
from src.element.message import Message
from src.element.permissions import ServerList
from src.element.result import Result


class ServerListCommand(CommandParser):
    _command_helper: Result = Result.of_failure("服务器状态：\n"
                                                "/serverlist add (ServerName) (ServerIp) [weight]添加一个服务器\n"
                                                "/serverlist del (ServerName) 删除某个服务器\n"
                                                "/serverlist enable (ServerName) 开启某个服务器的状态查询\n"
                                                "/serverlist disable (ServerName) 关闭某个服务器的状态查询\n"
                                                "/serverlist rename (ServerName) (NewName) 修改某个服务器名称\n"
                                                "/serverlist modify (ServerName) (NewServerIp) 修改某个服务器ip\n"
                                                "/serverlist weight (ServerName) (weight) 修改服务器权重"
                                                "/serverlist reload 重载服务器列表\n"
                                                "/serverlist list 列出所有服务器")

    def __init__(self):
        super().__init__()

    @staticmethod
    def check_server_exists(server_name: str) -> Optional[ServerListModel]:
        try:
            return ServerListModel.get(server_name=server_name)
        except DoesNotExist:
            return None

    async def parse(self, message: Message, command: List[str]) -> Optional[Result]:
        await super().parse(message, command)
        res = await self.handle(command)
        server.reload_server_list()
        return res

    async def handle(self, command: List[str]) -> Optional[Result]:
        command_length = len(command)
        if command[0] not in ["serverlist", "sl"]:
            return None
        if command_length < 2:
            return self._command_helper
        match command[1]:
            case "list" | "l":
                if self._check_permission(ServerList.List):
                    return self._permission_reject
                return Result.of_success("\n".join([str(item) for item in ServerListModel.select()]))
            case "add" | "a":
                if command_length < 4 or command_length > 5:
                    return Result.of_failure()
                if self._check_permission(ServerList.Add):
                    return self._permission_reject
                if self.check_server_exists(command[2]) is not None:
                    return Result.of_failure(f"服务器「{command[2]}」已存在")
                server_list: ServerListModel = ServerListModel(server_name=command[2], server_ip=command[3])
                if command_length == 5:
                    server_list.priority = int(command[4])
                server_list.save()
                return Result.of_success(f"成功添加服务器「{command[2]}」，服务器IP：{command[3]}")
            case "del" | "d":
                if command_length < 3:
                    return Result.of_failure()
                if self._check_permission(ServerList.Del):
                    return self._permission_reject
                if (server_list := self.check_server_exists(command[2])) is None:
                    return Result.of_failure(f"不存在服务器「{command[2]}」")
                server_list.delete_instance()
                return Result.of_success(f"成功移除服务器「{command[2]}」")
            case "enable" | "e":
                if command_length < 3:
                    return Result.of_failure()
                if self._check_permission(ServerList.Enable):
                    return self._permission_reject
                if (server_list := self.check_server_exists(command[2])) is None:
                    return Result.of_failure(f"不存在服务器「{command[2]}」")
                server_list.enable = True
                server_list.save()
                return Result.of_success(f"成功启用服务器「{command[2]}」")
            case "disable" | "D":
                if command_length < 3:
                    return Result.of_failure()
                if self._check_permission(ServerList.Disable):
                    return self._permission_reject
                if (server_list := self.check_server_exists(command[2])) is None:
                    return Result.of_failure(f"不存在服务器「{command[2]}」")
                server_list.enable = False
                server_list.save()
                return Result.of_success(f"成功禁用服务器「{command[2]}」")
            case "rename" | "r":
                if command_length < 4:
                    return Result.of_failure()
                if self._check_permission(ServerList.Rename):
                    return self._permission_reject
                if (server_list := self.check_server_exists(command[2])) is None:
                    return Result.of_failure(f"不存在服务器「{command[2]}」")
                server_list.server_name = command[3]
                server_list.save()
                return Result.of_success(f"成功重命名服务器：「{command[2]}」->「{command[3]}」")
            case "modify" | "m":
                if command_length < 4:
                    return Result.of_failure()
                if self._check_permission(ServerList.Modify):
                    return self._permission_reject
                if (server_list := self.check_server_exists(command[2])) is None:
                    return Result.of_failure(f"不存在服务器「{command[2]}」")
                server_list.server_ip = command[3]
                server_list.save()
                return Result.of_success(f"成功将服务器「{command[2]}」的地址修改为「{command[3]}」")
            case "weight" | "w":
                if command_length < 4:
                    return Result.of_failure()
                if self._check_permission(ServerList.Weight):
                    return self._permission_reject
                if (server_list := self.check_server_exists(command[2])) is None:
                    return Result.of_failure(f"不存在服务器「{command[2]}」")
                server_list.priority = int(command[3])
                server_list.save()
                return Result.of_success(f"成功将服务器「{command[2]}」的权重修改为「{command[3]}」")
            case "reload" | "R":
                if self._check_permission(ServerList.Reload):
                    return self._permission_reject
                server.reload_server_list()
                return Result.of_success("重新加载服务器列表成功")
