import importlib
import typing
import types

from atsume.settings import default_settings as _DEFAULT
from . import types as SETTINGS_TYPES

T = typing.TypeVar("T", bound=SETTINGS_TYPES)


class Settings:
    _SETTINGS: types.ModuleType = None
    _LOCAL: types.ModuleType = None

    def _initialize(self, bot_module):
        self._SETTINGS = importlib.import_module(f"{bot_module}.bot.settings")
        self._LOCAL = importlib.import_module(f"{bot_module}.bot.local")

    def __getattribute__(self, item):
        try:
            result = super().__getattribute__(item)
            return result
        except AttributeError:
            pass
        if hasattr(self._LOCAL, item):
            return getattr(self._LOCAL, item)
        if hasattr(self._SETTINGS, item):
            return getattr(self._SETTINGS, item)
        return getattr(_DEFAULT, item)


settings = Settings()
