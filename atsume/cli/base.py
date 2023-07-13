import os
from pathlib import Path

import click
import hikari


class CLIContext(click.Context):
    bot: hikari.GatewayBot
    project_dir: Path


@click.group()
@click.pass_context
def cli(ctx: click.Context) -> None:
    bot_module = os.environ["ATSUME_SETTINGS_MODULE"]
    from atsume.bot import create_bot

    ctx.obj = create_bot(bot_module)


cli.context_class = CLIContext
