from asyncio import Semaphore, gather, run
from typing import Any, Optional, Type, Union, Callable, Awaitable

from src.base.logger import logger
from src.bus.event.event import Event
from src.bus.event_callback_container import EventCallbackContainer

SubScriberCallback: Type = Callable[..., Union[Any, Awaitable[Any]]]
FilterCallback: Type = Callable[..., Union[Optional[bool], Awaitable[Optional[bool]]]]


class EventBus:
    """
    EventBus 事件总线类，提供事件订阅、发布和切面逻辑。

    :param max_concurrent_tasks: 异步任务的最大任务书
    """

    def __init__(self, max_concurrent_tasks: int = 10):
        self._subscribers: dict[str, EventCallbackContainer] = {}
        self._filters: dict[str, EventCallbackContainer] = {}
        self._global_filters: EventCallbackContainer = EventCallbackContainer()
        self._semaphore = Semaphore(max_concurrent_tasks)

    def on(self, event: Union[Event, str], *, weight: int = 1) -> Callable:
        """
        订阅事件修饰器

        使用修饰器来向事件总线注册一个事件处理函数，这个事件处理函数可以是异步函数，也可以是同步函数。

        事件类型可以是字符串，表示自定义类型，也可以写一个继承Event类的枚举类来管理事件。

        关于权重：查看 :py:func:`EventBus.publish` 了解更多

        示例::

            @event_bus.on('message_create')
            def message_logger(message, *_, **__):
                print(message)
            # 异步函数也可以
            @event_bus.on('message_create')
            async def message_recoder(message, *_, **__):
                await ...

        :param event: 要订阅的事件
        :param weight: 事件的选择权重
        :return: 实际上的修饰器
        """

        def decorator(func: SubScriberCallback):
            self.subscribe(event, func, weight=weight)
            logger.debug(f"{func.__name__} has subscribed to {event}, weight={weight}")

        return decorator

    def subscribe(self, event: Union[Event, str], callback: SubScriberCallback, *, weight: int = 1) -> None:
        """
        订阅事件

        用于订阅事件修饰器内部的函数，也可以单独使用

        详细信息请查看 :py:func:`EventBus.on`

        示例::

            def message_logger(message, *_, **__):
                print(message)
            async def message_recoder(message, *_, **__):
                await ...
            event_bus.subscribe('message_create', message_logger)
            event_bus.subscribe('message_create', message_recoder)

        :param event: 要订阅的事件
        :param callback: 事件回调函数
        :param weight: 事件的选择权重
        """
        if event not in self._subscribers:
            self._subscribers[event] = EventCallbackContainer()
        self._subscribers[event].add_callback(callback, weight)

    def unsubscribe(self, event: Union[Event, str], callback: SubScriberCallback) -> None:
        """
        取消订阅事件

        示例::

            def message_logger(message, *_, **__):
                print(message)
            event_bus.unsubscribe('message_create', message_logger)

        :param event: 要订阅的事件
        :param callback: 事件回调函数
        """
        if event in self._subscribers:
            self._subscribers[event].remove_callback(callback)

    def publish_sync(self, event: Union[Event, str], *args, **kwargs) -> None:
        """
        以同步方式触发事件（底层还是异步执行）

        示例:
            publish_sync('message_create', "This is a message", user="Half")

        :param event: 要触发的事件
        """
        run(self.publish(event, *args, **kwargs))

    async def _run_with_semaphore(self, coroutine: Callable, *args, **kwargs):
        """
        带有限制器的异步函数执行器
        :param coroutine: 原异步函数
        """
        async with self._semaphore:
            return await coroutine(*args, **kwargs)

    async def publish(self, event: Union[Event, str], *args, **kwargs) -> None:
        """
        异步触发事件

        执行顺序:
            函数的权重越大，越先被执行，同步函数优先于异步函数执行。

            同步全局过滤器 -> 异步全局过滤器 -> 同步事件过滤器 -> 异步事件过滤器 -> 同步事件处理函数 -> 异步事件处理函数

            其中，最后的异步事件处理函数权重没有作用，因为会使用asyncio.gather并发执行，执行先后顺序也就失去了意义

        示例:
            await publish('message_create', "This is a message", user="Half")

        :param event: 要触发的事件
        """
        for callback in self._global_filters.sync_callback:
            if callback(event, *args, **kwargs):
                return

        for callback in self._global_filters.async_callback:
            if await callback(event, *args, **kwargs):
                return

        if event in self._filters:
            for callback in self._filters[event].sync_callback:
                if callback(*args, **kwargs):
                    return
            for callback in self._filters[event].async_callback:
                if await callback(*args, **kwargs):
                    return

        if event in self._subscribers:
            for callback in self._subscribers[event].sync_callback:
                callback(*args, **kwargs)
            await gather(
                *(self._run_with_semaphore(callback, *args, **kwargs) for callback in
                  self._subscribers[event].async_callback),
                return_exceptions=True)

    def clear(self):
        self._subscribers.clear()
        self._filters.clear()
        self._global_filters.clear()

    def on_global_event_filter(self, *, weight: int = 1) -> Optional[Callable]:
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
