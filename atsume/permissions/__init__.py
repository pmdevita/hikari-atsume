"""
Atsume can limit components to run only in the guilds (or DM channel) you specify.
You can load the default `SettingsPermissions` class, which lets you configure permissions
from your local.py or settings.py. You can also subclass `AbstractComponentPermissions`
and write your own permissions handler.

"""

import importlib
import typing

from .base import AbstractComponentPermissions
from .settings_permissions import SettingsPermissions

__all__ = [
    "SettingsPermissions",
    "AbstractComponentPermissions",
    "import_permission_class",
]


def import_permission_class(
    module_path: str,
) -> typing.Type[AbstractComponentPermissions]:
    """
    Import the permissions class from a given module path. Used to load the user's configured permissions class
    from their settings.

    :param module_path: The module path to import.
    :return: The class object of the given module path.
    """
    parts = module_path.split(".")
    module = importlib.import_module(".".join(parts[:-1]))
    permissions: typing.Type[AbstractComponentPermissions] = getattr(module, parts[-1])
    if issubclass(permissions, AbstractComponentPermissions):
        return permissions
    raise ValueError(
        f"Permissions class {module_path} does not implement {AbstractComponentPermissions.__name__}"
    )
