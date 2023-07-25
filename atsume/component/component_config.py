import typing
from pathlib import Path

import sqlalchemy

from atsume.permissions import import_permission_class
from atsume.settings import settings
from atsume.utils import module_to_path

if typing.TYPE_CHECKING:
    from ormar.models.metaclass import ModelMetaclass
    from atsume.permissions.base import AbstractComponentPermissions


class ComponentConfig:
    """
    A dataclass for configuring an Atsume Component. Includes the component name, its permissions,
    and the file and module paths for its commands and models.
    """
    name: str
    verbose_name: str
    commands_module_name = "commands"
    models_module_name = "models"
    permissions: typing.Optional["AbstractComponentPermissions"]

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

    @property
    def commands_path(self) -> str:
        return f"{self.module_path}.{self.commands_module_name}"

    @property
    def models_path(self) -> str:
        return f"{self.module_path}.{self.models_module_name}"

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
        return f'ComponentConfig(name"{self.name}")'
