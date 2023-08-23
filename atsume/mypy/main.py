import configparser
import typing
import sys

import mypy.types
from mypy.options import Options
from mypy.plugin import Plugin, AttributeContext
import mypy.nodes
from mypy.modulefinder import mypy_path
from pathlib import Path
from .settings import SettingsPlugin

# Adapted from https://github.com/typeddjango/django-stubs/blob/master/mypy_django_plugin/main.py
# and https://github.com/typeddjango/django-stubs/blob/master/mypy_django_plugin/config.py

INI_SECTION = "mypy.plugins.atsume"
TOML_SECTION = "tool.atsume"
SETTINGS_KEY = "atsume_settings_module"


class AtsumePlugin(Plugin):
    def __init__(self, options: Options) -> None:
        super().__init__(options)
        assert options.config_file is not None
        self.plugin_config = AtsumePluginConfig(options.config_file)
        # Add paths from MYPYPATH env var
        sys.path.extend(mypy_path())
        # Add paths from mypy_path config option
        sys.path.extend(options.mypy_path)
        assert self.plugin_config.atsume_settings_module is not None

        # This isn't a very extensible or flexible way of doing this
        # But it's fine as long as there's only really one plugin
        self.settings_plugin = SettingsPlugin(
            options, atsume_settings_module=self.plugin_config.atsume_settings_module
        )

    def get_attribute_hook(
        self, fullname: str
    ) -> typing.Callable[[AttributeContext], mypy.types.Type] | None:
        return self.settings_plugin.get_attribute_hook(fullname)

    def get_additional_deps(
        self, file: mypy.nodes.MypyFile
    ) -> list[tuple[int, str, int]]:
        # If we're loading Atsume settings, load the project's settings files with it
        if file.fullname == "atsume.settings":
            return [
                (10, f"{self.plugin_config.atsume_settings_module}.settings", -1),
                (10, f"{self.plugin_config.atsume_settings_module}.local", -1),
            ]
        return []


class AtsumePluginConfig:
    def __init__(self, config_file: str) -> None:
        self.atsume_settings_module: typing.Optional[str] = None
        filepath = Path(config_file)
        if not filepath.is_file():
            raise FileNotFoundError
        if filepath.suffix.lower() == ".toml":
            self.parse_toml_file(filepath)
        else:
            self.parse_ini_file(filepath)

    def parse_toml_file(self, filepath: Path) -> None:
        if sys.version_info[:2] >= (3, 11):
            import tomllib
        else:
            import tomli as tomllib
        with filepath.open(mode="rb") as f:
            data = tomllib.load(f)
        try:
            config: typing.Dict[str, typing.Any] = data["tool"]["django-stubs"]
        except KeyError:
            raise Exception(f"{filepath} has no section [{TOML_SECTION}]")
        if SETTINGS_KEY not in config:
            raise Exception(
                f'Section [{TOML_SECTION}] in {filepath} has no option "{SETTINGS_KEY}"'
            )
        self.atsume_settings_module = config[SETTINGS_KEY]
        if not isinstance(self.atsume_settings_module, str):
            raise Exception(f'Invalid "{SETTINGS_KEY}": the setting must be a string')

    def parse_ini_file(self, filepath: Path) -> None:
        parser = configparser.ConfigParser()
        with filepath.open(encoding="utf-8") as f:
            parser.read_file(f, source=str(filepath))
        if not parser.has_section(INI_SECTION):
            raise Exception(f"{filepath} has no section [{INI_SECTION}]")
        if not parser.has_option(INI_SECTION, SETTINGS_KEY):
            raise Exception(
                f'Section [{INI_SECTION}] in {filepath} has no option "{SETTINGS_KEY}"'
            )
        self.atsume_settings_module = parser.get(INI_SECTION, SETTINGS_KEY).strip("'\"")


def plugin(version: str) -> typing.Type[AtsumePlugin]:
    return AtsumePlugin
