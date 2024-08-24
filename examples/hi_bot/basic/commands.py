import tanjun
import atsume

from typing import Annotated, Optional
from tanjun.annotations import Member, Positional

from .models import *

# Create your commands here.


@tanjun.annotations.with_annotated_args(follow_wrapped=True)
@tanjun.as_message_command("hi", "hello", "hey", "howdy")
@tanjun.as_slash_command("hi", "The bot says hi.")
async def hello(
    ctx: tanjun.abc.Context,
    member: Annotated[Optional[Member], "The user to say hi to.", Positional()] = None,
) -> None:
    member = member if member else ctx.member
    if member:
        count_model, _ = await HiCounter.objects.get_or_create(
            user=member.user.id, _defaults={"count": 0}
        )
        count_model.count = count_model.count + 1
        await count_model.upsert()
        await ctx.respond(
            f"Hi {member.display_name}! (You've said hi {count_model.count} time[s]!)"
        )
