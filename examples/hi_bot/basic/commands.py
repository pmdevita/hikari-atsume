import re
from typing import Optional

import hikari
from hikari import MessageCreateEvent

from atsume.command import CommandModel, Group, command, event
from atsume.command.context import CommandContext, MessageContext
from atsume.discord import fetch_guild_channel

from .models import *  # noqa: F403

# Create your commands here.


class Hi(CommandModel):
    member: Optional[hikari.Member]
    channel: Optional[hikari.GuildChannel]
    role: Optional[hikari.Role]


test_group = Group("group")


@test_group.subcommand("hi")
async def hi_group(ctx: MessageContext, args: Hi) -> None:
    member = args.member if args.member else ctx.author

    await ctx.respond(f"Hello {member.display_name}. (group)")


sub_group = test_group.subgroup("subgroup")


@sub_group.subcommand("hi")
async def hi_subgroup(ctx: CommandContext | MessageContext, args: Hi) -> None:
    member = args.member if args.member else ctx.author

    await ctx.respond(f"Hello {member.display_name}. (subgroup)")


@command
async def hi(ctx: CommandContext | MessageContext, args: Hi) -> None:
    member = args.member if args.member else ctx.author

    await ctx.respond(f"Hello {member.display_name}. (root) {args.model_dump()}")


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


# @tanjun.annotations.with_annotated_args(follow_wrapped=True)
# @tanjun.as_message_command("hi", "hello", "hey", "howdy")
# @tanjun.as_slash_command("hi", "The bot says hi.")
# async def hello(
#     ctx: tanjun.abc.Context,
#     member: Annotated[Optional[Member], "The user to say hi to.", Positional()] = None,
# ) -> None:
#     member = member if member else ctx.member
#     if member:
#         count_model, _ = await HiCounter.objects.get_or_create(
#             user=member.user.id, _defaults={"count": 0}
#         )
#         count_model.count = count_model.count + 1
#         await count_model.upsert()
#         await ctx.respond(
#             f"Hi {member.display_name}! (You've said hi {count_model.count} time[s]!)"
#         )
