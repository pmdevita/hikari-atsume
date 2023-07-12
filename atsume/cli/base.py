import os

import click


@click.group()
@click.pass_context
def cli(ctx: click.Context) -> None:
    bot_module = os.environ["ATSUME_SETTINGS_MODULE"]
    from atsume.bot import create_bot

    ctx.obj = create_bot(bot_module)
