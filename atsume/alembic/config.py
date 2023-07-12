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
    # Configuration is dynamically generated
    cfg = Config(ini_section=component_config.name)
    # NXAlembic uses a bundled env.py rather than a user one since setup is largely the same for each project
    cfg.set_main_option("script_location", str(Path(__file__).parent / "template"))
    # We can use an in memory database to simulate the database state without touching
    # the developer's database
    if in_memory:
        cfg.set_main_option("sqlalchemy.url", "sqlite://")
        cfg.engine = sqlalchemy.create_engine("sqlite://")
    else:
        cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
        cfg.engine = settings.DATABASE_URL
    # This is where this app's migration files will end up
    # Migration path needs to be a path relative to cwd
    migrations_path = component_config.db_migration_path.relative_to(Path(os.getcwd()))
    cfg.set_section_option(
        component_config.name, "version_locations", str(migrations_path)
    )
    # This app's alembic migration table
    cfg.set_main_option("version_table", get_alembic_table_name(component_config.name))
    # This is used by env.py
    cfg.component_config = component_config
    cfg.app_metadata = component_config._model_metadata
    # Migrations also needs awareness for all tables used by the bot
    cfg.all_tables = get_all_tables()

    # Get the previous revision's number
    cfg.previous_revision_number = -1
    scripts = ScriptDirectory.from_config(cfg)
    rev = scripts.get_current_head()
    if rev:
        script = scripts.get_revision(rev)
        if script:
            cfg.previous_revision_number = int(script.module.revision)

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

    cfg.previous_model_mapping = previous_models

    current_models = {
        model.Meta._qual_name: model.Meta.tablename for model in component_config.models
    }
    add_models = {}
    remove_models = {}
    # Find the models we are adding
    for model_name, table_name in current_models.items():
        if model_name not in previous_models:
            add_models[model_name] = table_name
    # Find the models we are removing
    for model_name, table_name in previous_models.items():
        if model_name not in current_models:
            remove_models[model_name] = table_name

    cfg.add_models = add_models
    cfg.remove_models = remove_models
    cfg.rename_models = {}

    return cfg
