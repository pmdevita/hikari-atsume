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


async def fetch_guild_channel(
    bot: hikari.GatewayBot,
    channel_id: hikari.Snowflakeish,
) -> hikari.PartialChannel:
    channel: Optional[hikari.PartialChannel] = bot.cache.get_guild_channel(channel_id)
    if channel is None:
        channel = await bot.rest.fetch_channel(channel_id)

    return channel


async def fetch_role(
    bot: hikari.GatewayBot,
    guild_id: hikari.Snowflakeish,
    role_id: hikari.Snowflakeish,
) -> hikari.Role:
    role: Optional[hikari.Role] = bot.cache.get_role(role_id)
    if role is None:
        role = await bot.rest.fetch_role(guild_id, role_id)

    return role


async def fetch_mentionable(
    bot: hikari.GatewayBot,
    guild_id: hikari.Snowflakeish,
    mentionable_id: hikari.Snowflakeish,
) -> hikari.Role | hikari.Member:
    member = await fetch_member(bot, guild_id, mentionable_id)
    if member is None:
        return await fetch_role(bot, guild_id, mentionable_id)
    return member
