from typing import Optional

from src.bot.plugin import mcsm
from src.command.command_manager import CommandManager
from src.element.message import Message
from src.element.permissions import Mcsm
from src.element.result import Result
from src.type.types import ReplyType
from src.utils.message_helper import MessageHelper
from src.utils.permission_helper import PermissionHelper
from src.utils.reply_message import ReplyMessageSender


@CommandManager.register_command("/mcsm", command_docs="展示mcsm模块的所有命令及其帮助")
async def mcsm_help(_: Message, __: list[str]) -> Optional[Result]:
    return Result.of_failure(
        "MCSM模块帮助：\n"
        "/mcsm check (InstanceName) [ServerName] 查询指定实例信息\n"
        "/mcsm list [ServerName] 列出某一守护进程的所有实例名称\n"
        "/mcsm rename (OriginalName) (NewName) 重命名某一守护进程或实例\n"
        "/mcsm update [true] （强制）更新实例信息\n"
        "/mcsm status 获取mcsm状态\n"
        "/mcsm stop (InstanceName) [ServerName] 停止某一实例\n"
        "/mcsm kill (InstanceName) [ServerName] 强行停止某一实例\n"
        "/mcsm start (InstanceName) [ServerName] 开启某一实例\n"
        "/mcsm restart (InstanceName) [ServerName] 重启某一实例\n"
        "/mcsm command (InstanceName) (Command) 向某一实例执行命令")


@CommandManager.register_command("/mcsm list",
                                 command_require_permission=Mcsm.List,
                                 command_docs="列出某一守护进程的所有实例名称",
                                 command_usage="/mcsm list [ServerName]",
                                 alia_list=["/mcsm l"])
async def mcsm_list(_: Message, command: list[str]) -> Optional[Result]:
    if (command_length := len(command)) > 3:
        return None
    if command_length == 2:
        return mcsm.list_instance()
    return mcsm.list_instance(command[2])


@CommandManager.register_command("/mcsm check",
                                 command_require_permission=Mcsm.Check,
                                 command_docs="查询指定实例信息",
                                 command_usage="/mcsm check (InstanceName) [ServerName]",
                                 alia_list=["/mcsm c"])
async def mcsm_check(_: Message, command: list[str]) -> Optional[Result]:
    if (command_length := len(command)) < 3 or command_length > 4:
        return None
    if command_length == 3:
        return mcsm.check_instance_status(command[2])
    return mcsm.check_instance_status(command[2], command[3])


@CommandManager.register_command("/mcsm rename",
                                 command_require_permission=Mcsm.Rename,
                                 command_docs="重命名某一守护进程或实例",
                                 command_usage="/mcsm rename (OriginalName) (NewName)",
                                 alia_list=["/mcsm r"])
async def mcsm_rename(_: Message, command: list[str]) -> Optional[Result]:
    if len(command) != 4:
        return None
    return mcsm.rename(command[2], command[3])


@CommandManager.register_command("/mcsm update",
                                 command_require_permission=Mcsm.Update.Common,
                                 command_docs="（强制）更新实例信息",
                                 command_usage="/mcsm update [true]",
                                 alia_list=["/mcsm u"])
async def mcsm_update(message: Message, command: list[str]) -> Optional[Result]:
    if (command_length := len(command)) > 3:
        return None
    if command_length == 2:
        mcsm.get_mcsm_info()
        return Result.of_success("操作成功")
    if await PermissionHelper.require_permission(message, Mcsm.Update.Force) and command[2].lower() == "true":
        msg = f"确认强制更新mcsm信息\n这将会清空所有自定义设置！\n是否继续(是/否)？"
        target = (await MessageHelper.send_message(message.group_id, msg))[0]
        result = await ReplyMessageSender.wait_reply_async(message, 60)
        match result:
            case ReplyType.REJECT:
                await MessageHelper.send_quote_message(message.group_id, target.id,
                                                       "操作已取消",
                                                       message.sender_id)
                return Result.of_success()
            case ReplyType.ACCEPT:
                mcsm.get_mcsm_info(True)
                await MessageHelper.send_quote_message(message.group_id, target.id,
                                                       "操作成功",
                                                       message.sender_id)
                return Result.of_failure()
            case ReplyType.TIMEOUT:
                await MessageHelper.send_quote_message(message.group_id, target.id, "操作超时",
                                                       message.sender_id)
                return Result.of_failure()
        return Result.of_failure()
    return Result.of_failure("/mcsm update [true]")


@CommandManager.register_command("/mcsm status",
                                 command_require_permission=Mcsm.Status,
                                 command_docs="获取mcsm状态")
async def mcsm_status(_: Message, command: list[str]) -> Optional[Result]:
    if len(command) != 2:
        return None
    return mcsm.status()


@CommandManager.register_command("/mcsm stop",
                                 command_require_permission=Mcsm.Stop,
                                 command_docs="停止某一实例",
                                 command_usage="/mcsm stop (InstanceName) [ServerName]",
                                 alia_list=["/mcsm s"])
async def mcsm_stop(_: Message, command: list[str]) -> Optional[Result]:
    if (command_length := len(command)) < 3 or command_length > 4:
        return None
    if command_length == 3:
        return mcsm.stop(command[2])
    return mcsm.stop(command[2], command[3])


@CommandManager.register_command("/mcsm kill",
                                 command_require_permission=Mcsm.Kill,
                                 command_docs="强行停止某一实例",
                                 command_usage="/mcsm kill (InstanceName) [ServerName]",
                                 alia_list=["/mcsm k"])
async def mcsm_kill(_: Message, command: list[str]) -> Optional[Result]:
    if (command_length := len(command)) < 3 or command_length > 4:
        return None
    if command_length == 3:
        return mcsm.stop(command[2], force_kill=True)
    return mcsm.stop(command[2], command[3], True)


@CommandManager.register_command("/mcsm start",
                                 command_require_permission=Mcsm.Start,
                                 command_docs="开启某一实例",
                                 command_usage="/mcsm start (InstanceName) [ServerName]",
                                 alia_list=["/mcsm S"])
async def mcsm_start(_: Message, command: list[str]) -> Optional[Result]:
    if (command_length := len(command)) < 3 or command_length > 4:
        return None
    if command_length == 3:
        return mcsm.start(command[2])
    return mcsm.start(command[2], command[3])


@CommandManager.register_command("/mcsm restart",
                                 command_require_permission=Mcsm.Restart,
                                 command_docs="重启某一实例",
                                 command_usage="/mcsm restart (InstanceName) [ServerName]",
                                 alia_list=["/mcsm R"])
async def mcsm_restart(_: Message, command: list[str]) -> Optional[Result]:
    if (command_length := len(command)) < 3 or command_length > 4:
        return None
    if command_length == 3:
        return mcsm.restart(command[2])
    return mcsm.restart(command[2], command[3])


@CommandManager.register_command("/mcsm command",
                                 command_require_permission=Mcsm.Command,
                                 command_docs="向某一实例执行命令",
                                 command_usage="/mcsm command (InstanceName) (Command)",
                                 alia_list=["/mcsm C"])
async def mcsm_command(_: Message, command: list[str]) -> Optional[Result]:
    if len(command) < 4:
        return None
    command_list = command[3:]
    res = await mcsm.run_command(command[2], " ".join(command_list))
    return Result.of_success(res)
