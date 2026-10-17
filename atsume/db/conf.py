import logging
from importlib import import_module

from piccolo.conf.apps import AppConfig, AppRegistry
from piccolo.engine import SQLiteEngine

from atsume.apps.manager import manager
from atsume.settings import settings

logger = logging.getLogger(__name__)

if settings.DATABASE_URL.startswith("sqlite://"):
    DB = SQLiteEngine(path=settings.DATABASE_URL.removeprefix("sqlite://"))
elif settings.DATABASE_URL.startswith("postgresql://"):
    from piccolo.engine.postgres import PostgresEngine

    DB = PostgresEngine(config={"dsn": settings.DATABASE_URL})
else:
    logging.warning("Unsupported database URL scheme.")
    DB = None


apps = []
for app in manager.component_configs:
    try:
        app_conf_module = import_module(app.module_path)
        app_config: AppConfig = getattr(app_conf_module, "APP_CONFIG")
    except (ImportError, AttributeError):
        if app.name.endswith(".piccolo_app"):
            continue
        try:
            app_conf_module = import_module(app.module_path + ".piccolo_app")
            app_config = getattr(app_conf_module, "APP_CONFIG")
        except (ImportError, AttributeError):
            continue
    apps.append(app.module_path)

APP_REGISTRY = AppRegistry(apps)
