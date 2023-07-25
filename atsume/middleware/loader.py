import importlib
import logging

import tanjun

from atsume.settings import settings

# Middleware that Atsume always needs to load
ATSUME_MIDDLEWARE = ["atsume.db.manager.hook_database"]


def attach_middleware(client: tanjun.Client) -> None:
    """
    Load the middleware modules from the Atsume project settings and hook them
    on to the given `tanjun.Client`.
    """
    middleware = set()
    middleware.update(settings.MIDDLEWARE)
    middleware.update(ATSUME_MIDDLEWARE)
    for module_path in middleware:
        path = module_path.split(".")
        try:
            module = importlib.import_module(".".join(path[:-1]))
            func = getattr(module, path[-1])
        except (ModuleNotFoundError, AttributeError):
            # Todo: Should this be an error?
            logging.error(f"Unable to load middleware {module_path}")
            continue
        func(client)
