from atsume.settings import env
from atsume.settings.type_hints import *  # noqa: F403

TOKEN = env("TOKEN")

MESSAGE_PREFIX = "-t"

DATABASE_URL = "sqlite://db.sqlite"

# DATABASE_URL = "postgresql://user:password@localhost:5432/hi_bot_db"
