from typing import Optional

from satori import At, Event
from satori.client import Account

from src.base.config import config
from src.bot.App import reply_manager
from src.module.message import Message
from src.module.permission_node import PermissionManager
from src.module.permissions import Permission
from src.module.reply_message import ReplyType
from src.module.server_status import ServerStatus

server = ServerStatus(config.config.server_list)
per = PermissionManager()


class Command:
    @staticmethod
    def command_split(message: Message) -> Optional[list[str]]:
        if message.message.startswith('/') or message.message.startswith('!'):
            return message.message[1:].removesuffix(" ").split(" ")
        return None

    @staticmethod
    async def command_parsing(message: Message, account: Account, event: Event) -> None:
        async def send(_msg: str) -> None:
            if config.sys_config.dev:
                await account.send(event, f"{"-" * 5}Dev{"-" * 5}\n{_msg}")
                return
            await account.send(event, _msg)

        def check_player(permission_: str) -> bool:
            return per.check_player_permission(str(event.user.id), permission_).is_success

        command = Command.command_split(message)

        if command is None:
            return

        command_length = len(command)

        per.create_player(str(event.user.id))

        match command[0]:
            case "info" | "status":
                await send(f"{await server.get_online_player()}")
            case "permission" | "ps":
                if command_length >= 2:
                    if command[1] == "list":
                        if not check_player(Permission.ShowList):
                            await send("你无权这么做")
                            return
                        if command_length == 2:
                            data = per.permission_node
                            msg = "所有权限节点: \n"
                            for raw in data:
                                msg += f"{raw}\n"
                            msg += "\n".join(data)
                            await send(msg)
                            return
                        if command_length == 3:
                            data = per.permission_node
                            msg = f"{command[2]}权限节点: \n"
                            data = list(filter(lambda x: command[2] in x, data))
                            msg += "\n".join(data)
                            await send(msg)
                            return
                        await send(f"Usage：\n/permission list [word]")
                        return
                    if command[1] == "reload":
                        if command_length == 2:
                            if not check_player(Permission.Reload.Common):
                                await send("你无权这么做")
                                return
                            await send(per.reload_group_permission().message)
                            return
                        if command_length == 3 and command[2] == "true":
                            if not check_player(Permission.Reload.Force):
                                await send("你无权这么做")
                                return
                            await send(per.reload_group_permission(True).message)
                            return
                        await send(f"Usage：\n/permission reload [force]")
                        return
                    if command[1] in ["player", "p"]:
                        if command_length >= 4:
                            match command[2]:
                                case "list" | "l":
                                    if command_length >= 5:
                                        await send(f"Usage：\n/permission player list (At | id) ")
                                        return
                                    if not check_player(Permission.Player.List):
                                        await send("你无权这么做")
                                        return
                                    if command[3].startswith("@"):
                                        at_list: list[At] = message.find(At)
                                        msg = f"{at_list[0].id}拥有的权限为：\n"
                                        msg += "\n".join(per.get_player_permission(str(at_list[0].id)))
                                    else:
                                        msg = f"{command[3]}拥有的权限为：\n"
                                        msg += "\n".join(per.get_player_permission(str(command[3])))
                                    await send(msg.removesuffix("\n"))
                                    return
                                case "info" | "i":
                                    if command_length >= 5:
                                        await send(f"Usage：\n/permission player info (At | id) ")
                                        return
                                    if not check_player(Permission.Player.Info):
                                        await send("你无权这么做")
                                        return
                                    if command[3].startswith("@"):
                                        at_list: list[At] = message.find(At)
                                        data = per.get_player_info(str(at_list[0].id))
                                        msg = f"{at_list[0].id}的信息如下:\n"
                                    else:
                                        data = per.get_player_info(str(command[3]))
                                        msg = f"{command[3]}拥有的权限为：\n"
                                    if data is None:
                                        await send("未查询到权限记录")
                                        return
                                    if "group" in data.keys():
                                        msg += "权限组: \n" + "\n".join(data["group"]) + "\n"
                                    if "permission" in data.keys():
                                        msg += "权限: \n" + "\n".join(data["permission"])
                                    await send(msg.removesuffix("\n"))
                                    return
                                case "del" | "d":
                                    # async def wait_callback(reply_type: ReplyType) -> None:
                                    #     match reply_type:
                                    #         case ReplyType.ACCEPT:
                                    #             await send("确认成功")
                                    #         case ReplyType.REJECT:
                                    #             await send("拒绝成功")
                                    #         case ReplyType.TIMEOUT:
                                    #             await send("确认时间超时")
                                    #
                                    # reply_manager.create_reply(message, wait_callback, 10).start()
                                    reply_type = await reply_manager.wait_reply_async(message, 10)
                                    match reply_type:
                                        case ReplyType.ACCEPT:
                                            await send("确认成功")
                                        case ReplyType.REJECT:
                                            await send("拒绝成功")
                                        case ReplyType.TIMEOUT:
                                            await send("确认时间超时")
                                    # if command_length >= 5:
                                    #     await send(f"Usage：\n/permission player del (At | id) ")
                                    #     return
                                    # if not check_player(Permission.Player.Del):
                                    #     await send("你无权这么做")
                                    #     return
                                    # if command[3].startswith("@"):
                                    #     at_list: list[At] = message.find(At)
                                    #     msg = f"{at_list[0].id}拥有的权限为：\n"
                                    #     msg += "\n".join(per.get_player_permission(str(at_list[0].id)))
                                    # else:
                                    #     msg = f"{command[3]}拥有的权限为：\n"
                                    #     msg += "\n".join(per.get_player_permission(str(command[3])))
                                    # await send(msg.removesuffix("\n"))
                                    return
                            return

                        # await send(f"Permission模块帮助: \n"
                        #            f"/permission player (At | id) add (permission)\n"
                        #            f"/permission player (At | id) remove (permission)\n"
                        #            f"/permission player (At | id) clone (At | id)\n"
                        #            f"/permission player (At | id) check (permission)\n"
                        #            f"/permission player (At | id) inherit add (groupName)\n"
                        #            f"/permission player (At | id) inherit remove (groupName)\n"
                        #            f"/permission player (At | id) inherit set (groupName)\n"
                        #            f"/permission player (At | id) del\n"
                        #            f"/permission player (At | id) list\n"
                        #            f"/permission player (At | id) info\n"
                        #            f"/permission player (At | id) create [groupName]\n"
                        #            f"/permission group (groupName) add (permission)\n"
                        #            f"/permission group (groupName) remove (permission)\n"
                        #            f"/permission group (groupName) clone (groupName)\n"
                        #            f"/permission group (groupName) check (permission)\n"
                        #            f"/permission group (groupName) inherit add (groupName)\n"
                        #            f"/permission group (groupName) inherit remove (groupName)\n"
                        #            f"/permission group (groupName) del\n"
                        #            f"/permission group (groupName) list\n"
                        #            f"/permission group (groupName) info\n"
                        #            f"/permission group (groupName) create\n"
                        #            f"/permission reload [force]\n"
                        #            f"/permission list [word]")
