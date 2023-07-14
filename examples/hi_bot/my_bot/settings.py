import hikari
from atsume.settings.type_hints import *

COMPONENTS = ["basic"]

COMPONENT_PERMISSIONS_CLASS = "atsume.permissions.SettingsPermissions"

COMPONENT_ALL_GUILDS_PERMISSIONS = ["basic"]

MIDDLEWARE = []

HIKARI_LOGGING = False

INTENTS = hikari.Intents.ALL_UNPRIVILEGED | hikari.Intents.MESSAGE_CONTENT
