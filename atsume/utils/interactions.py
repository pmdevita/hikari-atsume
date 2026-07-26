from typing import Any, Optional

import hikari
from hikari import CommandInteraction, CommandInteractionOption, OptionType

from atsume.discord import (
    fetch_guild_channel,
    fetch_member,
    fetch_mentionable,
    fetch_role,
)


async def interaction_options_to_objects(
    bot: hikari.GatewayBot,
    interaction: CommandInteraction,
    options: Optional[list[CommandInteractionOption]],
) -> dict[str, Any]:
    objs = {}

    if options is None:
        return objs

    for option in options:
        match option.type:
            case OptionType.USER:
                objs[option.name] = await fetch_member(
                    bot, interaction.guild_id, option.value
                )
            case OptionType.CHANNEL:
                objs[option.name] = await fetch_guild_channel(bot, option.value)
            case OptionType.ROLE:
                objs[option.name] = await fetch_role(
                    bot, interaction.guild_id, option.value
                )
            case OptionType.MENTIONABLE:
                objs[option.name] = await fetch_mentionable(
                    bot, interaction.guild_id, option.value
                )
            case _:
                objs[option.name] = option.value

    return objs


async def string_options_to_objects(
    bot: hikari.GatewayBot, command: list[str]
) -> dict[str, Any]:
    options = {}
    for string in command:
        pass

    return options
