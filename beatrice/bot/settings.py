from atsume.settings.type_hints import *
import hikari

COMPONENTS = [
    "basic",
    "splatgear2"
]

COMPONENT_ALL_GUILDS_PERMISSIONS = [
    "basic",
    "splatgear2"
]

COMPONENT_DM_PERMISSIONS = [
    "basic"
]

COMPONENT_GUILD_PERMISSIONS = {

}

HIKARI_LOGGING = True

INTENTS = hikari.Intents.ALL_UNPRIVILEGED | hikari.Intents.MESSAGE_CONTENT | hikari.Intents.GUILD_MEMBERS
