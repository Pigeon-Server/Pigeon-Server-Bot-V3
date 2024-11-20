from typing import Optional

from peewee import DoesNotExist

from src.command.command_manager import CommandManager
from src.database.server_model import ServerList as ServerListModel
from src.element.message import Message
from src.element.permissions import ServerList
from src.element.result import Result
from src.module.server_status import ServerStatus


def check_server_exists(server_name: str) -> Optional[ServerListModel]:
    try:
        return ServerListModel.get(server_name=server_name)
    except DoesNotExist:
        return None


@CommandManager.register_command("/serverlist",
                                 command_docs="展示serverlist模块的所有命令及其帮助",
                                 alia_list=["/sl"])
async def server_list_command(_: Message, __: list[str]) -> Optional[Result]:
    return Result.of_failure("服务器状态：\n"
                             "/serverlist add (ServerName) (ServerIp) [weight] 添加一个服务器\n"
                             "/serverlist del (ServerName) 删除某个服务器\n"
                             "/serverlist enable (ServerName) 开启某个服务器的状态查询\n"
                             "/serverlist disable (ServerName) 关闭某个服务器的状态查询\n"
                             "/serverlist rename (ServerName) (NewName) 修改某个服务器名称\n"
                             "/serverlist modify (ServerName) (NewServerIp) 修改某个服务器ip\n"
                             "/serverlist weight (ServerName) (weight) 修改服务器权重"
                             "/serverlist reload 重载服务器列表\n"
                             "/serverlist list 列出所有服务器")


@CommandManager.register_command("/serverlist add",
                                 command_require_permission=ServerList.Add,
                                 command_docs="添加一个服务器",
                                 command_usage="/serverlist add (ServerName) (ServerIp) [weight]",
                                 alia_list=["/sl a"])
async def server_list_add(_: Message, command: list[str]) -> Optional[Result]:
    if (command_length := len(command)) < 4 or command_length > 5:
        return None
    if check_server_exists(command[2]) is not None:
        return Result.of_failure(f"服务器「{command[2]}」已存在")
    server_list: ServerListModel = ServerListModel(server_name=command[2], server_ip=command[3])
    if command_length == 5:
        server_list.priority = int(command[4])
    server_list.save()
    return Result.of_success(f"成功添加服务器「{command[2]}」，服务器IP：{command[3]}")


@CommandManager.register_command("/serverlist del",
                                 command_require_permission=ServerList.Del,
                                 command_docs="删除某个服务器",
                                 command_usage="/serverlist del (ServerName)",
                                 alia_list=["/sl d"])
async def server_list_del(_: Message, command: list[str]) -> Optional[Result]:
    if len(command) < 3:
        return None
    if (server_list := check_server_exists(command[2])) is None:
        return Result.of_failure(f"不存在服务器「{command[2]}」")
    server_list.delete_instance()
    return Result.of_success(f"成功移除服务器「{command[2]}」")


@CommandManager.register_command("/serverlist enable",
                                 command_require_permission=ServerList.Enable,
                                 command_docs="/serverlist enable (ServerName)",
                                 command_usage="开启某个服务器的状态查询",
                                 alia_list=["/sl e"])
async def server_list_enable(_: Message, command: list[str]) -> Optional[Result]:
    if len(command) < 3:
        return None
    if (server_list := check_server_exists(command[2])) is None:
        return Result.of_failure(f"不存在服务器「{command[2]}」")
    server_list.enable = True
    server_list.save()
    return Result.of_success(f"成功启用服务器「{command[2]}」")


@CommandManager.register_command("/serverlist disable",
                                 command_require_permission=ServerList.Disable,
                                 command_docs="/serverlist disable (ServerName)",
                                 command_usage="关闭某个服务器的状态查询",
                                 alia_list=["/sl D"])
async def server_list_disable(_: Message, command: list[str]) -> Optional[Result]:
    if len(command) < 3:
        return None
    if (server_list := check_server_exists(command[2])) is None:
        return Result.of_failure(f"不存在服务器「{command[2]}」")
    server_list.enable = False
    server_list.save()
    return Result.of_success(f"成功禁用服务器「{command[2]}」")


@CommandManager.register_command("/serverlist rename",
                                 command_require_permission=ServerList.Rename,
                                 command_docs="/serverlist rename (ServerName) (NewName)",
                                 command_usage="修改某个服务器名称",
                                 alia_list=["/sl r"])
async def server_list_rename(_: Message, command: list[str]) -> Optional[Result]:
    if len(command) < 4:
        return None
    if (server_list := check_server_exists(command[2])) is None:
        return Result.of_failure(f"不存在服务器「{command[2]}」")
    server_list.server_name = command[3]
    server_list.save()
    return Result.of_success(f"成功重命名服务器：「{command[2]}」->「{command[3]}」")


@CommandManager.register_command("/serverlist modify",
                                 command_require_permission=ServerList.Modify,
                                 command_docs="修改某个服务器ip",
                                 command_usage="/serverlist modify (ServerName) (NewServerIp)",
                                 alia_list=["/sl m"])
async def server_list_modify(_: Message, command: list[str]) -> Optional[Result]:
    if len(command) < 4:
        return None
    if (server_list := check_server_exists(command[2])) is None:
        return Result.of_failure(f"不存在服务器「{command[2]}」")
    server_list.server_ip = command[3]
    server_list.save()
    return Result.of_success(f"成功将服务器「{command[2]}」的地址修改为「{command[3]}」")


@CommandManager.register_command("/serverlist weight",
                                 command_require_permission=ServerList.Weight,
                                 command_docs="修改服务器权重",
                                 command_usage="/serverlist weight (ServerName) (weight)",
                                 alia_list=["/sl w"])
async def server_list_weight(_: Message, command: list[str]) -> Optional[Result]:
    if len(command) < 4:
        return None
    if (server_list := check_server_exists(command[2])) is None:
        return Result.of_failure(f"不存在服务器「{command[2]}」")
    server_list.priority = int(command[3])
    server_list.save()
    return Result.of_success(f"成功将服务器「{command[2]}」的权重修改为「{command[3]}」")


@CommandManager.register_command("/serverlist reload",
                                 command_require_permission=ServerList.Reload,
                                 command_docs="重载服务器列表",
                                 alia_list=["/sl R"])
async def server_list_reload(_: Message, __: list[str]) -> Optional[Result]:
    ServerStatus.reload_server_list()
    return Result.of_success("重新加载服务器列表成功")


@CommandManager.register_command("/serverlist list",
                                 command_require_permission=ServerList.List,
                                 command_docs="列出所有服务器",
                                 alia_list=["/sl l"])
async def server_list_list(_: Message, __: list[str]) -> Optional[Result]:
    return Result.of_success("\n".join([str(item) for item in ServerListModel.select()]))
