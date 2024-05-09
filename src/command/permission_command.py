from re import Pattern, compile, search
from typing import Awaitable, Callable, Dict, List, Optional

from satori import Image

from src.bot.app import message_sender, permission_image_dir, reply_manager
from src.bot.permission import ps_manager
from src.command.command_parser import CommandParser
from src.element.message import Message
from src.element.permissions import Permission
from src.element.result import Result
from src.type.types import ReplyType


class PermissionCommand(CommandParser):
    _match_user_id: Pattern = compile(r"\(\d*?\)")
    _message: Message
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

    async def _parse_other_command(self, command: List[str]) -> Optional[Result]:
        if (command_length := len(command)) < 2:
            return None
        match command[1]:
            case "list" | "l":
                return await self._parse_list_command(command, command_length)
            case "reload" | "r":
                return await self._parse_reload_command(command, command_length)
            case "help" | "h":
                return self._command_helper

    async def _parse_player_command(self, command: List[str]) -> Optional[Result]:
        if (command_length := len(command)) <= 1 or command[1] not in ["player", "p"]:
            return None
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
            case _:
                return self._player_command_helper

    async def _parse_group_command(self, command: List[str]) -> Optional[Result]:
        if (command_length := len(command)) <= 1 or command[1] not in ["group", "g"]:
            return None
        if command_length < 4:
            return self._group_command_helper
        match command[2]:
            case "list" | "l":
                return await self._parse_group_list_command(command, command_length)
            case "info" | "i":
                return await self._parse_group_info_command(command, command_length)
            case "del" | "d":
                return await self._parse_group_delete_command(command, command_length)
            case "create" | "c":
                return await self._parse_group_create_command(command, command_length)
            case "add" | "a":
                return await self._parse_group_add_command(command, command_length)
            case "remove" | "r":
                return await self._parse_group_remove_command(command, command_length)
            case "clone":
                return await self._parse_group_clone_command(command, command_length)
            case "check":
                return await self._parse_group_check_command(command, command_length)
            case "group" | "g":
                return await self._parse_group_parent_command(command, command_length)
            case _:
                return self._group_command_helper

    async def parse(self, message: Message, command: List[str]) -> Optional[Result]:
        await super().parse(message, command)
        parsing_methods: List[Callable[[List[str]], Awaitable[Optional[Result]]]] = [
            self._parse_other_command,
            self._parse_player_command,
            self._parse_group_command
        ]

        if command[0] not in ["permission", "ps"]:
            return None

        for method in parsing_methods:
            result = await method(command)
            if result is not None:
                return result

        return None

    def _get_user_id(self, command: str) -> Optional[str]:
        if not command.startswith("@"):
            return command
        res = search(self._match_user_id, command)
        if res is None:
            return None
        return res.group()[1:-1]

    @staticmethod
    def _parse_permission_data(msg: str, data: Dict[str, str]) -> Result:
        if data is None:
            return Result.of_success("未查询到权限记录")
        if "group" in data.keys():
            msg += "权限组: \n" + "\n".join(data["group"]) + "\n"
        if "parent" in data.keys():
            msg += "父权限组: \n" + "\n".join(data["parent"]) + "\n"
        if "permission" in data.keys():
            msg += "权限: \n" + "\n".join(data["permission"])
        return Result.of_success(msg.removesuffix("\n"))

    async def _parse_list_command(self, _: List[str], command_length: int) -> Result:
        if self._check_permission(Permission.ShowList):
            return self._permission_reject
        if command_length == 2:
            with open(permission_image_dir, "rb") as f:
                await message_sender.send_message(self._message.group_id, [Image.of(raw=f.read(), mime="image/png")])
            return Result.of_success()
        return Result.of_failure(f"Usage：\n/permission list")

    async def _parse_reload_command(self, command: List[str], command_length: int) -> Result:
        if command_length == 2:
            if self._check_permission(Permission.Group.Reload.Common):
                return self._permission_reject
            return Result.of_success(ps_manager.reload_group_permission().message)
        if command_length == 3 and command[2] == "true":
            if self._check_permission(Permission.Group.Reload.Force):
                return self._permission_reject
            return Result.of_success(ps_manager.reload_group_permission(True).message)
        return Result.of_failure(f"Usage：\n/permission reload [force]")

    async def _parse_player_list_command(self, command: List[str], command_length: int) -> Result:
        if command_length >= 5:
            return Result.of_failure(f"Usage：\n/permission player list (At | id) ")
        if self._check_permission(Permission.Player.List):
            return self._permission_reject
        user_id = self._get_user_id(command[3])
        if user_id is None:
            return Result.of_failure(f"Usage：\n/permission player list (At | id) ")
        msg = f"「{user_id}」拥有的权限为：\n"
        msg += "\n".join(ps_manager.get_player_permission(user_id))
        return Result.of_success(msg.removesuffix("\n"))

    async def _parse_player_info_command(self, command: List[str], command_length: int) -> Result:
        if command_length >= 5:
            return Result.of_failure(f"Usage：\n/permission player info (At | id) ")
        if self._check_permission(Permission.Player.Info):
            return self._permission_reject
        user_id = self._get_user_id(command[3])
        if user_id is None:
            return Result.of_failure(f"Usage：\n/permission player info (At | id) ")
        data = ps_manager.get_player_info(user_id)
        msg = f"「{user_id}」拥有的权限为：\n"
        return self._parse_permission_data(msg, data)

    async def _parse_player_delete_command(self, command: List[str], command_length: int) -> Result:
        if command_length >= 5:
            return Result.of_failure(f"Usage：\n/permission player del (At | id) ")
        if self._check_permission(Permission.Player.Del):
            return self._permission_reject
        user_id = self._get_user_id(command[3])
        if user_id is None:
            return Result.of_failure(f"Usage：\n/permission player del (At | id) ")
        msg = f"是否删除「{user_id}」用户的权限信息(是/否)？"
        target = (await message_sender.send_message(self._message.group_id, msg))[0]
        result = await reply_manager.wait_reply_async(self._message, 60)
        match result:
            case ReplyType.REJECT:
                await message_sender.send_quote_message(self._message.group_id, target.id, "操作已取消",
                                                        self._message.sender_id)
                return Result.of_success()
            case ReplyType.ACCEPT:
                res = ps_manager.del_player(user_id)
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
        if user_id is None:
            return Result.of_failure(f"Usage：\n/permission player create (At | id) [groupName]")
        if command_length == 4:
            res = ps_manager.create_player(user_id)
        else:
            res = ps_manager.create_player(user_id, command[4])
        return res

    async def _parse_player_add_command(self, command: List[str], command_length: int) -> Result:
        if command_length >= 6:
            return Result.of_failure(f"Usage：\n/permission player add (At | id) (permission)")
        if self._check_permission(Permission.Player.Give):
            return self._permission_reject
        if command[4] not in ps_manager.permission_node:
            return Result.of_failure(f"{command[4]}不是一个有效的权限节点")
        user_id = self._get_user_id(command[3])
        if user_id is None:
            return Result.of_failure(f"Usage：\n/permission player add (At | id) (permission)")
        return ps_manager.add_player_permission(user_id, command[4])

    async def _parse_player_remove_command(self, command: List[str], command_length: int) -> Result:
        if command_length >= 6:
            return Result.of_failure(f"Usage：\n/permission player remove (At | id) (permission)")
        if self._check_permission(Permission.Player.Remove):
            return self._permission_reject
        if command[4] not in ps_manager.permission_node:
            return Result.of_failure(f"{command[4]}不是一个有效的权限节点")
        user_id = self._get_user_id(command[3])
        if user_id is None:
            return Result.of_failure(f"Usage：\n/permission player remove (At | id) (permission)")
        return ps_manager.remove_player_permission(user_id, command[4])

    async def _parse_player_clone_command(self, command: List[str], command_length: int) -> Result:
        if command_length >= 6:
            return Result.of_failure(f"Usage：\n/permission player clone (At | id) (At | id)")
        if self._check_permission(Permission.Player.Clone):
            return self._permission_reject
        clone_src = self._get_user_id(command[3])
        clone_dest = self._get_user_id(command[4])
        if clone_src is None or clone_dest is None:
            return Result.of_failure(f"Usage：\n/permission player clone (At | id) (At | id)")
        msg = f"确认克隆「{clone_src}」用户的`所有权限`到「{clone_dest}」(是/否)？"
        target = (await message_sender.send_message(self._message.group_id, msg))[0]
        result = await reply_manager.wait_reply_async(self._message, 60)
        match result:
            case ReplyType.REJECT:
                await message_sender.send_quote_message(self._message.group_id, target.id, "操作已取消",
                                                        self._message.sender_id)
                return Result.of_success()
            case ReplyType.ACCEPT:
                res = ps_manager.clone_player_permission(clone_src, clone_dest)
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
        if command[4] not in ps_manager.permission_node:
            return Result.of_failure(f"{command[4]}不是一个有效的权限节点")
        user_id = self._get_user_id(command[3])
        if user_id is None:
            return Result.of_failure(f"Usage：\n/permission player check (At | id) (permission)")
        res = ps_manager.check_player_permission(user_id, command[4])
        if res.is_success:
            return Result.of_success(f"用户「{user_id}」拥有权限节点「{command[4]}」")
        return Result.of_success(f"用户「{user_id}」没有权限节点「{command[4]}」")

    async def _parse_player_parent_add_command(self, command: List[str], command_length: int) -> Result:
        if command_length >= 7:
            return Result.of_failure(f"Usage：\n/permission player group add (At | id) (groupName)")
        if self._check_permission(Permission.Player.Parent.Add):
            return self._permission_reject
        user_id = self._get_user_id(command[4])
        if user_id is None:
            return Result.of_failure(f"Usage：\n/permission player group add (At | id) (groupName)")
        return ps_manager.add_player_parent(user_id, command[5])

    async def _parse_player_parent_remove_command(self, command: List[str], command_length: int) -> Result:
        if command_length >= 7:
            return Result.of_failure(f"Usage：\n/permission player group remove (At | id) (groupName)")
        if self._check_permission(Permission.Player.Parent.Del):
            return self._permission_reject
        user_id = self._get_user_id(command[4])
        if user_id is None:
            return Result.of_failure(f"Usage：\n/permission player group remove (At | id) (groupName)")
        return ps_manager.remove_player_parent(user_id, command[5])

    async def _parse_player_parent_set_command(self, command: List[str], command_length: int) -> Result:
        if command_length >= 7:
            return Result.of_failure(f"Usage：\n/permission player group set (At | id) (groupName)")
        if self._check_permission(Permission.Player.Parent.Del):
            return self._permission_reject
        user_id = self._get_user_id(command[4])
        if user_id is None:
            return Result.of_failure(f"Usage：\n/permission player group set (At | id) (groupName)")
        return ps_manager.set_player_parent(user_id, command[5])

    async def _parse_player_parent_command(self, command: List[str], command_length: int) -> Result:
        match command[3]:
            case "add" | "a":
                return await self._parse_player_parent_add_command(command, command_length)
            case "remove" | "r":
                return await self._parse_player_parent_remove_command(command, command_length)
            case "set" | "s":
                return await self._parse_player_parent_set_command(command, command_length)
            case _:
                return Result.of_failure("Usage：\n"
                                         "/permission player group add (At | id) (groupName)\n"
                                         "/permission player group remove (At | id) (groupName)\n"
                                         "/permission player group set (At | id) (groupName)")

    async def _parse_group_list_command(self, command: List[str], command_length: int) -> Result:
        if command_length >= 5:
            return Result.of_failure(f"Usage：\n/permission group list (groupName) ")
        if self._check_permission(Permission.Group.List):
            return self._permission_reject
        msg = f"「{command[3]}」拥有的权限为：\n"
        msg += "\n".join(ps_manager.get_group_permission(command[3]))
        return Result.of_success(msg.removesuffix("\n"))

    async def _parse_group_info_command(self, command: List[str], command_length: int) -> Result:
        if command_length >= 5:
            return Result.of_failure(f"Usage：\n/permission group info (groupName) ")
        if self._check_permission(Permission.Group.Info):
            return self._permission_reject
        data = ps_manager.get_group_info(command[3])
        msg = f"「{command[3]}」拥有的权限为：\n"
        return self._parse_permission_data(msg, data)

    async def _parse_group_delete_command(self, command: List[str], command_length: int) -> Result:
        if command_length >= 5:
            return Result.of_failure(f"Usage：\n/permission group del (groupName) ")
        if self._check_permission(Permission.Group.Del):
            return self._permission_reject
        msg = f"是否删除权限组「{command[3]}」(是/否)？"
        target = (await message_sender.send_message(self._message.group_id, msg))[0]
        result = await reply_manager.wait_reply_async(self._message, 60)
        match result:
            case ReplyType.REJECT:
                await message_sender.send_quote_message(self._message.group_id, target.id, "操作已取消",
                                                        self._message.sender_id)
                return Result.of_success()
            case ReplyType.ACCEPT:
                res = ps_manager.del_group(command[3])
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

    async def _parse_group_create_command(self, command: List[str], command_length: int) -> Result:
        if command_length >= 6:
            return Result.of_failure(f"Usage：\n/permission group create (groupName) [groupName]")
        if self._check_permission(Permission.Group.Create):
            return self._permission_reject
        if command_length == 4:
            res = ps_manager.create_group(command[3])
        else:
            res = ps_manager.create_group(command[3], command[4])
        return res

    async def _parse_group_add_command(self, command: List[str], command_length: int) -> Result:
        if command_length >= 6:
            return Result.of_failure(f"Usage：\n/permission group add (groupName) (permission)")
        if self._check_permission(Permission.Group.Give):
            return self._permission_reject
        if command[4] not in ps_manager.permission_node:
            return Result.of_failure(f"{command[4]}不是一个有效的权限节点")
        return ps_manager.add_group_permission(command[3], command[4])

    async def _parse_group_remove_command(self, command: List[str], command_length: int) -> Result:
        if command_length >= 6:
            return Result.of_failure(f"Usage：\n/permission group remove (groupName) (permission)")
        if self._check_permission(Permission.Group.Remove):
            return self._permission_reject
        if command[4] not in ps_manager.permission_node:
            return Result.of_failure(f"{command[4]}不是一个有效的权限节点")
        return ps_manager.remove_group_permission(command[3], command[4])

    async def _parse_group_clone_command(self, command: List[str], command_length: int) -> Result:
        if command_length >= 6:
            return Result.of_failure(f"Usage：\n/permission group clone (groupName) (groupName)")
        if self._check_permission(Permission.Group.Clone):
            return self._permission_reject
        msg = f"确认克隆权限组「{command[3]}」的`所有权限`到权限组「{command[4]}」(是/否)？"
        target = (await message_sender.send_message(self._message.group_id, msg))[0]
        result = await reply_manager.wait_reply_async(self._message, 60)
        match result:
            case ReplyType.REJECT:
                await message_sender.send_quote_message(self._message.group_id, target.id, "操作已取消",
                                                        self._message.sender_id)
                return Result.of_success()
            case ReplyType.ACCEPT:
                res = ps_manager.clone_group_permission(command[3], command[4])
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

    async def _parse_group_check_command(self, command: List[str], command_length: int) -> Result:
        if command_length >= 6:
            return Result.of_failure(f"Usage：\n/permission group check (groupName) (permission)")
        if self._check_permission(Permission.Group.Check):
            return self._permission_reject
        if command[4] not in ps_manager.permission_node:
            return Result.of_failure(f"{command[4]}不是一个有效的权限节点")
        res = ps_manager.check_group_permission(command[3], command[4])
        if res.is_success:
            return Result.of_success(f"权限节点「{command[4]}」存在于权限组「{command[3]}」中")
        return Result.of_success(f"权限节点「{command[4]}」不存在于权限组「{command[3]}」中")

    async def _parse_group_parent_add_command(self, command: List[str], command_length: int) -> Result:
        if command_length >= 7:
            return Result.of_failure(f"Usage：\n/permission group group add (groupName) (groupName)")
        if self._check_permission(Permission.Group.Parent.Add):
            return self._permission_reject
        return ps_manager.add_group_parent(command[4], command[5])

    async def _parse_group_parent_remove_command(self, command: List[str], command_length: int) -> Result:
        if command_length >= 7:
            return Result.of_failure(f"Usage：\n/permission group group remove (groupName) (groupName)")
        if self._check_permission(Permission.Group.Parent.Del):
            return self._permission_reject
        return ps_manager.remove_group_parent(command[4], command[5])

    async def _parse_group_parent_command(self, command: List[str], command_length: int) -> Result:
        match command[3]:
            case "add" | "a":
                return await self._parse_group_parent_add_command(command, command_length)
            case "remove" | "r":
                return await self._parse_group_parent_remove_command(command, command_length)
            case _:
                return Result.of_failure("Usage：\n"
                                         "/permission group group add (groupName) (groupName)\n"
                                         "/permission group group remove (groupName) (groupName)")
