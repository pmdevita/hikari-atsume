import collections
import inspect
import typing
from datetime import datetime, timezone

import hikari
import tanjun
from tanjun.schedules import TimeSchedule, _CallbackSigT, _CallbackSig

from atsume.permissions import AbstractComponentPermissions
from atsume.component.component import Component
from atsume.utils import copy_kwargs

if typing.TYPE_CHECKING:
    from atsume.component.context import Context


class BaseCallback:
    def __init__(
        self,
        callback: _CallbackSigT,
    ):
        self.callable_types = typing.get_type_hints(callback)
        self.callback = callback
        # Forward the type hints
        self.__signature__ = inspect.signature(self.callback)
        self._component: typing.Optional[Component] = None
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
    ) -> typing.Coroutine[None, None, None]:
        if self._component_parameter_name:
            kwargs[self._component_parameter_name] = self._component
        return self.callback(*args, **kwargs)


class PermissionsCallback(BaseCallback):
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
        self,
        hikari_obj: typing.Union[hikari.Event, "Context"],
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> typing.Coroutine[None, None, None]:
        if not self.has_permission(hikari_obj):
            return noop()
        return super().__call__(hikari_obj, *args, **kwargs)


class AtsumeEventListener(PermissionsCallback):
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
    def __init__(self, callback: _CallbackSigT, schedule_kwargs: typing.Any) -> None:
        super().__init__(callback)
        self.schedule_kwargs = schedule_kwargs

    def as_time_schedule(self) -> TimeSchedule["AtsumeTimeSchedule"]:
        return TimeSchedule(self, **self.schedule_kwargs)


async def noop() -> None:
    pass


def with_listener(
    callback: typing.Callable[[hikari.Event], typing.Coroutine[None, None, None]]
) -> AtsumeEventListener:
    return AtsumeEventListener(callback)


def on_open(callback: _CallbackSigT) -> AtsumeComponentOpen:
    return AtsumeComponentOpen(callback)


def on_close(callback: _CallbackSigT) -> AtsumeComponentClose:
    return AtsumeComponentClose(callback)


@copy_kwargs(tanjun.as_time_schedule)
def as_time_schedule(
    *args: typing.Any, **kwargs: typing.Any
) -> typing.Callable[[_CallbackSigT], AtsumeTimeSchedule]:
    def wrapper(callback: _CallbackSigT) -> AtsumeTimeSchedule:
        return AtsumeTimeSchedule(callback, schedule_kwargs=kwargs)

    return wrapper
