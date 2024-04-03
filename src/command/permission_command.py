from re import Pattern, compile, search
from typing import Awaitable, Callable, List, Optional

from src.bot.app import message_sender, reply_manager
from src.bot.tools import per
from src.command.command_parser import CommandParser
from src.module.message import Message
from src.module.permissions import Permission
from src.module.reply_message import ReplyType
from src.module.result import Result


class PermissionCommand(CommandParser):
    _match_user_id: Pattern = compile(r"\(\d*?\)")
    _message: Message
    _permission_reject: Result = Result.of_failure("你无权这么做")
    _command_helper: Result = Result.of_failure(f"Permission模块帮助: \n"
                                                f"/permission player add (At | id) (permission)\n"
                                                f"/permission player remove (At | id) (permission)\n"
                                                f"/permission player clone (At | id) (At | id)\n"
                                                f"/permission player check (At | id) (permission)\n"
                                                f"/permission player group add (At | id) (groupName)\n"
                                                f"/permission player group remove (At | id) (groupName)\n"
                                                f"/permission player group set (At | id) (groupName)\n"
                                                f"/permission player del (At | id) \n"
                                                f"/permission player list (At | id) \n"
                                                f"/permission player info (At | id) \n"
                                                f"/permission player create (At | id) [groupName]\n"
                                                f"/permission group add (groupName) (permission)\n"
                                                f"/permission group remove (groupName) (permission)\n"
                                                f"/permission group clone (groupName) (groupName)\n"
                                                f"/permission group check (groupName) (permission)\n"
                                                f"/permission group group add (groupName) (groupName)\n"
                                                f"/permission group group remove (groupName) (groupName)\n"
                                                f"/permission group del (groupName)\n"
                                                f"/permission group list (groupName)\n"
                                                f"/permission group info (groupName)\n"
                                                f"/permission group create (groupName)\n"
                                                f"/permission reload [force]\n"
                                                f"/permission list [word]")
    _player_command_helper: Result = Result.of_failure(f"Permission模块帮助: \n"
                                                       f"/permission player add (At | id) (permission)\n"
                                                       f"/permission player remove (At | id) (permission)\n"
                                                       f"/permission player clone (At | id) (At | id)\n"
                                                       f"/permission player check (At | id) (permission)\n"
                                                       f"/permission player group add (At | id) (groupName)\n"
                                                       f"/permission player group remove (At | id) (groupName)\n"
                                                       f"/permission player group set (At | id) (groupName)\n"
                                                       f"/permission player del (At | id) \n"
                                                       f"/permission player list (At | id) \n"
                                                       f"/permission player info (At | id) \n"
                                                       f"/permission player create (At | id) [groupName]")
    _group_command_helper: Result = Result.of_failure(f"Permission模块帮助: \n"
                                                      f"/permission group add (groupName) (permission)\n"
                                                      f"/permission group remove (groupName) (permission)\n"
                                                      f"/permission group clone (groupName) (groupName)\n"
                                                      f"/permission group check (groupName) (permission)\n"
                                                      f"/permission group group add (groupName) (groupName)\n"
                                                      f"/permission group group remove (groupName) (groupName)\n"
                                                      f"/permission group del (groupName)\n"
                                                      f"/permission group list (groupName)\n"
                                                      f"/permission group info (groupName)\n"
                                                      f"/permission group create (groupName)")

    def __init__(self):
        super().__init__()
        self._get_command_helper()

    async def _parse_other_command(self, command: List[str]) -> Optional[Result]:
        command_length = len(command)
        if command_length < 2:
            return
        match command[1]:
            case "list", "l":
                return await self._parse_list_command(command, command_length)
            case "reload", "r":
                return await self._parse_reload_command(command, command_length)
            case "help", "h":
                return self._command_helper

    async def _parse_player_command(self, command: List[str]) -> Optional[Result]:
        command_length = len(command)
        if command_length <= 1 or command[1] not in ["player", "p"]:
            return
        if command_length < 4:
            return self._player_command_helper
        match command[2]:
            case "list" | "l":
                return await self._parse_player_list_command(command, command_length)
            case "info" | "i":
                return await self._parse_player_info_command(command, command_length)
            case "del" | "d":
                return await self._parse_player_delete_command(command, command_length)
            case "create" | "c":
                return await self._parse_player_create_command(command, command_length)
            case "add" | "a":
                return await self._parse_player_add_command(command, command_length)
            case "remove" | "r":
                return await self._parse_player_remove_command(command, command_length)
            case "clone":
                return await self._parse_player_clone_command(command, command_length)
            case "check":
                return await self._parse_player_check_command(command, command_length)
            case "group" | "g":
                return await self._parse_player_parent_command(command, command_length)

    async def _parse_group_command(self, command: List[str]) -> Optional[Result]:
        pass

    async def parse(self, message: Message, command: List[str]) -> Optional[Result]:
        await super().parse(message, command)
        parsing_methods: List[Callable[[List[str]], Awaitable[Optional[Result]]]] = [
            self._parse_other_command,
            self._parse_player_command,
            self._parse_group_command
        ]

        for method in parsing_methods:
            result = await method(command)
            if result:
                return result

        return None

    def _get_user_id(self, command: str) -> str:
        if not command.startswith("@"):
            return command
        return search(self._match_user_id, command).group()[1:-1]

    def _check_permission(self, permission: str) -> bool:
        if self.check_player(self._message.sender_id, permission):
            return False
        return True

    async def _parse_list_command(self, command: List[str], command_length: int) -> Result:
        if self._check_permission(Permission.ShowList):
            return self._permission_reject
        if command_length == 2:
            return Result.of_success(f"所有权限节点: \n{'\n'.join(per.permission_node)}")
        if command_length == 3:
            return Result.of_success(
                f"{command[2]}权限节点: \n{'\n'.join(list(filter(lambda x: command[2] in x, per.permission_node)))}")
        return Result.of_failure(f"Usage：\n/permission list [word]")

    async def _parse_reload_command(self, command: List[str], command_length: int) -> Result:
        if command_length == 2:
            if self._check_permission(Permission.Reload.Common):
                return self._permission_reject
            return Result.of_success(per.reload_group_permission().message)
        if command_length == 3 and command[2] == "true":
            if self._check_permission(Permission.Reload.Force):
                return self._permission_reject
            return Result.of_success(per.reload_group_permission(True).message)
        return Result.of_failure(f"Usage：\n/permission reload [force]")

    async def _parse_player_list_command(self, command: List[str], command_length: int) -> Result:
        if command_length >= 5:
            return Result.of_failure(f"Usage：\n/permission player list (At | id) ")
        if self._check_permission(Permission.Player.List):
            return self._permission_reject
        user_id = self._get_user_id(command[3])
        msg = f"「{user_id}」拥有的权限为：\n"
        msg += "\n".join(per.get_player_permission(user_id))
        return Result.of_success(msg.removesuffix("\n"))

    async def _parse_player_info_command(self, command: List[str], command_length: int) -> Result:
        if command_length >= 5:
            return Result.of_failure(f"Usage：\n/permission player info (At | id) ")
        if self._check_permission(Permission.Player.Info):
            return self._permission_reject
        user_id = self._get_user_id(command[3])
        data = per.get_player_info(user_id)
        msg = f"「{user_id}」拥有的权限为：\n"
        if data is None:
            return Result.of_success("未查询到权限记录")
        if "group" in data.keys():
            msg += "权限组: \n" + "\n".join(data["group"]) + "\n"
        if "permission" in data.keys():
            msg += "权限: \n" + "\n".join(data["permission"])
        return Result.of_success(msg.removesuffix("\n"))

    async def _parse_player_delete_command(self, command: List[str], command_length: int) -> Result:
        if command_length >= 5:
            return Result.of_failure(f"Usage：\n/permission player del (At | id) ")
        if self._check_permission(Permission.Player.Del):
            return self._permission_reject
        user_id = self._get_user_id(command[3])
        msg = f"是否删除「{user_id}」用户的权限信息(是/否)？"
        target = (await message_sender.send_message(self._message.group_id, msg))[0]
        result = await reply_manager.wait_reply_async(self._message, 60)
        match result:
            case ReplyType.REJECT:
                await message_sender.send_quote_message(self._message.group_id, target.id, "操作已取消",
                                                        self._message.sender_id)
                return Result.of_success()
            case ReplyType.ACCEPT:
                res = per.del_player(user_id)
                if res.is_success:
                    await message_sender.send_quote_message(self._message.group_id, target.id,
                                                            f"操作成功, {res.message}",
                                                            self._message.sender_id)
                    return Result.of_success()
                await message_sender.send_quote_message(self._message.group_id, target.id,
                                                        f"操作失败, {res.message}",
                                                        self._message.sender_id)
                return Result.of_failure()
            case ReplyType.TIMEOUT:
                await message_sender.send_quote_message(self._message.group_id, target.id, "操作超时",
                                                        self._message.sender_id)
                return Result.of_failure()
        return Result.of_failure()

    async def _parse_player_create_command(self, command: List[str], command_length: int) -> Result:
        if command_length >= 6:
            return Result.of_failure(f"Usage：\n/permission player create (At | id) [groupName]")
        if self._check_permission(Permission.Player.Create):
            return self._permission_reject
        user_id = self._get_user_id(command[3])
        if command_length == 4:
            res = per.create_player(user_id)
        else:
            res = per.create_player(user_id, command[4])
        return res

    async def _parse_player_add_command(self, command: List[str], command_length: int) -> Result:
        if command_length >= 6:
            return Result.of_failure(f"Usage：\n/permission player add (At | id) (permission)")
        if self._check_permission(Permission.Player.Give):
            return self._permission_reject
        if command[4] not in per.permission_node:
            return Result.of_failure(f"{command[4]}不是一个有效的权限节点")
        return per.add_player_permission(self._get_user_id(command[3]), command[4])

    async def _parse_player_remove_command(self, command: List[str], command_length: int) -> Result:
        if command_length >= 6:
            return Result.of_failure(f"Usage：\n/permission player remove (At | id) (permission)")
        if self._check_permission(Permission.Player.Remove):
            return self._permission_reject
        if command[4] not in per.permission_node:
            return Result.of_failure(f"{command[4]}不是一个有效的权限节点")
        return per.remove_player_permission(self._get_user_id(command[3]), command[4])

    async def _parse_player_clone_command(self, command: List[str], command_length: int) -> Result:
        if command_length >= 6:
            return Result.of_failure(f"Usage：\n/permission player clone (At | id) (At | id)")
        if self._check_permission(Permission.Player.Clone):
            return self._permission_reject
        clone_src = self._get_user_id(command[3])
        clone_dest = self._get_user_id(command[4])
        msg = f"确认克隆「{clone_src}」用户的`所有权限`到「{clone_dest}」(是/否)？"
        target = (await message_sender.send_message(self._message.group_id, msg))[0]
        result = await reply_manager.wait_reply_async(self._message, 60)
        match result:
            case ReplyType.REJECT:
                await message_sender.send_quote_message(self._message.group_id, target.id, "操作已取消",
                                                        self._message.sender_id)
                return Result.of_success()
            case ReplyType.ACCEPT:
                res = per.clone_player_permission(clone_src, clone_dest)
                if res.is_success:
                    await message_sender.send_quote_message(self._message.group_id, target.id,
                                                            f"操作成功, {res.message}",
                                                            self._message.sender_id)
                    return Result.of_success()
                await message_sender.send_quote_message(self._message.group_id, target.id,
                                                        f"操作失败, {res.message}",
                                                        self._message.sender_id)
                return Result.of_failure()
            case ReplyType.TIMEOUT:
                await message_sender.send_quote_message(self._message.group_id, target.id, "操作超时",
                                                        self._message.sender_id)
                return Result.of_failure()
        return Result.of_failure()

    async def _parse_player_check_command(self, command: List[str], command_length: int) -> Result:
        if command_length >= 6:
            return Result.of_failure(f"Usage：\n/permission player check (At | id) (permission)")
        if self._check_permission(Permission.Player.Check):
            return self._permission_reject
        if command[4] not in per.permission_node:
            return Result.of_failure(f"{command[4]}不是一个有效的权限节点")
        return per.check_player_permission(self._get_user_id(command[3]), command[4])

    async def _parse_player_parent_add_command(self, command: List[str], command_length: int) -> Result:
        if command_length >= 7:
            return Result.of_failure(f"Usage：\n/permission player group add (At | id) (groupName)")
        if self._check_permission(Permission.Player.Parent.Add):
            return self._permission_reject
        return per.add_player_parent(self._get_user_id(command[4]), command[5])

    async def _parse_player_parent_remove_command(self, command: List[str], command_length: int) -> Result:
        if command_length >= 7:
            return Result.of_failure(f"Usage：\n/permission player group remove (At | id) (groupName)")
        if self._check_permission(Permission.Player.Parent.Del):
            return self._permission_reject
        return per.remove_player_parent(self._get_user_id(command[4]), command[5])

    async def _parse_player_parent_set_command(self, command: List[str], command_length: int) -> Result:
        if command_length >= 7:
            return Result.of_failure(f"Usage：\n/permission player group set (At | id) (groupName)")
        if self._check_permission(Permission.Player.Parent.Del):
            return self._permission_reject
        return per.set_player_group(self._get_user_id(command[4]), command[5])

    async def _parse_player_parent_command(self, command: List[str], command_length: int) -> Result:
        match command[3]:
            case "add" | "a":
                return await self._parse_player_parent_add_command(command, command_length)
            case "remove" | "r":
                return await self._parse_player_parent_remove_command(command, command_length)
            case "set" | "s":
                return await self._parse_player_parent_set_command(command, command_length)
        return Result.of_failure("Usage：\n"
                                 "/permission player group add (At | id) (groupName)\n"
                                 "/permission player group remove (At | id) (groupName)\n"
                                 "/permission player group set (At | id) (groupName)")
