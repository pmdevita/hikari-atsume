import hikari
import tanjun

from typing import Annotated, Optional
from tanjun.annotations import Member, User, Positional


# Write your commands here

@tanjun.annotations.with_annotated_args(follow_wrapped=True)
@tanjun.as_message_command("hi", "hello", "hey", "howdy")
@tanjun.as_slash_command("hi", "The bot says hi.")
async def hello(ctx: tanjun.abc.Context,
                member: Annotated[Optional[Member], "The user to say hi to.", Positional()] = None):
    member = member if member else ctx.member
    await ctx.respond(f"Hi {member.display_name}!")
