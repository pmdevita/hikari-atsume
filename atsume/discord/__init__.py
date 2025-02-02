async def fetch_member(bot, guild_id, member_id):
    member = bot.cache.get_member(guild_id, member_id)
    if member is None:
        member = await bot.rest.fetch_member(guild_id, member_id)

    return member


async def fetch_guild(bot, guild_id):
    guild = bot.cache.get_guild(guild_id)
    if guild is None:
        guild = await bot.rest.fetch_guild(guild_id)

    return guild
