"""
# Atsume Permissions

Atsume can limit components to run only in the guilds (or DM channel) you specify.
You can load the default `SettingsPermissions` class, which lets you configure permissions
from your local.py or settings.py. You can also subclass `AbstractComponentPermissions`
and write your own permissions handler.

"""


import importlib
import typing

import tanjun

from .settings_permissions import SettingsPermissions
from .base import AbstractComponentPermissions

__all__ = ["SettingsPermissions", "AbstractComponentPermissions"]


def import_permission_class(
    module_path: str,
) -> typing.Type[AbstractComponentPermissions]:
    parts = module_path.split(".")
    module = importlib.import_module(".".join(parts[:-1]))
    permissions: typing.Type[AbstractComponentPermissions] = getattr(module, parts[-1])
    if issubclass(permissions, AbstractComponentPermissions):
        return permissions
    raise ValueError(
        f"Permissions class {module_path} does not implement {AbstractComponentPermissions.__name__}"
    )


def permission_check(
    permissions: AbstractComponentPermissions,
) -> typing.Any:
    async def check(
        ctx: tanjun.abc.Context, *args: typing.Any, **kwargs: typing.Any
    ) -> bool:
        if ctx.guild_id:
            return permissions.allow_in_guild(ctx.guild_id)
        else:
            return permissions.allow_in_dm()

    return check
