import inspect
import logging
import sys
import typing
from importlib import import_module

from atsume.settings import settings
from .component_config import ComponentConfig


APPS_MODULE_NAME = "apps"


class ComponentAlreadyLoaded(Exception):
    pass


class ComponentNotFound(Exception):
    pass


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
        self.unloaded_components: dict[str, str] = {}

    def _load_components(self) -> None:
        for component in settings.COMPONENTS:
            self._load_component(component)

    def _load_component(self, component: str) -> ComponentConfig:
        component_config = get_component_config(component)
        self.component_configs.append(component_config)
        return component_config

    def get_config_from_models_path(
        self, models_path: str
    ) -> typing.Optional[ComponentConfig]:
        for config in manager.component_configs:
            if models_path == config.models_path:
                return config
        return None

    def get_config_by_name(self, config_name: str) -> typing.Optional[ComponentConfig]:
        for config in manager.component_configs:
            if config.name == config_name:
                return config
        return None

    def unload_component(self, component_config: ComponentConfig) -> None:
        """Unloads a component from Python. Should be called after `tanjun.Client.remove_component_by_name"""
        self.unloaded_components[component_config.name] = component_config.module_path
        component_config._unload()
        keys = []
        for i in sys.modules.keys():
            if i.startswith(component_config.module_path):
                logging.info(f"Unloading module {i}")
                keys.append(i)
        for key in keys:
            del sys.modules[key]

        self.component_configs.remove(component_config)

    def load_component(
        self,
        component_name: typing.Optional[str] = None,
        component_path: typing.Optional[str] = None,
    ) -> ComponentConfig:
        if component_name:
            if self.get_config_by_name(component_name):
                raise ComponentAlreadyLoaded
            component_path = self.unloaded_components.pop(component_name)
        if not component_path:
            raise ComponentNotFound
        return self._load_component(component_path)


manager = ComponentManager()
