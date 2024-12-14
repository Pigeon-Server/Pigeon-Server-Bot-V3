from asyncio import gather, run
from typing import Any, Optional, Union, Callable, Awaitable, overload

from src.bus.event.event import Event


class EventBus:
    """
    EventBus 基类，提供事件订阅、发布和切面逻辑的功能。
    """

    def __init__(self):
        self._subscribers = {}
        self._aspects = {}
        self._global_aspects = []

    def subscribe(self, event_type: Union[Event, str], callback: Callable[..., Awaitable[Any]]) -> None:
        """
        订阅事件。
        :param event_type: 事件类型（字符串）
        :param callback: 异步回调函数，事件触发时调用
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: Union[Event, str], callback: Callable[..., Awaitable[Any]]) -> None:
        """
        取消订阅事件。
        :param event_type: 事件类型（字符串）
        :param callback: 异步回调函数
        """
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(callback)
            if not self._subscribers[event_type]:
                del self._subscribers[event_type]

    def publish_sync(self, event_type: Union[Event, str], *args, **kwargs) -> None:
        run(self.publish(event_type, *args, **kwargs))

    async def publish(self, event_type: Union[Event, str], *args, **kwargs) -> None:
        """
        发布事件，通知所有订阅者。
        :param event_type: 事件类型（字符串）
        :param args: 传递给回调函数的参数
        :param kwargs: 传递给回调函数的关键字参数
        """
        for aspect in self._global_aspects:
            if await aspect(event_type, *args, **kwargs):
                return

        if event_type in self._aspects:
            for aspect in self._aspects[event_type]:
                if await aspect(*args, **kwargs):
                    return

        if event_type in self._subscribers:
            await gather(*(callback(*args, **kwargs) for callback in self._subscribers[event_type]))

    def clear(self):
        """
        清空所有订阅者和事件类型。
        """
        self._subscribers.clear()
        self._global_aspects.clear()
        self._aspects.clear()

    def add_global_aspect(self, aspect: Callable[[Union[Event, str], ...], Awaitable[Optional[bool]]]) -> None:
        """
        添加全局切面函数。
        :param aspect: 异步切面函数，接收事件类型和参数，返回布尔值。如果返回True代表该event被截断，False或者None则表示继续。
        """
        self._global_aspects.append(aspect)

    def remove_global_aspect(self, aspect: Callable[[Union[Event, str], ...], Awaitable[Optional[bool]]]) -> None:
        """
        移除全局切面函数。
        :param aspect: 异步切面函数
        """
        self._global_aspects.remove(aspect)

    def add_aspect(self, event_type: Union[Event, str], aspect: Callable[..., Awaitable[Optional[bool]]]) -> None:
        """
        添加事件切面函数。
        :param event_type: 事件类型（字符串）
        :param aspect: 异步切面函数，接收参数，返回布尔值。如果返回True代表该event被截断，False或者None则表示继续。
        """
        if event_type not in self._aspects:
            self._aspects[event_type] = []
        self._aspects[event_type].append(aspect)

    def remove_aspect(self, event_type: Union[Event, str], aspect: Callable[..., Awaitable[Optional[bool]]]) -> None:
        """
        移除事件切面函数。
        :param event_type: 事件类型（字符串）
        :param aspect: 异步切面函数
        """
        if event_type in self._aspects:
            self._aspects[event_type].remove(aspect)
            if not self._aspects[event_type]:
                del self._aspects[event_type]
