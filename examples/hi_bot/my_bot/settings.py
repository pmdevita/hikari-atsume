import hikari

from atsume.settings import env
from atsume.settings.type_hints import *  # noqa: F403

COMPONENTS = ["basic", "atsume.contrib.handles_gui", "atsume.contrib.handles"]

# COMPONENT_PERMISSIONS_CLASS = "atsume.permissions.SettingsPermissions"
COMPONENT_PERMISSIONS_CLASS = "atsume.contrib.handles.permissions.DatabasePermissions"

COMPONENT_ALL_GUILDS_PERMISSIONS = ["basic"]

EXTENSIONS = []

HIKARI_LOGGING = False

INTENTS = hikari.Intents.ALL_UNPRIVILEGED | hikari.Intents.MESSAGE_CONTENT

DEBUG = env("DEBUG", var_type=bool, default=False)

TOKEN = env("TOKEN")

DATABASE_URL = "sqlite://db.sqlite"

MESSAGE_PREFIX = "-t "
