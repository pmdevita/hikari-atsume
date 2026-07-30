import dataclasses
import inspect
import typing
from pathlib import Path
from typing import Optional

import sqlalchemy

from atsume.command.model import Command
from atsume.permissions import import_permission_class
from atsume.settings import settings
from atsume.utils import module_to_path

if typing.TYPE_CHECKING:
    from ormar.models.metaclass import ModelMetaclass

    from atsume.permissions.base import AbstractComponentPermissions


class AppConfig:
    """
    A dataclass for configuring an Atsume Component. Includes the component name, its permissions,
    and the file and module paths for its commands and models.
    """

    name: str
    verbose_name: str
    commands_module_name = "commands"
    models_module_name = "models"
    migrations_module_name = "migrations"
    permissions: typing.Optional["AbstractComponentPermissions"]
    handles: list["BaseChannelHandle"] = []

    def __init__(self, module_path: str) -> None:
        assert self.name is not None
        if not hasattr(self, "verbose_name"):
            self.verbose_name = self.name
        self.module_path = module_path
        self._models: list["ModelMetaclass"] = []
        self._model_metadata = sqlalchemy.MetaData()
        self.permissions = None
        if settings.COMPONENT_PERMISSIONS_CLASS:
            permission_class = import_permission_class(
                settings.COMPONENT_PERMISSIONS_CLASS
            )
            self.permissions = permission_class(self.module_path)
        self.commands: typing.List[Command] = []

    @property
    def commands_path(self) -> str:
        return f"{self.module_path}.{self.commands_module_name}"

    @property
    def models_path(self) -> str:
        return f"{self.module_path}.{self.models_module_name}"

    @classmethod
    def migrations_folder_path(cls) -> Path:
        return Path(inspect.getfile(cls)).parent / cls.migrations_module_name

    @property
    def models(self) -> list["ModelMetaclass"]:
        return self._models

    @property
    def db_migration_path(self) -> Path:
        return Path(module_to_path(self.__class__.__module__)).parent / "migrations"

    def _unload(self) -> None:
        while self._models:
            self._models.pop()

    def __str__(self) -> str:
        return f'AppConfig(name"{self.name}")'

    def __repr__(self) -> str:
        return f"AppConfig({self.name=})"


@dataclasses.dataclass
class BaseChannelHandle:
    name: str
    """The name of the channel handle."""

    description: Optional[str] = None
    """The description of what this handle is used for."""


@dataclasses.dataclass
class ListeningHandle(BaseChannelHandle):
    """A channel handle which maps to multiple channels, used for receiving events."""


@dataclasses.dataclass
class InteractionHandle:
    """A channel handle which maps to a single channel, used for bot initiated actions or receiving events."""

    default_bot_channel: bool = False
    """Whether this channel uses a server's bot channel if unconfigured. Defaults to False."""
