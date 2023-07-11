import typing

from hikari import Intents

TOKEN: str

COMPONENTS: list[str]

COMPONENT_ALL_GUILDS_PERMISSIONS: list[str]

COMPONENT_DM_PERMISSIONS: list[str]

COMPONENT_GUILD_PERMISSIONS: dict[int, list[str]]

HIKARI_LOGGING: bool

INTENTS: Intents

MESSAGE_PREFIX: typing.Optional[str]

DATABASE_URL: str

MIDDLEWARE: list[str]
