import inspect
import typing

import hikari

from atsume.permissions import AbstractComponentPermissions

if typing.TYPE_CHECKING:
    from atsume.component.context import Context

CallbackType = typing.TypeVar(
    "CallbackType", bound=typing.Callable[..., typing.Coroutine[None, None, None]]
)

ListenerCallbackType = typing.TypeVar(
    "ListenerCallbackType",
    bound=typing.Callable[[hikari.Event], typing.Coroutine[None, None, None]],
)


class BaseCallback:
    def __init__(
        self,
        callback: CallbackType,
    ):
        self.callable_types = typing.get_type_hints(callback)
        self.callback = callback
        # Forward the type hints
        self.__signature__ = inspect.signature(self.callback)

    def __call__(
        self, *args: typing.Any, **kwargs: typing.Any
    ) -> typing.Coroutine[None, None, None]:
        return self.callback(*args, **kwargs)


class PermissionsCallback(BaseCallback):
    def __init__(self, callback: ListenerCallbackType):
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
        **kwargs: typing.Any
    ) -> typing.Coroutine[None, None, None]:
        if not self.has_permission(hikari_obj):
            return noop()
        return super().__call__(hikari_obj, *args, **kwargs)


class AtsumeEventListener(PermissionsCallback):
    def __init__(self, callback: CallbackType):
        super().__init__(callback)
        key = list(self.callable_types.keys())[0]
        self.event_type = self.callable_types[key]
        if not issubclass(self.event_type, hikari.Event):
            raise Exception("Event listener argument does not specify an Event type")


class AtsumeComponentOpen(BaseCallback):
    pass


class AtsumeComponentClose(BaseCallback):
    pass


async def noop() -> None:
    pass


def with_listener(
    callback: typing.Callable[[hikari.Event], typing.Coroutine[None, None, None]]
) -> AtsumeEventListener:
    return AtsumeEventListener(callback)


def on_open(callback: CallbackType) -> AtsumeComponentOpen:
    return AtsumeComponentOpen(callback)


def on_close(callback: CallbackType) -> AtsumeComponentClose:
    return AtsumeComponentClose(callback)
