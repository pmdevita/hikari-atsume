import hikari
from atsume.settings.type_hints import *

COMPONENTS = []

COMPONENT_PERMISSIONS_CLASS = "atsume.permissions.SettingsPermissions"

COMPONENT_ALL_GUILDS_PERMISSIONS = []

COMPONENT_DM_PERMISSIONS = []

COMPONENT_GUILD_PERMISSIONS = {}

MIDDLEWARE = []

HIKARI_LOGGING = False

INTENTS = hikari.Intents.ALL_UNPRIVILEGED

MESSAGE_PREFIX = None

DATABASE_URL = "sqlite:///db.sqlite"
