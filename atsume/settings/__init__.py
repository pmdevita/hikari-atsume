"""

Provide access to the Atsume project's settings and supply type hinting for the settings
variables used by the Atsume framework.

"""


import importlib
import typing
import types

from atsume.settings import default_settings as _DEFAULT
from atsume.settings import type_hints


class Settings:
    _SETTINGS: typing.Optional[types.ModuleType] = None
    _LOCAL: typing.Optional[types.ModuleType] = None

    def _initialize(self, bot_module: str) -> None:
        self._SETTINGS = importlib.import_module(f"{bot_module}.settings")
        self._LOCAL = importlib.import_module(f"{bot_module}.local")

    def __getattribute__(self, item: str) -> typing.Any:
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
"""
A singleton to access the Atsume project's settings. Each variable defined in your `settings.py` and
`local.py` can be accessed as an attribute on this object.
"""
