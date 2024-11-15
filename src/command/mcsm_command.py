from typing import List, Optional

from src.bot.plugin import mcsm
from src.command.command_manager import CommandManager
from src.command.command_parser import CommandParser
from src.element.message import Message
from src.element.permissions import Mcsm
from src.element.result import Result
from src.type.types import ReplyType
from src.utils.message_sender import MessageSender
from src.utils.reply_message import ReplyMessageSender


class McsmCommand(CommandParser):
    _command_helper: Result = Result.of_failure(
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
    
    @staticmethod
    @CommandManager.add_command_parser("mcsm_command")
    async def parse(message: Message, command: List[str]) -> Optional[Result]:
        await CommandParser.parse(message, command)
        command_length = len(command)
        if command[0] not in ["mcsm"]:
            return None
        if command_length < 2:
            return McsmCommand._command_helper
        match command[1]:
            case "check" | "c":
                if command_length < 3 or command_length > 4:
                    return Result.of_failure("/mcsm check (InstanceName) [ServerName]")
                if McsmCommand._check_permission(Mcsm.Check):
                    return McsmCommand._permission_reject
                if command_length == 3:
                    return mcsm.check_instance_status(command[2])
                return mcsm.check_instance_status(command[2], command[3])
            case "list" | "l":
                if command_length > 3:
                    return Result.of_failure("/mcsm list [ServerName]")
                if McsmCommand._check_permission(Mcsm.List):
                    return McsmCommand._permission_reject
                if command_length == 2:
                    return mcsm.list_instance()
                return mcsm.list_instance(command[2])
            case "rename" | "r":
                if command_length != 4:
                    return Result.of_failure("/mcsm rename (OriginalName) (NewName)")
                if McsmCommand._check_permission(Mcsm.Rename):
                    return McsmCommand._permission_reject
                return mcsm.rename(command[2], command[3])
            case "status":
                if command_length != 2:
                    return Result.of_failure("/mcsm status")
                if McsmCommand._check_permission(Mcsm.Check):
                    return McsmCommand._permission_reject
                return mcsm.status()
            case "update" | "u":
                if command_length > 3:
                    return Result.of_failure("/mcsm update [true]")
                if McsmCommand._check_permission(Mcsm.Rename):
                    return McsmCommand._permission_reject
                if command_length == 2:
                    mcsm.get_mcsm_info()
                    return Result.of_success("操作成功")
                if command[2].lower() == "true":
                    msg = f"确认强制更新mcsm信息\n这将会清空所有自定义设置！\n是否继续(是/否)？"
                    target = (await MessageSender.send_message(McsmCommand._message.group_id, msg))[0]
                    result = await ReplyMessageSender.wait_reply_async(McsmCommand._message, 60)
                    match result:
                        case ReplyType.REJECT:
                            await MessageSender.send_quote_message(McsmCommand._message.group_id, target.id, "操作已取消",
                                                                   McsmCommand._message.sender_id)
                            return Result.of_success()
                        case ReplyType.ACCEPT:
                            mcsm.get_mcsm_info(True)
                            await MessageSender.send_quote_message(McsmCommand._message.group_id, target.id,
                                                                   "操作成功",
                                                                   McsmCommand._message.sender_id)
                            return Result.of_failure()
                        case ReplyType.TIMEOUT:
                            await MessageSender.send_quote_message(McsmCommand._message.group_id, target.id, "操作超时",
                                                                   McsmCommand._message.sender_id)
                            return Result.of_failure()
                    return Result.of_failure()
                return Result.of_failure("/mcsm update [true]")
            case "stop" | "s":
                if command_length < 3 or command_length > 4:
                    return Result.of_failure("/mcsm stop (InstanceName) [ServerName]")
                if McsmCommand._check_permission(Mcsm.Stop):
                    return McsmCommand._permission_reject
                if command_length == 3:
                    return mcsm.stop(command[2])
                return mcsm.stop(command[2], command[3])
            case "kill" | "k":
                if command_length < 3 or command_length > 4:
                    return Result.of_failure("/mcsm kill (InstanceName) [ServerName]")
                if McsmCommand._check_permission(Mcsm.Kill):
                    return McsmCommand._permission_reject
                if command_length == 3:
                    return mcsm.stop(command[2], force_kill=True)
                return mcsm.stop(command[2], command[3], True)
            case "start" | "S":
                if command_length < 3 or command_length > 4:
                    return Result.of_failure("/mcsm start (InstanceName) [ServerName]")
                if McsmCommand._check_permission(Mcsm.Start):
                    return McsmCommand._permission_reject
                if command_length == 3:
                    return mcsm.start(command[2])
                return mcsm.start(command[2], command[3])
            case "restart" | "R":
                if command_length < 3 or command_length > 4:
                    return Result.of_failure("/mcsm restart (InstanceName) [ServerName]")
                if McsmCommand._check_permission(Mcsm.Restart):
                    return McsmCommand._permission_reject
                if command_length == 3:
                    return mcsm.restart(command[2])
                return mcsm.restart(command[2], command[3])
            case "command" | "C":
                if command_length < 4:
                    return Result.of_failure("/mcsm command (InstanceName) (command)")
                if McsmCommand._check_permission(Mcsm.Rename):
                    return McsmCommand._permission_reject
                command_list = command[3:]
                return await mcsm.run_command(command[2], " ".join(command_list))
