from piccolo.conf.apps import AppConfig, table_finder

from .apps import component_upper_name

APP_CONFIG = AppConfig(
    component_upper_name.name,
    component_upper_name.migrations_folder_path(),
    table_classes=table_finder(
        modules=["." + component_upper_name.models_module_name],
        package=component_upper_name.__module__.removesuffix(".apps"),
    ),
)
