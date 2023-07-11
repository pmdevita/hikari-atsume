import importlib
import typing

import tanjun

from .settings_permissions import SettingsPermissions
from .base import AbstractComponentPermissions


def import_permission_class(module_path):
    parts = module_path.split(".")
    module = importlib.import_module(".".join(parts[:-1]))
    return getattr(module, parts[-1])


def permission_check(permissions: AbstractComponentPermissions):
    async def check(ctx: tanjun.abc.Context):
        if ctx.guild_id:
            return permissions.allow_in_guild(ctx.guild_id)
        else:
            return permissions.allow_in_dm()
    return check
