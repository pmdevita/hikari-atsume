from typing import Optional

import hikari


async def fetch_member(
    bot: hikari.GatewayBot,
    guild_id: hikari.Snowflakeish,
    member_id: hikari.Snowflakeish,
) -> hikari.Member:
    member: Optional[hikari.Member] = bot.cache.get_member(guild_id, member_id)
    if member is None:
        member = await bot.rest.fetch_member(guild_id, member_id)

    return member


async def fetch_guild(
    bot: hikari.GatewayBot, guild_id: hikari.Snowflakeish
) -> hikari.Guild:
    guild: Optional[hikari.Guild] = bot.cache.get_guild(guild_id)
    if guild is None:
        guild = await bot.rest.fetch_guild(guild_id)

    return guild
