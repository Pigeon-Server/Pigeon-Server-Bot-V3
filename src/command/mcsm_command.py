from typing import List, Optional

from src.bot.app import message_sender, reply_manager
from src.bot.mcsm import mcsm
from src.command.command_parser import CommandParser
from src.element.message import Message
from src.element.permissions import Mcsm
from src.element.result import Result
from src.type.types import ReplyType


class McsmCommand(CommandParser):
    _command_helper: Result = Result.of_failure(
        "MCSM模块帮助：\n"
        "/mcsm check (InstanceName) [ServerName] 查询指定实例信息\n"
        "/mcsm list [ServerName] 列出某一守护进程的所有实例名称\n"
        "/mcsm rename (OriginalName) (NewName) 重命名某一守护进程或实例\n"
        "/mcsm update [true] （强制）更新实例信息\n"
        "/mcsm stop (InstanceName) [ServerName] 停止某一实例\n"
        "/mcsm kill (InstanceName) [ServerName] 强行停止某一实例\n"
        "/mcsm start (InstanceName) [ServerName] 开启某一实例\n"
        "/mcsm restart (InstanceName) [ServerName] 重启某一实例\n"
        "/mcsm command (InstanceName) (Command) 向某一实例执行命令")

    async def parse(self, message: Message, command: List[str]) -> Optional[Result]:
        await super().parse(message, command)
        command_length = len(command)
        if command[0] not in ["mcsm"]:
            return None
        if command_length < 2:
            return self._command_helper
        match command[1]:
            case "check" | "c":
                if command_length < 3 or command_length > 4:
                    return Result.of_failure("/mcsm check (InstanceName) [ServerName]")
                if self._check_permission(Mcsm.Check):
                    return self._permission_reject
                if command_length == 3:
                    return mcsm.check_instance_status(command[2])
                return mcsm.check_instance_status(command[2], command[3])
            case "list" | "l":
                if command_length > 3:
                    return Result.of_failure("/mcsm list [ServerName]")
                if self._check_permission(Mcsm.List):
                    return self._permission_reject
                if command_length == 2:
                    return mcsm.list_instance()
                return mcsm.list_instance(command[2])
            case "rename" | "r":
                if command_length != 4:
                    return Result.of_failure("/mcsm rename (OriginalName) (NewName)")
                if self._check_permission(Mcsm.Rename):
                    return self._permission_reject
                return mcsm.rename(command[2], command[3])
            case "update" | "u":
                if command_length > 3:
                    return Result.of_failure("/mcsm update [true]")
                if self._check_permission(Mcsm.Rename):
                    return self._permission_reject
                if command_length == 2:
                    mcsm.get_mcsm_info()
                    return Result.of_success("操作成功")
                if command[2].lower() == "true":
                    msg = f"确认强制更新mcsm信息\n这将会清空所有自定义设置！\n是否继续(是/否)？"
                    target = (await message_sender.send_message(self._message.group_id, msg))[0]
                    result = await reply_manager.wait_reply_async(self._message, 60)
                    match result:
                        case ReplyType.REJECT:
                            await message_sender.send_quote_message(self._message.group_id, target.id, "操作已取消",
                                                                    self._message.sender_id)
                            return Result.of_success()
                        case ReplyType.ACCEPT:
                            mcsm.get_mcsm_info(True)
                            await message_sender.send_quote_message(self._message.group_id, target.id,
                                                                    "操作成功",
                                                                    self._message.sender_id)
                            return Result.of_failure()
                        case ReplyType.TIMEOUT:
                            await message_sender.send_quote_message(self._message.group_id, target.id, "操作超时",
                                                                    self._message.sender_id)
                            return Result.of_failure()
                    return Result.of_failure()
                return Result.of_failure("/mcsm update [true]")
            case "stop" | "s":
                if command_length < 3 or command_length > 4:
                    return Result.of_failure("/mcsm stop (InstanceName) [ServerName]")
                if self._check_permission(Mcsm.Stop):
                    return self._permission_reject
                if command_length == 3:
                    return mcsm.stop(command[2])
                return mcsm.stop(command[2], command[3])
            case "kill" | "k":
                if command_length < 3 or command_length > 4:
                    return Result.of_failure("/mcsm kill (InstanceName) [ServerName]")
                if self._check_permission(Mcsm.Kill):
                    return self._permission_reject
                if command_length == 3:
                    return mcsm.stop(command[2], force_kill=True)
                return mcsm.stop(command[2], command[3], True)
            case "start" | "S":
                if command_length < 3 or command_length > 4:
                    return Result.of_failure("/mcsm start (InstanceName) [ServerName]")
                if self._check_permission(Mcsm.Start):
                    return self._permission_reject
                if command_length == 3:
                    return mcsm.start(command[2])
                return mcsm.start(command[2], command[3])
            case "restart" | "R":
                if command_length < 3 or command_length > 4:
                    return Result.of_failure("/mcsm restart (InstanceName) [ServerName]")
                if self._check_permission(Mcsm.Restart):
                    return self._permission_reject
                if command_length == 3:
                    return mcsm.restart(command[2])
                return mcsm.restart(command[2], command[3])
            case "command" | "C":
                if command_length < 4:
                    return Result.of_failure("/mcsm command (InstanceName) (command)")
                if self._check_permission(Mcsm.Rename):
                    return self._permission_reject
                command_list = command[3:]
                return await mcsm.run_command(command[2], " ".join(command_list))
