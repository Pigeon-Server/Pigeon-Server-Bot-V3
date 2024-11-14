from enum import Enum
from typing import Callable, List


class LifeCycleEvent(Enum):
    INITIAL = 0
    STARTING = 1
    STARTED = 2
    STOPPING = 3
    STOPPED = 4


class LifeCycleManager:
    _life_cycle_map: dict[LifeCycleEvent, List[Callable[[], None]]] = {}

    @staticmethod
    def add_life_cycle_event(event: LifeCycleEvent, func: Callable[[], None]) -> None:
        if event not in LifeCycleManager._life_cycle_map:
            LifeCycleManager._life_cycle_map[event] = [func]
        else:
            LifeCycleManager._life_cycle_map[event].append(func)

    @staticmethod
    def emit_life_cycle_event(event: LifeCycleEvent) -> None:
        if event in LifeCycleManager._life_cycle_map:
            for func in LifeCycleManager._life_cycle_map[event]:
                func()
