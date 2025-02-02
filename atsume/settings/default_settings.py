import hikari

from atsume.settings.type_hints import *  # noqa: F403

VOICE_COMPONENT = None

COMPONENTS = []

COMPONENT_PERMISSIONS_CLASS = None

COMPONENT_ALL_GUILDS_PERMISSIONS = []

COMPONENT_DM_PERMISSIONS = []

COMPONENT_GUILD_PERMISSIONS = {}

EXTENSIONS = []

HIKARI_LOGGING = False

INTENTS = hikari.Intents.ALL_UNPRIVILEGED

MESSAGE_PREFIX = None

DATABASE_URL = "sqlite:///db.sqlite"

DEBUG = False

GLOBAL_COMMANDS = False

DISABLE_UVLOOP = False
