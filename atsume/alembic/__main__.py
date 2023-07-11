import os
import typing
from pathlib import Path

import alembic.util.exc
import click
import sqlalchemy

from alembic.command import revision
from alembic.config import Config as AlembicConfig

from atsume.bot import create_bot
from atsume.component.manager import manager
from atsume.settings import settings

if typing.TYPE_CHECKING:
    from atsume.component.component_config import ComponentConfig


class Config(AlembicConfig):
    app_metadata: sqlalchemy.MetaData
    all_tables: typing.List[str]


def get_alembic_config(component_config: "ComponentConfig") -> Config:
    # Configuration is dynamically generated
    cfg = Config(ini_section=component_config.name)
    # NXAlembic uses a bundled env.py rather than a user one since setup is largely the same for each project
    cfg.set_main_option("script_location", str(Path(__file__).parent / "template"))
    cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
    # This is where this app's migration files will end up
    # Migration path needs to be a path relative to cwd
    migrations_path = component_config.db_migration_path.relative_to(Path(os.getcwd()))
    cfg.set_section_option(
        component_config.name, "version_locations", str(migrations_path)
    )
    # This app's alembic migration table
    cfg.set_main_option("version_table", get_alembic_table_name(component_config.name))
    # This is used by env.py
    cfg.app_metadata = component_config._model_metadata
    # Migrations also needs awareness for all tables used by the bot
    cfg.all_tables = get_all_tables()
    return cfg


def get_all_tables() -> typing.List[str]:
    tables = []
    for app in manager.component_configs:
        tables.append(get_alembic_table_name(app.name))
        tables.extend(app._model_metadata.tables.keys())
    return tables


def get_alembic_table_name(app_name: str) -> str:
    return f"alembic.{app_name}"


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
