from __future__ import annotations

import dataclasses
from typing import Callable

from kivy.event import EventDispatcher


@dataclasses.dataclass
class Event:
    name: str
    data: dict = dataclasses.field(default_factory=dict)


class Dispatcher(EventDispatcher):
    _event_subscribers: dict[str, list[Callable]] = {}

    def __new__(cls, *args, **kwargs):
        raise NotImplementedError('Dispatcher class should not be instantiated!')

    @classmethod
    def publish_event(cls, event_name: str, **kwargs):
        for subscriber_callback in cls._event_subscribers.get(event_name):
            subscriber_callback(**kwargs)

    @classmethod
    def subscribe_to_event(cls, event_name: str, callback: Callable):
        cls._event_subscribers.setdefault(event_name, []).append(callback)
