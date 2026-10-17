from piccolo.conf.apps import AppConfig, table_finder

from .apps import HandlesGUI

APP_CONFIG = AppConfig(
    HandlesGUI.name,
    HandlesGUI.migrations_folder_path(),
    table_classes=table_finder(
        modules=["." + HandlesGUI.models_module_name],
        package=HandlesGUI.__module__.removesuffix(".apps"),
    ),
)
