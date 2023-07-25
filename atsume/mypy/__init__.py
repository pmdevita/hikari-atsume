"""

Plugins for mypy to help with type checking atsume. At the moment, there is only one, the :py:class:`SettingsPlugin`, used to
help check types for variables accessed through the Atsume's global settings.

"""

from .settings import SettingsPlugin

__all__ = ["SettingsPlugin"]

