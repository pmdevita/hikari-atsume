import asyncio
from functools import wraps
from typing import Optional

import click
from piccolo.apps.migrations.commands.forwards import forwards
from piccolo.apps.migrations.commands.new import new

from atsume.cli.base import cli


def sync(func):
    """Decorator that wraps coroutine with asyncio.run."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    return wrapper


@cli.command("makemigrations")
@click.option(
    "--component_name",
    "-c",
    help="Specify a specific component to make migrations for.",
)
@click.option(
    "--empty", is_flag=True, default=False, help="Create an empty migration file."
)
@sync
async def make_migrations(
    component_name: Optional[str] = None, empty: bool = False
) -> None:
    await new(component_name if component_name else "all", auto=not empty)


@cli.command(name="upgrade")
@click.option("--component_name", "-c", help="Specify a specific component to upgrade.")
@sync
async def upgrade_command(component_name: Optional[str] = None) -> None:
    await forwards("all" if component_name is None else component_name)
