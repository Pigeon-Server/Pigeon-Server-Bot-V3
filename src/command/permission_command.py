from re import Pattern, compile, search
from typing import Callable, List, Optional

from src.bot.tools import per
from src.command.command_parser import CommandParser
from src.module.message import Message
from src.module.permissions import Permission
from src.module.result import Result


class PermissionCommand(CommandParser):

    _match_user_id: Pattern = compile(r"\(\d*?\)")

    def __init__(self):
        CommandParser.__init__(self)

    async def parse(self, sender: str, command: List[str], message: Message) -> Result:
        parsing_methods: List[Callable[[str, List[str], Message], Optional[Result]]] = [
            self._parse_other_command,
            self._parse_player_command,
            self._parse_group_command
        ]

        for method in parsing_methods:
            result = method(sender, command, message)
            if result is not None:
                return result

        return Result.of_failure()

    def _get_user_id(self, command: str) -> str:
        res = search(self._match_user_id, command)
        return res.group()[1:-1]

    def _parse_other_command(self, sender: str, command: List[str], _: Message) -> Optional[Result]:
        command_length = len(command)
        if command_length < 2:
            return
        if command[1] == "list":
            if not self.check_player(sender, Permission.ShowList):
                return Result.of_success("你无权这么做")
            if command_length == 2:
                data = per.permission_node
                msg = "所有权限节点: \n"
                for raw in data:
                    msg += f"{raw}\n"
                msg += "\n".join(data)
                return Result.of_success(msg)
            if command_length == 3:
                data = per.permission_node
                msg = f"{command[2]}权限节点: \n"
                data = list(filter(lambda x: command[2] in x, data))
                msg += "\n".join(data)
                return Result.of_success(msg)
            return Result.of_success(f"Usage：\n/permission list [word]")
        if command[1] == "reload":
            if command_length == 2:
                if not self.check_player(sender, Permission.Reload.Common):
                    return Result.of_success("你无权这么做")
                return Result.of_success(per.reload_group_permission().message)
            if command_length == 3 and command[2] == "true":
                if not self.check_player(sender, Permission.Reload.Force):
                    return Result.of_success("你无权这么做")
                return Result.of_success(per.reload_group_permission(True).message)
            return Result.of_success(f"Usage：\n/permission reload [force]")

    def _parse_player_command(self, sender: str, command: List[str], _: Message) -> Optional[Result]:
        command_length = len(command)
        if command[1] not in ["player", "p"] or command_length < 4:
            return
        match command[2]:
            case "list" | "l":
                if command_length >= 5:
                    return Result.of_success(f"Usage：\n/permission player list (At | id) ")
                if not self.check_player(sender, Permission.Player.List):
                    return Result.of_success("你无权这么做")
                if command[3].startswith("@"):
                    user_id = self._get_user_id(command[3])
                    msg = f"{user_id}拥有的权限为：\n"
                    msg += "\n".join(per.get_player_permission(user_id))
                else:
                    msg = f"{command[3]}拥有的权限为：\n"
                    msg += "\n".join(per.get_player_permission(str(command[3])))
                return Result.of_success(msg.removesuffix("\n"))
            case "info" | "i":
                if command_length >= 5:
                    return Result.of_success(f"Usage：\n/permission player info (At | id) ")
                if not self.check_player(sender, Permission.Player.Info):
                    return Result.of_success("你无权这么做")
                if command[3].startswith("@"):
                    user_id = self._get_user_id(command[3])
                    data = per.get_player_info(user_id)
                    msg = f"{user_id}的信息如下:\n"
                else:
                    data = per.get_player_info(str(command[3]))
                    msg = f"{command[3]}拥有的权限为：\n"
                if data is None:
                    return Result.of_success("未查询到权限记录")
                if "group" in data.keys():
                    msg += "权限组: \n" + "\n".join(data["group"]) + "\n"
                if "permission" in data.keys():
                    msg += "权限: \n" + "\n".join(data["permission"])
                return Result.of_success(msg.removesuffix("\n"))
            case "del" | "d":
                return

    def _parse_group_command(self, sender: str, command: List[str], _: Message) -> Optional[Result]:
        pass
