import hikari

from atsume.settings.type_hints import *

TOKEN = "MTIzNDU2Nzg5MA==.Your Discord Bot Token"

DATABASE_URL = "sqlite:///db.sqlite"

DEBUG = True

COMPONENTS = []

EXTENSIONS = []

HIKARI_LOGGING = False

INTENTS = hikari.Intents.ALL_UNPRIVILEGED

MESSAGE_PREFIX = None
