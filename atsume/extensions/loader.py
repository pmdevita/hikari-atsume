import importlib
import logging
import typing

import tanjun

from atsume.settings import settings

# Extensions that Atsume always needs to load
ATSUME_EXTENSIONS = ["atsume.db.manager.hook_database"]


class ExtensionCallable:
    def __call__(self, client: tanjun.Client) -> None:
        ...


def attach_extensions(client: tanjun.Client) -> None:
    """
    Load the extension modules from the Atsume project settings and hook them
    on to the given `tanjun.Client`.
    """
    extensions = set()
    extensions.update(settings.EXTENSIONS)
    extensions.update(ATSUME_EXTENSIONS)
    for module_path in extensions:
        func = load_module_func(module_path, ExtensionCallable)
        func(client)


class ModulePathNotFound(Exception):
    def __init__(self, module_path: str):
        super().__init__(f'Unable to load module at path "{module_path}".')


T = typing.TypeVar("T")


def load_module_func(module_path: str, return_type: typing.Type[T]) -> T:
    path = module_path.split(".")
    try:
        module = importlib.import_module(".".join(path[:-1]))
        func = getattr(module, path[-1])
    except (ModuleNotFoundError, AttributeError):
        raise ModulePathNotFound(module_path)
    return typing.cast(T, func)


def load_module_class(module_path: str, return_type: T) -> T:
    path = module_path.split(".")
    try:
        module = importlib.import_module(".".join(path[:-1]))
        func = getattr(module, path[-1])
    except (ModuleNotFoundError, AttributeError):
        raise ModulePathNotFound(module_path)
    return typing.cast(T, func)
