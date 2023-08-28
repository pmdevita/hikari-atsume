import collections
import inspect
import typing
from datetime import datetime, timezone, timedelta
from typing import Callable, Any, Coroutine

import hikari
import tanjun
from tanjun.schedules import TimeSchedule, _CallbackSigT, IntervalSchedule

from atsume.permissions import AbstractComponentPermissions
from atsume.component.component import Component
from atsume.utils import copy_kwargs
from atsume.component.context import Context


class BaseCallback:
    """
    A class wrapper for a Tanjun command or event listener. It forwards the callback's signature
    so Tanjun can parse it, and adds the Component reference if the command has a argument with
    a matching type hint.
    """

    def __init__(
        self,
        callback: _CallbackSigT,
    ):
        self.callable_types = typing.get_type_hints(callback)
        self.callback = callback
        # Forward the type hints
        self.__signature__ = inspect.signature(self.callback)
        self._component: typing.Optional[
            Component
        ] = None  # The component is set during listener registration
        self._component_parameter_name: typing.Optional[str] = None
        self._should_insert_component()

    def _should_insert_component(self) -> None:
        """Check the callback signature to see if it wants the component"""
        for name, parameter in self.__signature__.parameters.items():
            if parameter.annotation == Component:
                if parameter.kind == inspect.Parameter.POSITIONAL_ONLY:
                    raise Exception("Not sure how to deal with this yet")
                elif self._component_parameter_name is not None:
                    raise Exception(
                        f"Callback {self.callback} has more than one component parameter"
                    )
                else:
                    self._component_parameter_name = name

    def __call__(
        self, *args: typing.Any, **kwargs: typing.Any
    ) -> Coroutine[Any, Any, None]:
        if self._component_parameter_name:
            kwargs[self._component_parameter_name] = self._component
        return self.callback(*args, **kwargs)


class PermissionsCallback(BaseCallback):
    """
    Does a permissions check before the callback is allowed through. This is done since Tanjun's
    Component checks aren't performed on event listeners.
    """

    def __init__(self, callback: _CallbackSigT):
        super().__init__(callback)
        self.permissions: typing.Optional[AbstractComponentPermissions] = None

    def has_permission(self, hikari_obj: typing.Union[hikari.Event, "Context"]) -> bool:
        if self.permissions:
            if hasattr(hikari_obj, "guild_id"):
                if hikari_obj.guild_id:
                    if not self.permissions.allow_in_guild(hikari_obj.guild_id):
                        return False
            # IDK if this is correct but if it has these it's still probably a DM event right?
            elif hasattr(hikari_obj, "channel_id"):
                if not self.permissions.allow_in_dm():
                    return False
        return True

    def __call__(
        self, *args: typing.Any, **kwargs: typing.Any
    ) -> Coroutine[Any, Any, None]:
        assert len(args) > 0
        first = args[0]
        assert isinstance(first, hikari.Event) or isinstance(first, Context)
        if not self.has_permission(first):
            return noop()
        return super().__call__(*args, **kwargs)


class AtsumeEventListener(PermissionsCallback):
    """
    A wrapper for an event listener callback that retrieves the desired event type
    from the function type hints.
    """

    def __init__(self, callback: _CallbackSigT):
        super().__init__(callback)
        key = list(self.callable_types.keys())[0]
        self.event_type = self.callable_types[key]
        if not issubclass(self.event_type, hikari.Event):
            raise Exception("Event listener argument does not specify an Event type")


class AtsumeComponentOpen(BaseCallback):
    pass


class AtsumeComponentClose(BaseCallback):
    pass


class AtsumeTimeSchedule(BaseCallback):
    """
    A callback wrapper for a scheduled function. The created :py:class:`tanjun.TimeSchedule` object
    calls the wrapper, which then calls the callback.
    """

    def __init__(self, callback: _CallbackSigT, schedule_kwargs: typing.Any) -> None:
        super().__init__(callback)
        self.schedule_kwargs = schedule_kwargs

    def as_time_schedule(self) -> TimeSchedule["AtsumeTimeSchedule"]:
        return TimeSchedule(self, **self.schedule_kwargs)


class AtsumeIntervalSchedule(BaseCallback):
    """
    A callback wrapper for a interval scheduled function. The created
    :py:class:`tanjun.IntervalSchedule` object calls the wrapper, which then calls the callback.
    """

    def __init__(
        self,
        callback: _CallbackSigT,
        interval: int | float | timedelta,
        schedule_kwargs: typing.Any,
    ) -> None:
        super().__init__(callback)
        self.interval = interval
        self.schedule_kwargs = schedule_kwargs

    def as_interval(
        self,
    ) -> IntervalSchedule[Callable[..., Coroutine[Any, Any, None]] | Any]:
        return IntervalSchedule(self, self.interval, **self.schedule_kwargs)


async def noop() -> None:
    pass


def with_listener(
    callback: typing.Callable[
        [hikari.events.base_events.Event], typing.Coroutine[None, None, None]
    ]
) -> AtsumeEventListener:
    """
    Decorator to register a function as an event listener. Callback must
    type hint the first position argument as the desired event type.
    """
    return AtsumeEventListener(callback)


def on_open(callback: _CallbackSigT) -> AtsumeComponentOpen:
    """Decorator to register a function to run when a component starts."""
    return AtsumeComponentOpen(callback)


def on_close(callback: _CallbackSigT) -> AtsumeComponentClose:
    """Decorator to register a function to run when a component stops."""
    return AtsumeComponentClose(callback)


@copy_kwargs(tanjun.as_time_schedule)
def as_time_schedule(
    *args: typing.Any, **kwargs: typing.Any
) -> typing.Callable[[_CallbackSigT], AtsumeTimeSchedule]:
    """Decorator to register a function to run on a given schedule."""

    def wrapper(callback: _CallbackSigT) -> AtsumeTimeSchedule:
        return AtsumeTimeSchedule(callback, schedule_kwargs=kwargs)

    return wrapper


@copy_kwargs(tanjun.as_interval)
def as_interval(
    interval: int | float | timedelta, *args: typing.Any, **kwargs: typing.Any
) -> typing.Callable[[_CallbackSigT], AtsumeIntervalSchedule]:
    def wrapper(callback: _CallbackSigT) -> AtsumeIntervalSchedule:
        return AtsumeIntervalSchedule(callback, interval, kwargs)

    return wrapper
