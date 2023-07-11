import typing

import hikari

from atsume.permissions import AbstractComponentPermissions

ListenerCallbackType = typing.TypeVar(
    "ListenerCallbackType",
    bound=typing.Callable[[hikari.Event], typing.Coroutine[None, None, None]],
)


class AtsumeEventListener:
    def __init__(
        self,
        callback: ListenerCallbackType,
    ):
        callable_types = typing.get_type_hints(callback)
        if len(callable_types) > 1:
            raise Exception("Event listener created with more than one argument")
        key = list(callable_types.keys())[0]
        self.event_type = callable_types[key]
        if not issubclass(self.event_type, hikari.Event):
            raise Exception("Event listener argument does not specify an Event type")
        self.callback = callback
        self.permissions: typing.Optional[AbstractComponentPermissions] = None

    def __call__(
        self, event: hikari.Event
    ) -> typing.Coroutine[None, None, None] | None:
        if self.permissions:
            if hasattr(event, "guild_id"):
                if not self.permissions.allow_in_guild(event.guild_id):
                    return None
            # IDK if this is correct but if it has these it's still probably a DM event right?
            elif hasattr(event, "channel_id"):
                if not self.permissions.allow_in_dm():
                    return None

        return self.callback(event)


def with_listener(
    callback: typing.Callable[[hikari.Event], typing.Coroutine[None, None, None]]
) -> AtsumeEventListener:
    return AtsumeEventListener(callback)
