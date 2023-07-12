import alembic.util.exc
import click

from alembic.command import revision, upgrade, downgrade

from atsume.bot import create_bot
from atsume.alembic.config import get_alembic_config
from atsume.alembic.exceptions import MigrationIsEmpty
from atsume.component.manager import manager
from atsume.utils import pad_number


@click.group(name="alembic")
def alembic_group() -> None:
    pass


@alembic_group.command()
@click.argument("bot_module")
def makemigrations(bot_module: str) -> None:
    create_bot(bot_module)
    apps = manager.component_configs
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


@alembic_group.command(name="upgrade")
@click.argument("bot_module")
def upgrade_command(bot_module: str) -> None:
    create_bot(bot_module)
    apps = manager.component_configs
    for app in apps:
        cfg = get_alembic_config(app)
        # If the app has no models, skip it
        if len(app._models) == 0:
            continue
        upgrade(cfg, "head")


@alembic_group.command(name="downgrade")
@click.argument("bot_module")
@click.argument("app_name")
def downgrade_command(bot_module: str, app_name: str) -> None:
    create_bot(bot_module)
    apps = [app for app in manager.component_configs if app.name == app_name]
    for app in apps:
        cfg = get_alembic_config(app)
        # If the app has no models, skip it
        if len(app._models) == 0:
            continue
        downgrade(cfg, "-1")


if __name__ == "__main__":
    alembic_group()
