from typing import Optional
from src.command.command_manager import CommandManager
from src.database.message_model import BlockWord
from src.element.message import Message
from src.element.permissions import BlockWords
from src.element.result import Result
from src.module.block_message import BlockMessage


def get_group_id(group_id: str) -> Optional[str]:
    if group_id == "default":
        return "default"
    try:
        return str(int(group_id))
    except ValueError:
        return None


@CommandManager.register_command("/blockword",
                                 command_docs="展示blockword模块的所有命令及其帮助",
                                 alia_list=["/bw"])
async def blockword_command(_: Message, __: list[str]) -> Optional[Result]:
    return Result.of_failure("屏蔽词管理：\n"
                             "/blockword add [group_id] [word] ... 添加屏蔽词\n"
                             "/blockword del [group_id] [word] ... 删除屏蔽词\n"
                             "/blockword list 列出所有屏蔽词")


@CommandManager.register_command("/blockword list",
                                 command_docs="列出所有屏蔽词",
                                 alia_list=["/bw l"],
                                 command_require_permission=BlockWords.List)
async def blockword_list_command(_: Message, __: list[str]) -> Optional[Result]:
    res: list[BlockWord] = BlockWord.select().order_by(BlockWord.group_id).execute()
    data = {}
    for block in res:
        if block.group_id not in data:
            data[block.group_id] = [block.block_word]
        else:
            data[block.group_id].append(block.block_word)
    return Result.of_success(''.join([f"{k}:\n\t{'\n\t'.join(v)}\n" for k, v in data.items()]))


@CommandManager.register_command("/blockword add",
                                 command_docs="添加屏蔽词",
                                 alia_list=["/bw a"],
                                 command_require_permission=BlockWords.Add)
async def blockword_add_command(message: Message, command_list: list[str]) -> Optional[Result]:
    if len(command_list) < 3:
        return None
    group_id = get_group_id(command_list[2])
    if group_id is None:
        group_id = message.group_id
        words = command_list[2:]
    else:
        words = command_list[3:]
    data = [{"group_id": group_id,
             "block_word": word
             } for word in words]
    for i in range(0, len(data), 100):
        BlockWord.insert_many(data[i:i + 100]).execute()
    BlockMessage.update_block_words()
    return Result.of_success(f"为群「{group_id}」添加屏蔽词「{', '.join(words)}」")


@CommandManager.register_command("/blockword del",
                                 command_docs="删除屏蔽词",
                                 alia_list=["/bw d"],
                                 command_require_permission=BlockWords.Del)
async def blockword_del_command(message: Message, command_list: list[str]) -> Optional[Result]:
    if len(command_list) < 3:
        return None
    group_id = get_group_id(command_list[2])
    if group_id is None:
        group_id = message.group_id
        words = command_list[2:]
    else:
        words = command_list[3:]
    BlockWord.delete().where((BlockWord.group_id == group_id) & (BlockWord.block_word << words)).execute()
    BlockMessage.update_block_words()
    return Result.of_success(f"为群「{group_id}」删除屏蔽词「{', '.join(words)}」")


@CommandManager.register_command("/blockword reload",
                                 command_docs="重载屏蔽词",
                                 alia_list=["/bw r"],
                                 command_require_permission=BlockWords.Reload)
async def blockword_del_command(_: Message, __: list[str]) -> Optional[Result]:
    BlockMessage.update_block_words()
    return Result.of_success(f"重载屏蔽词成功")
