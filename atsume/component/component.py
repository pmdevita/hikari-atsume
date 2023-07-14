import typing

import hikari
import tanjun

from atsume.permissions import AbstractComponentPermissions, permission_check


class Component(tanjun.Component):
    permissions: typing.Optional[AbstractComponentPermissions]

    def set_permissions(self, permissions: AbstractComponentPermissions) -> None:
        self.permissions = permissions
        self.add_check(permission_check(permissions))

    @property
    def guilds(self) -> list[hikari.Snowflake]:
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
