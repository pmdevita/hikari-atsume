import typing

import hikari
import tanjun

from atsume.permissions import AbstractComponentPermissions, permission_check


class Component(tanjun.Component):
    """
    Organizes related commands and functionality into a single object. Extends the Tanjun Component
    with some features for per-guild permissions.
    """

    permissions: typing.Optional[AbstractComponentPermissions]

    def set_permissions(self, permissions: AbstractComponentPermissions) -> None:
        """
        Sets the permissions object to be used by this component and adds the check for it.
        """
        self.permissions = permissions
        self.add_check(permission_check(permissions))

    @property
    def guilds(self) -> list[hikari.snowflakes.Snowflake]:
        """
        A shortcut to `Client.cache.get_guilds_view()`. It's recommended to use this instead of
        directly using the cache to filter to only the guilds this component is permitted to
        run in.
        """
        if not self.client:
            return []
        if not self.client.cache:
            return []
        # Todo: Make this an iterator so it can be computed lazily
        if self.permissions:
            return [
                g
                for g in self.client.cache.get_guilds_view()
                if self.permissions.allow_in_guild(g)
            ]
        else:
            return [g for g in self.client.cache.get_guilds_view()]

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.name=}, {self.checks=}, {self.hooks=}, {self.slash_hooks=}, {self.message_hooks=})"
