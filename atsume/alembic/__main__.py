import alembic.util.exc
import click

from alembic.command import revision

from atsume.bot import create_bot
from atsume.alembic.config import get_alembic_config
from atsume.component.manager import manager


@click.group(name="alembic")
def alembic_group() -> None:
    pass


@alembic_group.command()
@click.argument("bot_module")
def makemigrations(bot_module: str) -> None:
    bot = create_bot(bot_module)
    apps = manager.component_configs
    print(apps)
    for app in apps:
        cfg = get_alembic_config(app)
        # If the app has zero models, skip it
        if len(app._models) == 0:
            continue
        try:
            revision(cfg, "New migration", autogenerate=True)
        except alembic.util.exc.CommandError as e:
            if e.args[0] == "Target database is not up to date.":
                print(f"Cannot migrate {app}, a migration hasn't been applied.")
            else:
                raise e


if __name__ == "__main__":
    alembic_group()
