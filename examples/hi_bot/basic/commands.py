from typing import Optional

import hikari

from atsume.command import CommandModel
from atsume.command.context import Context
from atsume.command.model import command

from .models import *  # noqa: F403

# Create your commands here.


class Hi(CommandModel):
    member: Optional[hikari.Member]


@command
async def hi(ctx: Context, args: Hi) -> None:
    member = args.member if args.member else ctx.author

    await ctx.respond(f"Hello {member.display_name}.")


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
