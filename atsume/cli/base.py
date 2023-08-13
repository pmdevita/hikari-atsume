import os
from pathlib import Path

import click
import hikari


class CLIContext(click.Context):
    """
    A dataclass to carry data to subcommands in Click.
    """

    bot: hikari.GatewayBot
    """A reference to the Hikari bot object"""
    project_dir: Path
    """The path to the root directory of the project."""


@click.group()
@click.pass_context
def cli(ctx: click.Context) -> None:
    """
    This is the main click command group used within a project. It bootstraps Atsume with the settings
    defined in the environment variable `ATSUME_SETTINGS_MODULE` and instantiates the main bo object.
    """
    assert isinstance(ctx, CLIContext)
    bot_module = os.environ["ATSUME_SETTINGS_MODULE"]
    from atsume.bot import create_bot

    ctx.obj = create_bot(bot_module)


cli.context_class = CLIContext
