from atsume.settings import env
from atsume.settings.type_hints import *  # noqa: F403

TOKEN = env("TOKEN")

MESSAGE_PREFIX = "-t"

DATABASE_URL = "sqlite:///db.sqlite"
