import inspect
import typing
from importlib import import_module

from atsume.settings import settings
from .component_config import ComponentConfig


APPS_MODULE_NAME = "apps"


def get_component_config(module_path: str) -> ComponentConfig:
    app_module = import_module(f"{module_path}.{APPS_MODULE_NAME}")
    app_configs = [
        (name, candidate)
        for name, candidate in inspect.getmembers(app_module, inspect.isclass)
        if (issubclass(candidate, ComponentConfig) and candidate is not ComponentConfig)
    ]
    # You could declare multiple apps in a package but for right now we're not going to do that
    assert len(app_configs) == 1

    return app_configs[0][1](module_path)


class ComponentManager:
    def __init__(self) -> None:
        self.component_configs: list[ComponentConfig] = []

    def _load_components(self) -> None:
        for component in settings.COMPONENTS:
            self.component_configs.append(get_component_config(component))

    def get_config_from_models_path(
        self, models_path: str
    ) -> typing.Optional[ComponentConfig]:
        for config in manager.component_configs:
            if models_path == config.models_path:
                return config
        return None


manager = ComponentManager()
