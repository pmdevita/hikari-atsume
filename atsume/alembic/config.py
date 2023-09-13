import typing
import os
from pathlib import Path

import sqlalchemy
from alembic.config import Config as AlembicConfig
from alembic.script import ScriptDirectory

from atsume.settings import settings
from atsume.component.manager import manager

if typing.TYPE_CHECKING:
    from atsume.component.component_config import ComponentConfig


def get_alembic_table_name(app_name: str) -> str:
    return f"alembic.{app_name}"


class Config(AlembicConfig):
    app_metadata: sqlalchemy.MetaData
    engine: sqlalchemy.engine.Engine | str
    all_tables: typing.List[str]
    previous_revision_number: int
    component_config: "ComponentConfig"
    previous_model_mapping: dict[str, str]
    # model: table name
    add_models: dict[str, str] = {}
    remove_models: dict[str, str] = {}
    # old table name: new table name
    rename_models: dict[str, str] = {}


def get_all_tables() -> typing.List[str]:
    tables = []
    for app in manager.component_configs:
        tables.append(get_alembic_table_name(app.name))
        tables.extend(app._model_metadata.tables.keys())
    return tables


def get_alembic_config(
    component_config: "ComponentConfig", in_memory: bool = False
) -> Config:
    """
    Generate the config object for Alembic from an Atsume project's settings.
    """
    cfg = Config(ini_section=component_config.name)
    # Use our bundled template env.py and script.py.mako
    cfg.set_main_option("script_location", str(Path(__file__).parent / "template"))
    # We can use either Atsume's configured database settings, or an in memory database
    # The in-memory database is used for making migrations since using a real one would
    # require that database to be up to date on migrations.
    if in_memory:
        cfg.set_main_option("sqlalchemy.url", "sqlite://")
        cfg.engine = sqlalchemy.create_engine("sqlite://")
    else:
        cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
        cfg.engine = settings.DATABASE_URL
    # This is where this component's migration files will end up
    # Migration path needs to be a path relative to cwd
    migrations_path = component_config.db_migration_path.relative_to(Path(os.getcwd()))
    cfg.set_section_option(
        component_config.name, "version_locations", str(migrations_path)
    )
    # The name of this component's Alembic migration table
    cfg.set_main_option("version_table", get_alembic_table_name(component_config.name))
    # The env.py script may want to also pull certain things from the ComponentConfig
    cfg.component_config = component_config
    cfg.app_metadata = component_config._model_metadata
    # TODO: May not be needed anymore now that make migrations simulates the database and for each component
    # Migrations also needs awareness for all tables used by the bot
    cfg.all_tables = get_all_tables()

    # Get the previous migration's revision number
    # The ID of the next migration is the incremented previous migration
    cfg.previous_revision_number = -1
    scripts = ScriptDirectory.from_config(cfg)
    rev = scripts.get_current_head()
    if rev:
        script = scripts.get_revision(rev)
        if script:
            cfg.previous_revision_number = int(script.module.revision)

    # Get the mapping of the model names to table names that reflects the
    # current state of the migration scripts.
    cfg.previous_model_mapping = get_model_table_names(scripts)

    # Get the current mapping of model names to table names.
    current_models = {
        model.Meta._qual_name: model.Meta.tablename for model in component_config.models
    }
    # Determine the changes that we are making to these models.
    add_models = {}
    remove_models = {}
    # All of the models not in the previous model mapping must be models we are adding
    for model_name, table_name in current_models.items():
        if model_name not in cfg.previous_model_mapping:
            add_models[model_name] = table_name
    # All of the models not in the current model mapping must be models we are dropping
    for model_name, table_name in cfg.previous_model_mapping.items():
        if model_name not in current_models:
            remove_models[model_name] = table_name

    cfg.add_models = add_models
    cfg.remove_models = remove_models
    # Renames are figured out in env.py after table schemas are computed.
    cfg.rename_models = {}

    get_formatting(cfg)

    return cfg


def get_model_table_names(scripts: ScriptDirectory) -> dict[str, str]:
    """
    Get a dictionary mapping model names to table names. This mapping reflects the last state
    of the migrations.
    :param scripts: The Alembic ScriptDirectory to check through.
    :return:
    """
    # Get the current set of models
    previous_models: dict[str, str] = {}
    migrations = list(scripts.walk_revisions())
    for migration in reversed(migrations):
        # Order here might eliminate instances of models stepping on each other's toes
        for key in migration.module.remove_models.keys():
            del previous_models[key]
        # Renames are before: after
        for key, value in migration.module.rename_models.items():
            previous_models[value] = previous_models[key]
            del previous_models[key]
        for key, value in migration.module.add_models.items():
            previous_models[key] = value
    return previous_models


def get_formatting(config: Config) -> None:
    """If Black is installed, add configuration to use it for formatting"""
    try:
        import black
    except ImportError:
        return

    config.set_section_option("post_write_hooks", "hooks", "black")
    config.set_section_option("post_write_hooks", "black.type", "console_scripts")
    config.set_section_option("post_write_hooks", "black.entrypoint", "black")
    config.set_section_option("post_write_hooks", "black.options", "-q")
