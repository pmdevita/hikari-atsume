import importlib
import logging
import typing

import tanjun

from atsume.settings import settings

# Middleware that Atsume always needs to load
ATSUME_MIDDLEWARE = ["atsume.db.manager.hook_database"]


class MiddlewareCallable:
    def __call__(self, client: tanjun.Client):
        ...


def attach_middleware(client: tanjun.Client) -> None:
    """
    Load the middleware modules from the Atsume project settings and hook them
    on to the given `tanjun.Client`.
    """
    middleware = set()
    middleware.update(settings.MIDDLEWARE)
    middleware.update(ATSUME_MIDDLEWARE)
    for module_path in middleware:
        func = load_module_setting(module_path, MiddlewareCallable)
        func(client)


class ModulePathNotFound(Exception):
    def __init__(self, module_path: str):
        super().__init__(f'Unable to load module at path "{module_path}".')


T = typing.TypeVar("T")


def load_module_setting(module_path: str, return_type: typing.Type[T]) -> T:
    path = module_path.split(".")
    try:
        module = importlib.import_module(".".join(path[:-1]))
        func = getattr(module, path[-1])
    except (ModuleNotFoundError, AttributeError):
        raise ModulePathNotFound(module_path)
    return typing.cast(T, func)
