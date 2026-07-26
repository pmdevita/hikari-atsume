from atsume.command import command
from atsume.command.context import MessageContext, SlashContext

from .models import *

# Create your commands here.


@command
async def hello(
    ctx: MessageContext | SlashContext,
) -> None:
    member = ctx.author
    if member:
        await ctx.respond(f"Hi {member.display_name}!")
