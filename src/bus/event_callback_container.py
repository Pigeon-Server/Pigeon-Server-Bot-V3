from typing import Callable, Union

from src.bus.event_callback_factory import EventCallbackFactory
from src.bus.handler.async_event_callback import AsyncEventCallback
from src.bus.handler.event_callback import EventCallback
from src.bus.handler.sync_event_callback import SyncEventCallback


class EventCallbackContainer:
    """
    存储回调函数的容器类
    """
    def __init__(self):
        self._sync_callback: list[SyncEventCallback] = []
        self._async_callback: list[AsyncEventCallback] = []

    def add_sync_callback(self, callback: SyncEventCallback) -> None:
        self._sync_callback.append(callback)
        self._sync_callback.sort(key=lambda item: item.weight, reverse=True)

    def add_async_callback(self, callback: AsyncEventCallback) -> None:
        self._async_callback.append(callback)
        self._async_callback.sort(key=lambda item: item.weight, reverse=True)

    def add_callback(self, callback: Union[EventCallback, Callable], weight: int = 1) -> None:
        if not isinstance(callback, EventCallback):
            callback = EventCallbackFactory.create(callback, weight)
        if isinstance(callback, AsyncEventCallback):
            self.add_async_callback(callback)
        elif isinstance(callback, SyncEventCallback):
            self.add_sync_callback(callback)
        else:
            raise TypeError(f'Callback type {type(callback)} not supported')

    def remove_sync_callback(self, callback: Union[SyncEventCallback, Callable]) -> None:
        if callback in self._sync_callback:
            self._sync_callback.remove(callback)

    def remove_async_callback(self, callback: Union[AsyncEventCallback, Callable]) -> None:
        if callback in self._async_callback:
            self._async_callback.remove(callback)

    def remove_callback(self, callback: Union[EventCallback, Callable]) -> None:
        if isinstance(callback, AsyncEventCallback):
            self.remove_async_callback(callback)
        elif isinstance(callback, SyncEventCallback):
            self.remove_sync_callback(callback)
        else:
            raise TypeError(f'Callback type {type(callback)} not supported')

    def clear(self) -> None:
        self._sync_callback.clear()
        self._async_callback.clear()

    @property
    def sync_callback(self) -> list[SyncEventCallback]:
        return self._sync_callback

    @property
    def async_callback(self) -> list[AsyncEventCallback]:
        return self._async_callback
