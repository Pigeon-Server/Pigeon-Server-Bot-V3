from typing import Optional
from re import compile, findall, Pattern, IGNORECASE

from src.base.event_bus import event_bus
from src.base.logger import logger
from src.bus.event.event import Event, MessageEvent
from src.database.message_model import BlockWord
from src.element.message import Message
from src.utils.message_helper import MessageHelper


class BlockMessage:
    _wordlist: Optional[dict[str, list[dict[str, int]]]] = None
    _patterns: Optional[dict[str, Pattern]] = None

    @classmethod
    def update_block_words(cls):
        cls._wordlist = {}
        cls._patterns = {}
        tmp = {}
        block_words: list[BlockWord] = BlockWord.select().execute()
        for word in block_words:
            if word.group_id not in cls._wordlist:
                cls._wordlist[word.group_id] = []
            if word.group_id not in tmp:
                tmp[word.group_id] = []
            cls._wordlist[word.group_id].append({word.block_word: word.punish_level})
            tmp[word.group_id].append(word.block_word)
        for group in tmp:
            tmp[group].sort(key=lambda x: len(x), reverse=True)
            cls._patterns[group] = compile("|".join(tmp[group]), IGNORECASE)

    @staticmethod
    @event_bus.on_event_filter(MessageEvent.MESSAGE_CREATED)
    async def check_message(message: Message, event: Event, *_, **__) -> Optional[bool]:
        logger.debug(f"Checking message: {message}")
        if message.is_command:
            return
        if BlockMessage._wordlist is None or BlockMessage._patterns is None:
            BlockMessage.update_block_words()
        if "default" in BlockMessage._patterns:
            block_word = findall(BlockMessage._patterns["default"], message.message)
            if len(block_word) != 0:
                logger.debug(f"Block word found: {block_word}")
                await MessageHelper.send_message(event, f"发现违禁词{block_word[0]}")
                await MessageHelper.retract_message(message)
                await MessageHelper.mute_member(message)
                return True
        if message.group_id in BlockMessage._patterns:
            block_word = findall(BlockMessage._patterns[message.group_id], message.message)
            if len(block_word) != 0:
                logger.debug(f"Block word found: {block_word}")
                await MessageHelper.send_message(event, f"发现违禁词{block_word[0]}")
                await MessageHelper.retract_message(message)
                await MessageHelper.mute_member(message)
                return True
