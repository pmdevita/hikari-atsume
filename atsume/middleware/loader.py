import importlib
import logging

import tanjun

from atsume.settings import settings

# Middleware that Atsume always needs to load
ATSUME_MIDDLEWARE = [
    "atsume.db.manager.hook_database"
]


def attach_middleware(client: tanjun.Client):
    middleware = set()
    middleware.update(settings.MIDDLEWARE)
    middleware.update(ATSUME_MIDDLEWARE)
    for module_path in middleware:
        path = module_path.split(".")
        try:
            module = importlib.import_module(".".join(path[:-1]))
            func = getattr(module, path[-1])
        except (ModuleNotFoundError, AttributeError):
            logging.error(f"Unable to load middleware {module_path}")
            continue
        func(client)



