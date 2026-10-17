from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.column_types import BigInt, Integer
from piccolo.columns.indexes import IndexMethod

ID = "2025-12-29T19:24:59:867128"
VERSION = "1.30.0"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="basic", description=DESCRIPTION
    )

    manager.add_table(
        class_name="PiccoloHiCounter",
        tablename="piccolo_hi_counter",
        schema=None,
        columns=None,
    )

    manager.add_column(
        table_class_name="PiccoloHiCounter",
        tablename="piccolo_hi_counter",
        column_name="count",
        db_column_name="count",
        column_class_name="Integer",
        column_class=Integer,
        params={
            "default": 0,
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="PiccoloHiCounter",
        tablename="piccolo_hi_counter",
        column_name="user",
        db_column_name="user",
        column_class_name="BigInt",
        column_class=BigInt,
        params={
            "default": 0,
            "null": False,
            "primary_key": True,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    return manager
