from piccolo.apps.migrations.auto.migration_manager import MigrationManager

ID = "2026-07-30T01:53:25:954747"
VERSION = "1.35.0"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(migration_id=ID, app_name="", description=DESCRIPTION)

    async def run():
        ComponentGuild = await manager.get_table_from_snapshot(
            app_name="handles", table_class_name="ComponentGuild"
        )
        await ComponentGuild.objects().get_or_create(
            (ComponentGuild.component == "atsume.contrib.handles")
            & (ComponentGuild.all == True),
            defaults={
                ComponentGuild.component: "atsume.contrib.handles",
                ComponentGuild.all: True,
                ComponentGuild.mode: True,
            },
        )

    manager.add_raw(run)

    return manager
