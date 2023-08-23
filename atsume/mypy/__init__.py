"""

Plugins for mypy to help with type checking atsume. At the moment, there is only one, the :py:class:`SettingsPlugin`, used to
help check types for variables accessed through the Atsume's global settings.

"""
import typing

from .settings import SettingsPlugin
from .main import AtsumePlugin

__all__ = ["AtsumePlugin", "SettingsPlugin"]


def plugin(version: str) -> typing.Type[AtsumePlugin]:
    return AtsumePlugin
