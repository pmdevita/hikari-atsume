import typing
from logging.config import fileConfig

from alembic.autogenerate.api import RevisionContext
from alembic.operations import ops
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy.sql.schema import SchemaItem

from alembic import context

from atsume.alembic.config import Config
from atsume.alembic.exceptions import MigrationIsEmpty, ServerDefaultRequired

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
alembic_config = context.config
if not isinstance(alembic_config, Config):
    raise ValueError("Provided config is not an Atsume Alembic Config")
config: Config = alembic_config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support

# This is set when it grabs the app metadata out of the component config
target_metadata = config.app_metadata
all_tables = config.all_tables
version_table = config.get_main_option("version_table")


# target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def metadata_has_table(all_tables: list[str], table_name: typing.Optional[str]) -> bool:
    return table_name in all_tables


def include_object(
    object: SchemaItem,
    name: typing.Optional[str],
    type_: str,
    reflected: bool,
    compare_to: typing.Optional[SchemaItem],
) -> bool:
    if type_ == "table":
        # If this app currently owns this table, allow it
        if name in target_metadata.tables:
            return True
        # If this app previously owned this table, allow it
        if name in config.previous_model_mapping.values():
            return True
        # If we don't know what this table is, don't touch it
        return False
    else:
        # print(object, name, type_)
        return True


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
        version_table=version_table,
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    if isinstance(config.engine, str):
        connectable = engine_from_config(
            config.get_section(config.config_ini_section, {}),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )
    else:
        connectable = config.engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
            version_table=version_table,
            include_object=include_object,
            # https://alembic.sqlalchemy.org/en/latest/autogenerate.html#what-does-autogenerate-detect-and-what-does-it-not-detect
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

# Not sure what's going on here but this property totally does exist at runtime
revision_context: typing.Optional[RevisionContext] = context._proxy.context_opts.get("revision_context")  # type: ignore

# If we are making migrations
if revision_context:
    # If the migration is empty, don't output anything
    is_empty = True
    for revision in revision_context.generated_revisions:
        if len(revision.downgrade_ops.ops) > 0:
            is_empty = False
        if len(revision.upgrade_ops.ops) > 0:
            is_empty = False

    if is_empty:
        raise MigrationIsEmpty()


def table_name_to_model_name(table_name: str) -> typing.Optional[str]:
    for model in config.component_config._models:
        if model.Meta.tablename == table_name:
            # Something funny happened with the types but this should be a string
            assert isinstance(model.Meta._qual_name, str)
            return model.Meta._qual_name
    for old_model, old_table_name in config.previous_model_mapping.items():
        if old_table_name == table_name:
            return old_model
    return None


OPERATION_NAME_TEMPLATES: dict[typing.Type[ops.MigrateOperation], str] = {
    ops.CreateTableOp: "create_{model_name}",
    ops.DropTableOp: "drop_{model_name}",
    ops.ModifyTableOps: "modify_{model_name}{column_name}",
}

# For migrations that don't have a name, attempt to autogenerate it
# Todo: move this to a function and clean it up
if revision_context:
    print(f"Migrating {config.component_config}...")
    for revision in revision_context.generated_revisions:
        # Todo: Make this a sentinel
        if revision.message != "New migration":
            continue
        actions = []
        for upgrade in revision.upgrade_ops.ops:
            template = OPERATION_NAME_TEMPLATES.get(upgrade.__class__, "")
            model_name = table_name_to_model_name(upgrade.table_name)
            if not model_name:
                model_name = ""
            columns = []
            if isinstance(upgrade, ops.CreateTableOp):
                print(f"  Create model {model_name}...")
            elif isinstance(upgrade, ops.DropTableOp):
                print(f"  Drop model {model_name}...")
            elif isinstance(upgrade, ops.ModifyTableOps):
                print(f"  Modify model {model_name}...")
                for op in upgrade.ops:
                    if isinstance(op, ops.AddColumnOp):
                        # If this is being added to an already existing table...
                        if op.table_name in all_tables:
                            # And the column is not nullable or doesn't have a server_default
                            if (
                                not op.column.nullable
                                and op.column.server_default is None
                            ):
                                raise ServerDefaultRequired(model_name, op.column.name)
                            print(op.column)
                        print(f"    Add Column {op.column.name}...")
                        columns.append(op.column.name)
                    elif isinstance(op, ops.DropColumnOp):
                        print(f"    Drop Column {op.column_name}...")
                        columns.append(op.column_name)
                    elif isinstance(op, ops.AlterColumnOp):
                        print(f"    Alter Column {op.column_name}...")
                        columns.append(op.column_name)
            actions.append(
                template.format(model_name=model_name, column_name="_".join(columns))
            )
        if actions:
            name = "_".join(actions)
        else:
            name = "migration"
        revision.message = name
