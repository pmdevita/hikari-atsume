from piccolo.conf.apps import AppConfig, table_finder

from .apps import Basic

APP_CONFIG = AppConfig(
    Basic.name,
    Basic.migrations_folder_path(),
    table_classes=table_finder(
        modules=["." + Basic.models_module_name],
        package=Basic.__module__.removesuffix(".apps"),
    ),
)
