from typing import Optional, Union
from re import compile, match, Pattern, IGNORECASE

from src.base.logger import logger
from src.bus.event.event import Event
from src.database.message_model import BlockWord
from src.element.message import Message
from src.utils.message_sender import MessageSender


class BlockMessage:
    _wordlist: Optional[dict[str, list[dict[str, int]]]] = None
    _patterns: Optional[dict[str, Pattern]] = None

    @classmethod
    def updateBlockWords(cls):
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

    @classmethod
    async def checkMessage(cls, message: Message, event: Event, *_, **__) -> Optional[bool]:
        logger.debug(f"Checking message: {message}")
        if cls._wordlist is None or cls._patterns is None:
            cls.updateBlockWords()
        if "default" in cls._patterns:
            block_word = match(cls._patterns["default"], message.message)
            if block_word is not None:
                await MessageSender.send_message(event, f"发现违禁词{block_word[0]}")
                return True
        if message.group_id in cls._patterns:
            block_word = match(cls._patterns[message.group_id], message.message)
            if block_word is not None:
                await MessageSender.send_message(event, f"发现违禁词{block_word[0]}")
                return True
