import hikari
from hikari import CommandInteraction, OptionType

from atsume.discord import fetch_member


async def interaction_options_to_objects(
    bot: hikari.GatewayBot, interaction: CommandInteraction
):
    options = {}
    for option in interaction.options:
        print(option)
        match option.type:
            case OptionType.USER:
                options[option.name] = await fetch_member(
                    bot, interaction.guild_id, option.value
                )
            case _:
                options[option.name] = option.value

    return options
