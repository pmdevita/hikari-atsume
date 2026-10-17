from piccolo.conf.apps import AppConfig, table_finder

from .apps import Schedule
from .task import task

__all__ = ["task"]

APP_CONFIG = AppConfig(
    Schedule.name,
    Schedule.migrations_folder_path(),
    table_classes=table_finder(
        modules=["." + Schedule.models_module_name],
        package=Schedule.__module__.removesuffix(".apps"),
    ),
)
