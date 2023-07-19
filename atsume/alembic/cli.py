import typing

import alembic.util.exc
import click

from alembic.command import revision, upgrade, downgrade

from atsume.bot import create_bot
from atsume.alembic.config import get_alembic_config
from atsume.alembic.exceptions import MigrationIsEmpty
from atsume.component.manager import manager
from atsume.cli.base import cli
from atsume.utils import pad_number


@cli.command("makemigrations")
@click.option(
    "--component_name",
    "-c",
    help="Specify a specific component to make migrations for.",
)
@click.option(
    "--empty", is_flag=True, default=False, help="Create an empty migration file."
)
def make_migrations(
    component_name: typing.Optional[str] = None, empty: bool = False
) -> None:
    apps = manager.component_configs
    if component_name:
        apps = [app for app in apps if app.name == component_name]
    for app in apps:
        # If the app has no models, skip it
        if len(app.models) == 0:
            continue

        cfg = get_alembic_config(app, in_memory=True)
        # Simulate the migration state up to this point
        upgrade(cfg, "head")

        try:
            revision(
                cfg,
                "New migration",
                autogenerate=True,
                rev_id=pad_number(cfg.previous_revision_number + 1, 4),
            )
        except MigrationIsEmpty:
            print(f"Component {app} does not have to be migrated.")
        except alembic.util.exc.CommandError as e:
            if e.args[0] == "Target database is not up to date.":
                print(f"Cannot migrate {app}, a migration hasn't been applied.")
            else:
                raise e


@cli.command(name="upgrade")
@click.option("--component_name", "-c", help="Specify a specific component to upgrade.")
def upgrade_command(component_name: typing.Optional[str] = None) -> None:
    apps = manager.component_configs
    if component_name:
        apps = [app for app in apps if app.name == component_name]
    for app in apps:
        cfg = get_alembic_config(app)
        # If the app has no models, skip it
        if len(app.models) == 0:
            continue
        upgrade(cfg, "head")


@cli.command(name="downgrade", help="Downgrade a specific component.")
@click.argument("component_name")
def downgrade_command(component_name: str) -> None:
    apps = [app for app in manager.component_configs if app.name == component_name]
    for app in apps:
        cfg = get_alembic_config(app)
        # If the app has no models, skip it
        if len(app.models) == 0:
            continue
        try:
            downgrade(cfg, "-1")
        except alembic.util.exc.CommandError as e:
            if e.args[0] == "Relative revision -1 didn't produce 1 migrations":
                print(f"{app} cannot be downgraded any further.")
