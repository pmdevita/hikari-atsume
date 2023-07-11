import hikari
import tanjun

from typing import Annotated, Optional
from tanjun.annotations import Member, User, Positional, Str
from .models import *


# Write your commands here


@tanjun.annotations.with_annotated_args(follow_wrapped=True)
@tanjun.as_message_command("splatadd")
@tanjun.as_slash_command("splatadd", "The bot says hi.")
async def splatadd(ctx: tanjun.abc.Context,
                   string: Annotated[Str, "Thing to add.", Positional()] = None):
    print(string)
    t = await Test.objects.create(name=string)
    print(t)


@tanjun.annotations.with_annotated_args(follow_wrapped=True)
@tanjun.as_message_command("splatcheck")
@tanjun.as_slash_command("splatcheck", "The bot says hi.")
async def hello(ctx: tanjun.abc.Context):
    objs = await Test.objects.all()
    print(objs)
    await ctx.respond(str(objs))
