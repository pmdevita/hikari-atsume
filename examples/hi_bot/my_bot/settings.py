import hikari

from atsume.settings.type_hints import *  # noqa: F403

COMPONENTS = ["basic", "atsume.contrib.handles_gui"]

COMPONENT_PERMISSIONS_CLASS = "atsume.permissions.SettingsPermissions"

COMPONENT_ALL_GUILDS_PERMISSIONS = ["basic"]

EXTENSIONS = []

HIKARI_LOGGING = False

INTENTS = hikari.Intents.ALL_UNPRIVILEGED | hikari.Intents.MESSAGE_CONTENT
