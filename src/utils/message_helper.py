from typing import List, Optional, Union, overload

from satori import At, Element, Event, Guild, Quote
from satori.client import Account
from satori.model import MessageReceipt

from src.base.config import sys_config
from src.base.logger import logger
from src.element.message import Message
from src.type.types import MessageType


class MessageHelper:
    _account: Optional[Account] = None

    @classmethod
    def set_account(cls, account: Account) -> None:
        cls._account = account

    @classmethod
    @overload
    async def send_message(cls, channel_id: str, message: str) -> List[MessageReceipt]:
        ...

    @classmethod
    @overload
    async def send_message(cls, channel_id: str, message: list[str | Element]) -> List[MessageReceipt]:
        ...

    @classmethod
    @overload
    async def send_message(cls, channel_id: Event, message: str) -> List[MessageReceipt]:
        ...

    @classmethod
    @overload
    async def send_message(cls, channel_id: Event, message: list[str | Element]) -> List[MessageReceipt]:
        ...

    @classmethod
    async def send_message(cls, channel_id: Union[str, Event],
                           message: MessageType) -> list[MessageReceipt]:
        if cls._account is None:
            raise ValueError("Account is not set")
        if sys_config.dev:
            if isinstance(message, str):
                message = f"{'-' * 5}Dev{'-' * 5}\n{message}"
            if isinstance(message, list):
                message = [f"{'-' * 5}Dev{'-' * 5}\n"] + message
        log_message = Message.parse(message)
        if isinstance(channel_id, str):
            channel: Guild = await cls._account.guild_get(guild_id=channel_id)
            logger.info(f'[消息]->{channel.name}({channel.id}): {log_message}')
            return await cls._account.send_message(channel_id, message)
        if isinstance(channel_id, Event):
            logger.info(f'[消息]->{channel_id.guild.name}({channel_id.guild.id}): {log_message}')
            return await cls._account.send(channel_id, message)

    @classmethod
    async def send_quote_message(cls, channel_id: str, replay_id: Union[str, MessageReceipt], msg: str,
                                 at_id: Optional[str] = None) -> List[MessageReceipt]:
        if cls._account is None:
            raise ValueError("Account is not set")
        message: List[Union[str, Element]] = [Quote(replay_id, False)]
        if at_id:
            message.append(At(at_id))
            message.append(" ")
        message.append(msg)
        return await cls.send_message(channel_id, message)

    @classmethod
    async def retract_message(cls, message: Message) -> None:
        try:
            await cls._account.message_delete(message.group_id, message.message_id)
        except Exception as e:
            logger.error(e)

    @classmethod
    async def mute_member(cls, message: Message) -> None:
        try:
            await cls._account.guild_member_mute(message.group_id, message.sender_id, 60)
        except Exception as e:
            logger.error(e)
