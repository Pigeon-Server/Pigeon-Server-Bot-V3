from asyncio import Semaphore, gather, run
from typing import Any, Optional, Type, Union, Callable, Awaitable

from src.bus.event.event import Event
from src.bus.event_callback_container import EventCallbackContainer
from src.bus.handler.event_callback import EventCallback

SubScriberCallback: Type = Callable[..., Union[Any, Awaitable[Any]]]
FilterCallback: Type = Callable[..., Union[Optional[bool], Awaitable[Optional[bool]]]]


class EventBus:
    """
    EventBus 基类，提供事件订阅、发布和切面逻辑的功能。
    """

    def __init__(self, max_concurrent_tasks=10):
        self._subscribers: dict[str, EventCallbackContainer] = {}
        self._filters: dict[str, EventCallbackContainer] = {}
        self._global_filters: EventCallbackContainer = EventCallbackContainer()
        self._semaphore = Semaphore(max_concurrent_tasks)

    @staticmethod
    def _append_and_sort(target: list[EventCallback], data: EventCallback, *,
                         key=lambda item: item.weight,
                         reverse: bool = True) -> None:
        target.append(data)
        target.sort(key=key, reverse=reverse)

    def subscribe(self, event_type: Union[Event, str], callback: SubScriberCallback, *, weight: int = 1) -> None:
        if event_type not in self._subscribers:
            self._subscribers[event_type] = EventCallbackContainer()
        self._subscribers[event_type].add_callback(callback, weight)

    def unsubscribe(self, event_type: Union[Event, str], callback: SubScriberCallback) -> None:
        if event_type in self._subscribers:
            self._subscribers[event_type].remove_callback(callback)

    def publish_sync(self, event_type: Union[Event, str], *args, **kwargs) -> None:
        run(self.publish(event_type, *args, **kwargs))

    async def _run_with_semaphore(self, coroutine, *args, **kwargs):
        async with self._semaphore:
            return await coroutine(*args, **kwargs)

    async def publish(self, event_type: Union[Event, str], *args, **kwargs) -> None:
        for callback in self._global_filters.sync_callback:
            if callback(event_type, *args, **kwargs):
                return

        for callback in self._global_filters.async_callback:
            if await callback(event_type, *args, **kwargs):
                return

        if event_type in self._filters:
            for callback in self._filters[event_type].sync_callback:
                if callback(*args, **kwargs):
                    return
            for callback in self._filters[event_type].async_callback:
                if await callback(*args, **kwargs):
                    return

        if event_type in self._subscribers:
            for callback in self._subscribers[event_type].sync_callback:
                callback(*args, **kwargs)
            await gather(
                *(self._run_with_semaphore(callback, *args, **kwargs) for callback in
                  self._subscribers[event_type].async_callback),
                return_exceptions=True)

    def clear(self):
        self._subscribers.clear()
        self._filters.clear()
        self._global_filters.clear()

    def add_global_filter(self, callback: FilterCallback, *, weight: int = 1) -> None:
        self._global_filters.add_callback(callback, weight)

    def remove_global_filter(self, callback: FilterCallback) -> None:
        self._global_filters.remove_callback(callback)

    def add_filter(self, event_type: Union[Event, str], callback: FilterCallback, *, weight: int = 1) -> None:
        if event_type not in self._filters:
            self._filters[event_type] = EventCallbackContainer()
        self._filters[event_type].add_callback(callback, weight)

    def remove_filter(self, event_type: Union[Event, str], callback: FilterCallback) -> None:
        if event_type in self._filters:
            self._filters[event_type].remove_callback(callback)
