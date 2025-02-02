from typing import Any, Awaitable, Callable, Optional, Type, Union

from src.base.logger import logger
from src.bus.event.event import Event
from src.bus.event_callback_container import EventCallbackContainer
from src.bus.module.base_module import BaseModule

FilterCallback: Type = Callable[..., Union[Optional[bool], Awaitable[Optional[bool]]]]


class BusFilter(BaseModule):
    """
    事件总线过滤器模块, 负责对事件进行过滤, 同时判断是否继续传播该事件
    """

    def __init__(self):
        self._filters: dict[str, EventCallbackContainer] = {}
        self._global_filters: EventCallbackContainer = EventCallbackContainer()

    def clear(self):
        self._filters.clear()
        self._global_filters.clear()

    async def resolve(self, event: Union[Event, str], args, kwargs) -> bool:
        if await self._apply_global_filter(event, args, kwargs):
            return True
        if await self._apply_filter(event, args, kwargs):
            return True
        return False

    async def _apply_filter(self, event: Union[Event, str], args, kwargs) -> bool:
        if event in self._filters:
            for callback in self._filters[event].sync_callback:
                if callback(*args, **kwargs):
                    return True
            for callback in self._filters[event].async_callback:
                if await callback(*args, **kwargs):
                    return True

    async def _apply_global_filter(self, event: Union[Event, str], args, kwargs) -> bool:
        for callback in self._global_filters.sync_callback:
            if callback(event, *args, **kwargs):
                return True
        for callback in self._global_filters.async_callback:
            if await callback(event, *args, **kwargs):
                return True

    def on_global_event_filter(self, *, weight: int = 1) -> Callable:
        """
        全局过滤器修饰器

        使用修饰器来向事件总线注册一个全局事件过滤器函数，这个过滤器函数可以是异步函数，也可以是同步函数。

        过滤器返回值：如果返回True，则代表此事件被截断，不再向下传播。如果返回False或者None，则此事件继续传播

        示例::

            @event_bus.on_global_event_filter()
            def message_logger(message, *_, **__):
                print(message)
            # 异步函数也可以
            @event_bus.on_global_event_filter()
            async def message_recoder(message, *_, **__):
                await ...

        :param weight: 事件的选择权重
        :return: 实际上的修饰器
        """

        def decorator(func: FilterCallback):
            self.add_global_filter(func, weight=weight)
            logger.debug(f"Global filter {func.__name__} has been added, weight={weight}")

        return decorator

    def add_global_filter(self, callback: FilterCallback, *, weight: int = 1) -> None:
        """
        注册全局过滤器

        用于注册全局过滤器的函数，也可以单独使用

        详细信息请查看 :py:func:`EventBus.on_global_event_filter`

        示例::

            def message_logger(message, *_, **__):
                print(message)
            async def message_recoder(message, *_, **__):
                await ...
            event_bus.on_global_event_filter(message_logger)
            event_bus.on_global_event_filter(message_recoder)

        :param callback: 事件回调函数
        :param weight: 事件的选择权重
        """
        self._global_filters.add_callback(callback, weight)

    def remove_global_filter(self, callback: FilterCallback) -> None:
        """
        移除全局过滤器

        示例::

            def message_logger(message, *_, **__):
                print(message)
            event_bus.remove_global_filter(message_logger)

        :param callback: 事件回调函数
        """
        self._global_filters.remove_callback(callback)

    def on_event_filter(self, event: Union[Event, str], *, weight: int = 1) -> Optional[Callable]:
        """
        事件过滤器修饰器

        使用修饰器来向事件总线注册一个事件过滤器函数，这个过滤器函数可以是异步函数，也可以是同步函数。

        事件类型可以是字符串，表示自定义类型，也可以写一个继承Event类的枚举类来管理事件。

        过滤器返回值：查看 :py:func:`EventBus.on_global_event_filter` 了解更多

        关于权重：查看 :py:func:`EventBus.publish` 了解更多

        示例::

            @event_bus.on_event_filter('message_create')
            def message_logger(message, *_, **__):
                print(message)
            # 异步函数也可以
            @event_bus.on_event_filter('message_create')
            async def message_recoder(message, *_, **__):
                await ...

        :param event: 要订阅的事件
        :param weight: 事件的选择权重
        :return: 实际上的修饰器
        """

        def decorator(func: FilterCallback):
            self.add_filter(event, func, weight=weight)
            logger.debug(f"Event filter {func.__name__} has been added to event {event}, weight={weight}")

        return decorator

    def add_filter(self, event: Union[Event, str], callback: FilterCallback, *, weight: int = 1) -> None:
        """
        注册事件过滤器

        用于注册事件过滤器的函数，也可以单独使用

        详细信息请查看 :py:func:`EventBus.on_event_filter`

        示例::

            def message_logger(message, *_, **__):
                print(message)
            async def message_recoder(message, *_, **__):
                await ...
            event_bus.add_filter('message_create', message_logger)
            event_bus.add_filter('message_create', message_recoder)

        :param event: 要订阅的事件
        :param callback: 事件回调函数
        :param weight: 事件的选择权重
        """
        if event not in self._filters:
            self._filters[event] = EventCallbackContainer()
        self._filters[event].add_callback(callback, weight)

    def remove_filter(self, event: Union[Event, str], callback: FilterCallback) -> None:
        """
        移除事件过滤器

        示例::

            def message_logger(message, *_, **__):
                print(message)
            event_bus.remove_filter('message_create', message_logger)

        :param event: 要订阅的事件
        :param callback: 事件回调函数
        """
        if event in self._filters:
            self._filters[event].remove_callback(callback)
