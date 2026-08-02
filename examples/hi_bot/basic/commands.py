import re
from typing import Optional

import hikari
from hikari import MessageCreateEvent

from atsume.command import CommandModel, Group, command, event
from atsume.command.context import CommandContext, MessageContext
from atsume.discord import fetch_guild_channel

from .models import PiccoloHiCounter

# Create your commands here.


class Hi(CommandModel):
    member: Optional[hikari.Member]
    channel: Optional[hikari.GuildChannel]
    role: Optional[hikari.Role]


test_group = Group("group")


@test_group.subcommand("hi", aliases=["hey", "howdy"])
async def hi_group(ctx: MessageContext | CommandContext, args: Hi) -> None:
    member = args.member if args.member else ctx.author

    await ctx.respond(f"Hello {member.display_name}. (group)")


sub_group = test_group.subgroup("subgroup")


@sub_group.subcommand("hi", aliases=["hey", "howdy"])
async def hi_subgroup(ctx: CommandContext | MessageContext, args: Hi) -> None:
    member = args.member if args.member else ctx.author

    await ctx.respond(f"Hello {member.display_name}. (subgroup)")


@command(aliases=["howdy", "hey"])
async def hi(ctx: CommandContext | MessageContext, args: Hi) -> None:
    member = args.member if args.member else ctx.author

    count_model = await PiccoloHiCounter.objects().get_or_create(
        PiccoloHiCounter.user == member.id, defaults={"count": 0}
    )
    await count_model.update_self({PiccoloHiCounter.count: PiccoloHiCounter.count + 1})
    await ctx.respond(
        f"Hello {member.display_name}. You've said hi {count_model.count} time(s). (root) {args.model_dump()}"
    )


YOUTUBE = re.compile(r"https://(?:youtube.com|youtu.be)/(?:shorts/)?([\w\-_]+)\?si=")


@event
async def yell_at_tracking(bot: hikari.GatewayBot, event: MessageCreateEvent) -> None:
    if not event.content:
        return

    matches = YOUTUBE.findall(event.content)
    if matches:
        channel: hikari.GuildTextChannel = await fetch_guild_channel(
            bot, event.channel_id
        )
        await channel.send(
            f"Hey {event.author.mention} your link has tracking in it you jerk! Use https://youtube.com/watch?v={matches[0]} instead!"
        )
