"""

This is a list of the default Atsume settings and their expected types. You can set these
in your `settings.py` and `local.py` file.

Example
-------

.. code-block:: python

  # local.py

  TOKEN = "TEyNzAzMY5MjYzxODE1MMTA5..."

.. code-block:: python

  # settings.py

  INTENTS = hikari.

  EXTENSIONS = [
      "atsume.extensions.aiohttp"
  ]

"""


import typing

from hikari import Intents

TOKEN: str
"""Your Discord bot token."""

DEBUG: bool
"""Whether to run the bot in Debug or Production mode. (default: False)"""

GLOBAL_COMMANDS: bool
"""
Whether to register commands globally or per-guild. (default: False)"""

VOICE_COMPONENT: typing.Optional[str]
"""
The VoiceComponentImpl implementation to use. Must be a subclass of :py:class:`hikari.impl.voice.VoiceComponentImpl`.
"""

COMPONENTS: list[str]
"""A list of module paths to Component that will be loaded."""

COMPONENT_PERMISSIONS_CLASS: typing.Optional[str]
"""
An optional module path to a Permissions class 
(must implement :py:class:`atsume.permissions.AbstractComponentPermissions`).
"""

COMPONENT_ALL_GUILDS_PERMISSIONS: list[str]
"""
For use with :py:class:`atsume.permissions.SettingsPermissions`, 
a list of component module paths for those that have access to all guilds.
"""

COMPONENT_DM_PERMISSIONS: list[str]
"""
For use with :py:class:`atsume.permissions.SettingsPermissions`, 
a list of component module paths for those that have access to DMs.
"""

COMPONENT_GUILD_PERMISSIONS: dict[int, list[str]]
"""
For use with :py:class:`atsume.permissions.SettingsPermissions`, a dictionary mapping Discord Guild IDs 
to a list of allowed component module paths.
"""

HIKARI_LOGGING: bool
"""Enable more verbose logging. (default: False)"""

INTENTS: Intents
"""The intents to use for Hikari."""

MESSAGE_PREFIX: typing.Optional[str]
"""The message prefix for message commands."""

DATABASE_URL: str
"""A database URL for Ormar to use to connect to the database."""

EXTENSIONS: list[str]
"""A list of extension module paths to load."""

DISABLE_UVLOOP: bool
"""Prevent running with uvloop even if installed. (default: False)"""
