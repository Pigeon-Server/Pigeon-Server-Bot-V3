from typing import Dict, Optional

from satori import Image

from src.bot.thread import permission_image_dir
from src.command.command_manager import CommandManager
from src.element.message import Message
from src.element.permissions import Permission
from src.element.result import Result
from src.type.types import ReplyType
from src.utils.message_helper import MessageHelper
from src.utils.permission_helper import PermissionHelper
from src.utils.reply_message import ReplyMessageSender


def parser_permission_data(msg: str, data: Dict) -> Result:
    if data is None:
        return Result.of_success("未查询到权限记录")
    if "group" in data.keys():
        msg += "权限组: \n" + "\n".join(data["group"]) + "\n"
    if "parent" in data.keys():
        msg += "父权限组: \n" + "\n".join(data["parent"]) + "\n"
    if "permission" in data.keys():
        msg += "权限: \n" + "\n".join(data["permission"])
    return Result.of_success(msg.removesuffix("\n"))


@CommandManager.register_command("/permission",
                                 command_docs="展示permission模块的所有命令及其帮助",
                                 alia_list=["/ps"])
def permission_command(_: Message, __: list[str]) -> Optional[Result]:
    return Result.of_failure(f"Permission模块帮助: \n"
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


@CommandManager.register_command("/permission player add",
                                 command_require_permission=Permission.Player.Add,
                                 command_docs="为某个用户添加某条权限",
                                 command_usage="/permission player add (At | id) (permission)",
                                 alia_list=["/ps p a"])
async def permission_player_add(_: Message, command: list[str]) -> Optional[Result]:
    if len(command) >= 6:
        return None
    if not PermissionHelper.check_permission_node(command[4]):
        return Result.of_failure(f"{command[4]}不是一个有效的权限节点")
    user_id = PermissionHelper.get_user_id(command[3])
    if user_id is None:
        return None
    return PermissionHelper.get_permission_manager().add_player_permission(user_id, command[4])


@CommandManager.register_command("/permission player remove",
                                 command_require_permission=Permission.Player.Del,
                                 command_docs="为某个用户移除某条权限",
                                 command_usage="/permission player remove (At | id) (permission)",
                                 alia_list=["/ps p r"])
async def permission_player_remove(_: Message, command: list[str]) -> Optional[Result]:
    if len(command) >= 6:
        return None
    if not PermissionHelper.check_permission_node(command[4]):
        return Result.of_failure(f"{command[4]}不是一个有效的权限节点")
    user_id = PermissionHelper.get_user_id(command[3])
    if user_id is None:
        return None
    return PermissionHelper.get_permission_manager().remove_player_permission(user_id, command[4])


@CommandManager.register_command("/permission player clone",
                                 command_require_permission=Permission.Player.Clone,
                                 command_docs="将某个用户的全部权限克隆到某用户",
                                 command_usage="/permission player clone (At | id) (At | id)")
async def permission_player_clone(message: Message, command: list[str]) -> Optional[Result]:
    if len(command) >= 6:
        return None
    clone_src = PermissionHelper.get_user_id(command[3])
    clone_dest = PermissionHelper.get_user_id(command[4])
    if clone_src is None or clone_dest is None:
        return None
    msg = f"确认克隆「{clone_src}」用户的`所有权限`到「{clone_dest}」(是/否)？"
    target = (await MessageHelper.send_message(message.group_id, msg))[0]
    result = await ReplyMessageSender.wait_reply_async(message, 60)
    match result:
        case ReplyType.REJECT:
            await MessageHelper.send_quote_message(message.group_id, target.id, "操作已取消",
                                                   message.sender_id)
            return Result.of_success()
        case ReplyType.ACCEPT:
            res = PermissionHelper.get_permission_manager().clone_player_permission(clone_src, clone_dest)
            if res.is_success:
                await MessageHelper.send_quote_message(message.group_id, target.id,
                                                       f"操作成功, {res.message}",
                                                       message.sender_id)
                return Result.of_success()
            await MessageHelper.send_quote_message(message.group_id, target.id,
                                                   f"操作失败, {res.message}",
                                                   message.sender_id)
            return Result.of_failure()
        case ReplyType.TIMEOUT:
            await MessageHelper.send_quote_message(message.group_id, target.id, "操作超时",
                                                   message.sender_id)
            return Result.of_failure()
    return Result.of_failure()


@CommandManager.register_command("/permission player check",
                                 command_require_permission=Permission.Player.Check,
                                 command_docs="检查某个玩家是否具有某权限",
                                 command_usage="/permission player check (At | id) (permission)")
async def permission_player_check(_: Message, command: list[str]) -> Optional[Result]:
    if len(command) >= 6:
        return None
    if not PermissionHelper.check_permission_node(command[4]):
        return Result.of_failure(f"{command[4]}不是一个有效的权限节点")
    user_id = PermissionHelper.get_user_id(command[3])
    if user_id is None:
        return None
    res = PermissionHelper.check_user_permission(user_id, command[4])
    if res:
        return Result.of_success(f"用户「{user_id}」拥有权限节点「{command[4]}」")
    return Result.of_success(f"用户「{user_id}」没有权限节点「{command[4]}」")


@CommandManager.register_command("/permission player group add",
                                 command_require_permission=Permission.Player.Parent.Add,
                                 command_docs="将某位玩家添加到某个权限组内",
                                 command_usage="/permission player group add (At | id) (groupName)",
                                 alia_list=["/ps p g a"])
async def permission_player_group_add(_: Message, command: list[str]) -> Optional[Result]:
    if len(command) >= 7:
        return None
    user_id = PermissionHelper.get_user_id(command[4])
    if user_id is None:
        return None
    return PermissionHelper.get_permission_manager().add_player_parent(user_id, command[5])


@CommandManager.register_command("/permission player group remove",
                                 command_require_permission=Permission.Player.Parent.Del,
                                 command_docs="将某个玩家从某个权限组中移除",
                                 command_usage="/permission player group remove (At | id) (groupName)",
                                 alia_list=["/ps p g r"])
async def permission_player_group_remove(_: Message, command: list[str]) -> Optional[Result]:
    if len(command) >= 7:
        return None
    user_id = PermissionHelper.get_user_id(command[4])
    if user_id is None:
        return None
    return PermissionHelper.get_permission_manager().remove_player_parent(user_id, command[5])


@CommandManager.register_command("/permission player group set",
                                 command_require_permission=Permission.Player.Parent.Set,
                                 command_docs="设置某个玩家的权限组",
                                 command_usage="/permission player group set (At | id) (groupName)",
                                 alia_list=["/ps p g s"])
async def permission_player_group_set(_: Message, command: list[str]) -> Optional[Result]:
    if len(command) >= 7:
        return None
    user_id = PermissionHelper.get_user_id(command[4])
    if user_id is None:
        return None
    return PermissionHelper.get_permission_manager().set_player_parent(user_id, command[5])


@CommandManager.register_command("/permission player del",
                                 command_require_permission=Permission.Player.Del,
                                 command_docs="从权限系统中移除某用户",
                                 command_usage="/permission player del (At | id)",
                                 alia_list=["/ps p d"])
async def permission_player_del(message: Message, command: list[str]) -> Optional[Result]:
    if len(command) >= 5:
        return None
    user_id = PermissionHelper.get_user_id(command[3])
    if user_id is None:
        return None
    msg = f"是否删除「{user_id}」用户的权限信息(是/否)？"
    target = (await MessageHelper.send_message(message.group_id, msg))[0]
    result = await ReplyMessageSender.wait_reply_async(message, 60)
    match result:
        case ReplyType.REJECT:
            await MessageHelper.send_quote_message(message.group_id, target.id, "操作已取消",
                                                   message.sender_id)
            return Result.of_success()
        case ReplyType.ACCEPT:
            res = PermissionHelper.get_permission_manager().del_player(user_id)
            if res.is_success:
                await MessageHelper.send_quote_message(message.group_id, target.id,
                                                       f"操作成功, {res.message}",
                                                       message.sender_id)
                return Result.of_success()
            await MessageHelper.send_quote_message(message.group_id, target.id,
                                                   f"操作失败, {res.message}",
                                                   message.sender_id)
            return Result.of_failure()
        case ReplyType.TIMEOUT:
            await MessageHelper.send_quote_message(message.group_id, target.id, "操作超时",
                                                   message.sender_id)
            return Result.of_failure()
    return Result.of_failure()


@CommandManager.register_command("/permission player list",
                                 command_require_permission=Permission.Player.List,
                                 command_docs="列出某位用户具有的所有权限节点",
                                 command_usage="/permission player list (At | id)",
                                 alia_list=["/ps p l"])
async def permission_player_list(_: Message, command: list[str]) -> Optional[Result]:
    if len(command) >= 5:
        return None
    user_id = PermissionHelper.get_user_id(command[3])
    if user_id is None:
        return None
    msg = f"「{user_id}」拥有的权限为：\n"
    msg += "\n".join(PermissionHelper.get_permission_manager().get_player_permission(user_id))
    return Result.of_success(msg.removesuffix("\n"))


@CommandManager.register_command("/permission player info",
                                 command_require_permission=Permission.Player.Info,
                                 command_docs="列出某位用户的权限信息",
                                 command_usage="/permission player info (At | id)",
                                 alia_list=["/ps p i"])
async def permission_player_info(_: Message, command: list[str]) -> Optional[Result]:
    if len(command) >= 5:
        return None
    user_id = PermissionHelper.get_user_id(command[3])
    if user_id is None:
        return None
    data = PermissionHelper.get_permission_manager().get_player_info(user_id)
    msg = f"「{user_id}」拥有的权限为：\n"
    return parser_permission_data(msg, data)


@CommandManager.register_command("/permission player create",
                                 command_require_permission=Permission.Player.Create,
                                 command_docs="向权限系统中添加一位用户",
                                 command_usage="/permission player create (At | id) [groupName]",
                                 alia_list=["/ps p c"])
async def permission_player_create(_: Message, command: list[str]) -> Optional[Result]:
    if (command_length := len(command)) >= 6:
        return None
    user_id = PermissionHelper.get_user_id(command[3])
    if user_id is None:
        return None
    if command_length == 4:
        res = PermissionHelper.get_permission_manager().create_player(user_id)
    else:
        res = PermissionHelper.get_permission_manager().create_player(user_id, command[4])
    return res


@CommandManager.register_command("/permission group add",
                                 command_require_permission=Permission.Group.Add,
                                 command_docs="向某个权限组中添加某条权限",
                                 command_usage="/permission group add (groupName) (permission)",
                                 alia_list=["/ps g a"])
async def permission_group_add(_: Message, command: list[str]) -> Optional[Result]:
    if len(command) >= 6:
        return None
    if not PermissionHelper.check_permission_node(command[4]):
        return Result.of_failure(f"{command[4]}不是一个有效的权限节点")
    return PermissionHelper.get_permission_manager().add_group_permission(command[3], command[4])


@CommandManager.register_command("/permission group remove",
                                 command_require_permission=Permission.Group.Remove,
                                 command_docs="从某个权限组中移除某条权限",
                                 command_usage="/permission group remove (groupName) (permission)",
                                 alia_list=["/ps g r"])
async def permission_group_remove(_: Message, command: list[str]) -> Optional[Result]:
    if len(command) >= 6:
        return None
    if not PermissionHelper.check_permission_node(command[4]):
        return Result.of_failure(f"{command[4]}不是一个有效的权限节点")
    return PermissionHelper.get_permission_manager().remove_group_permission(command[3], command[4])


@CommandManager.register_command("/permission group clone",
                                 command_require_permission=Permission.Group.Clone,
                                 command_docs="从某个权限组复制权限到某个权限组",
                                 command_usage="/permission group clone (groupName) (groupName)")
async def permission_group_clone(message: Message, command: list[str]) -> Optional[Result]:
    if len(command) >= 6:
        return None
    msg = f"确认克隆权限组「{command[3]}」的`所有权限`到权限组「{command[4]}」(是/否)？"
    target = (await MessageHelper.send_message(message.group_id, msg))[0]
    result = await ReplyMessageSender.wait_reply_async(message, 60)
    match result:
        case ReplyType.REJECT:
            await MessageHelper.send_quote_message(message.group_id, target.id, "操作已取消",
                                                   message.sender_id)
            return Result.of_success()
        case ReplyType.ACCEPT:
            res = PermissionHelper.get_permission_manager().clone_group_permission(command[3], command[4])
            if res.is_success:
                await MessageHelper.send_quote_message(message.group_id, target.id,
                                                       f"操作成功, {res.message}",
                                                       message.sender_id)
                return Result.of_success()
            await MessageHelper.send_quote_message(message.group_id, target.id,
                                                   f"操作失败, {res.message}",
                                                   message.sender_id)
            return Result.of_failure()
        case ReplyType.TIMEOUT:
            await MessageHelper.send_quote_message(message.group_id, target.id, "操作超时",
                                                   message.sender_id)
            return Result.of_failure()
    return Result.of_failure()


@CommandManager.register_command("/permission group check",
                                 command_require_permission=Permission.Group.Check,
                                 command_docs="检查某个权限组是否有某条权限",
                                 command_usage="/permission group check (groupName) (permission)")
async def permission_group_check(_: Message, command: list[str]) -> Optional[Result]:
    if len(command) >= 6:
        return None
    if not PermissionHelper.check_permission_node(command[4]):
        return Result.of_failure(f"{command[4]}不是一个有效的权限节点")
    res = PermissionHelper.check_group_permission(command[3], command[4])
    if res:
        return Result.of_success(f"权限节点「{command[4]}」存在于权限组「{command[3]}」中")
    return Result.of_success(f"权限节点「{command[4]}」不存在于权限组「{command[3]}」中")


@CommandManager.register_command("/permission group group add",
                                 command_require_permission=Permission.Group.Parent.Add,
                                 command_docs="将某个权限组添加到某个权限组中",
                                 command_usage="/permission group group add (groupName) (groupName)",
                                 alia_list=["/ps g g a"])
async def permission_group_group_add(_: Message, command: list[str]) -> Optional[Result]:
    if len(command) >= 7:
        return None
    return PermissionHelper.get_permission_manager().add_group_parent(command[4], command[5])


@CommandManager.register_command("/permission group group remove",
                                 command_require_permission=Permission.Group.Parent.Del,
                                 command_docs="将某个权限组从某个权限组中移除",
                                 command_usage="/permission group group remove (groupName) (groupName)",
                                 alia_list=["/ps g g r"])
async def permission_group_group_remove(_: Message, command: list[str]) -> Optional[Result]:
    if len(command) >= 7:
        return None
    return PermissionHelper.get_permission_manager().remove_group_parent(command[4], command[5])


@CommandManager.register_command("/permission group del",
                                 command_require_permission=Permission.Group.Del,
                                 command_docs="从权限系统中删除某个权限组",
                                 command_usage="/permission group del (groupName)",
                                 alia_list=["/ps g d"])
async def permission_group_del(message: Message, command: list[str]) -> Optional[Result]:
    if len(command) >= 5:
        return None
    msg = f"是否删除权限组「{command[3]}」(是/否)？"
    target = (await MessageHelper.send_message(message.group_id, msg))[0]
    result = await ReplyMessageSender.wait_reply_async(message, 60)
    match result:
        case ReplyType.REJECT:
            await MessageHelper.send_quote_message(message.group_id, target.id, "操作已取消",
                                                   message.sender_id)
            return Result.of_success()
        case ReplyType.ACCEPT:
            res = PermissionHelper.get_permission_manager().del_group(command[3])
            if res.is_success:
                await MessageHelper.send_quote_message(message.group_id, target.id,
                                                       f"操作成功, {res.message}",
                                                       message.sender_id)
                return Result.of_success()
            await MessageHelper.send_quote_message(message.group_id, target.id,
                                                   f"操作失败, {res.message}",
                                                   message.sender_id)
            return Result.of_failure()
        case ReplyType.TIMEOUT:
            await MessageHelper.send_quote_message(message.group_id, target.id, "操作超时",
                                                   message.sender_id)
            return Result.of_failure()
    return Result.of_failure()


@CommandManager.register_command("/permission group list",
                                 command_require_permission=Permission.Group.List,
                                 command_docs="列出某个权限组包含的所有权限",
                                 command_usage="/permission group list (groupName)",
                                 alia_list=["/ps g l"])
async def permission_group_list(_: Message, command: list[str]) -> Optional[Result]:
    if len(command) >= 5:
        return None
    msg = f"「{command[3]}」拥有的权限为：\n"
    msg += "\n".join(PermissionHelper.get_permission_manager().get_group_permission(command[3]))
    return Result.of_success(msg.removesuffix("\n"))


@CommandManager.register_command("/permission group info",
                                 command_require_permission=Permission.Group.Info,
                                 command_docs="列出某个权限组的权限信息",
                                 command_usage="/permission group info (groupName)",
                                 alia_list=["/ps g i"])
async def permission_group_info(_: Message, command: list[str]) -> Optional[Result]:
    if len(command) >= 5:
        return None
    data = PermissionHelper.get_permission_manager().get_group_info(command[3])
    msg = f"「{command[3]}」拥有的权限为：\n"
    return parser_permission_data(msg, data)


@CommandManager.register_command("/permission group create",
                                 command_require_permission=Permission.Group.Create,
                                 command_docs="为权限系统创建一个新权限组",
                                 command_usage="/permission group create (groupName)",
                                 alia_list=["/ps g c"])
async def permission_group_create(_: Message, command: list[str]) -> Optional[Result]:
    if (command_length := len(command)) >= 6:
        return None
    if command_length == 4:
        res = PermissionHelper.get_permission_manager().create_group(command[3])
    else:
        res = PermissionHelper.get_permission_manager().create_group(command[3], command[4])
    return res


@CommandManager.register_command("/permission reload",
                                 command_require_permission=Permission.Group.Reload.Common,
                                 command_docs="重载权限系统",
                                 alia_list=["/ps r"])
async def permission_reload(message: Message, command: list[str]) -> Optional[Result]:
    if (command_length := len(command)) == 2:
        return Result.of_success(PermissionHelper.get_permission_manager().reload_group_permission().message)
    if command_length == 3 and command[2] == "true":
        if PermissionHelper.require_permission(message, Permission.Group.Reload.Force):
            return Result.of_success(PermissionHelper.get_permission_manager().reload_group_permission(True).message)
        return Result.of_failure()
    return None


@CommandManager.register_command("/permission list",
                                 command_require_permission=Permission.ShowList,
                                 command_docs="获取所有权限节点列表",
                                 alia_list=["/ps l"])
async def permission_list(message: Message, command: list[str]) -> Optional[Result]:
    if len(command) == 2:
        with open(permission_image_dir, "rb") as f:
            await MessageHelper.send_message(message.group_id,
                                             [Image.of(raw=f.read(), mime="image/png")])
        return Result.of_success()
    return None
