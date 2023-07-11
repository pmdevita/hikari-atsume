import typing

if typing.TYPE_CHECKING:
    from atsume.db import Model


class ComponentConfig:
    name: str = None
    verbose_name: str = None
    commands_module_name = "commands"
    models_module_name = "models"

    def __init__(self, module_path):
        assert self.name is not None
        if not hasattr(self, "verbose_name"):
            self.verbose_name = self.name
        self.module_path = module_path
        self._models: list["Model"] = []

    @property
    def commands_path(self):
        return f"{self.module_path}.{self.commands_module_name}"

    @property
    def models_path(self):
        return f"{self.module_path}.{self.models_module_name}"



