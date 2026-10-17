from piccolo.conf.apps import AppConfig, table_finder

from .apps import Handles

APP_CONFIG = AppConfig(
    Handles.name,
    Handles.migrations_folder_path(),
    table_classes=table_finder(
        modules=["." + Handles.models_module_name],
        package=Handles.__module__.removesuffix(".apps"),
    ),
)
