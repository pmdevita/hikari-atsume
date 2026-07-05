from typing import Optional

from piccolo.columns import BigInt, Boolean, Serial, Varchar
from piccolo.table import Table

from atsume.component.manager import manager


class ComponentSafetyException(Exception):
    pass


def component_name_to_path(name: str) -> str:
    return next(i for i in manager.component_configs if i.name == name).module_path


class ComponentGuild(Table):
    """Configure whether a component is enabled in a guild."""

    id: int = Serial(primary_key=True)
    component: str = Varchar()
    all: bool = Boolean(default=False)
    guild_id: int = BigInt(null=True)
    mode: bool = Boolean(
        default=True
    )  # True = Component is Enabled, False = Component is Disabled

    @classmethod
    async def get_global_mode(cls, component_name: str) -> bool:
        """Get the global default mode for a component. Returns True for Enabled, False for Disabled."""
        component_path = component_name_to_path(component_name)
        model = (
            await cls.objects()
            .where(
                (ComponentGuild.component == component_path)
                & (ComponentGuild.all == True)
            )
            .first()
        )
        if model:
            return model.mode
        return False  # Default to disabled mode

    @classmethod
    async def set_global_mode(
        cls, component_name: str, enabled: bool, ensure_guild_id: Optional[int] = None
    ) -> None:
        """Toggle the global mode for a component."""
        component_path = component_name_to_path(component_name)

        if (
            ensure_guild_id
            and not enabled
            and not (
                await cls.exists().where(
                    ComponentGuild.component == component_path,
                    ComponentGuild.guild_id == ensure_guild_id,
                    ComponentGuild.mode == True,
                )
            )
        ):
            raise ComponentSafetyException(
                "Cannot disable access from within the same guild."
            )

        model = await cls.objects().get_or_create(
            (ComponentGuild.component == component_path) & (ComponentGuild.all == True),
            defaults={
                ComponentGuild.component: component_path,
                ComponentGuild.all: True,
                ComponentGuild.mode: enabled,
            },
        )
        if not model._was_created:
            await model.update_self({ComponentGuild.mode: enabled})

        from atsume.contrib.handles.utils import reset_cache

        reset_cache()

    @classmethod
    async def get_guilds(cls, component_name: str) -> list["ComponentGuild"]:
        """Get the list of guild IDs for a component based on its global mode."""
        component_path = component_name_to_path(component_name)
        return await cls.objects().where(
            (ComponentGuild.component == component_path) & (ComponentGuild.all == False)
        )

    @classmethod
    async def toggle_guild(
        cls, component_name: str, guild_id: int, block_inaccess: bool = False
    ) -> None:
        """Toggle a guild's inclusion/exclusion for a component."""
        # Toggling cycles mode true -> false -> removed
        component_path = component_name_to_path(component_name)
        model = await cls.objects().get_or_create(
            (ComponentGuild.component == component_path)
            & (ComponentGuild.all == False)
            & (ComponentGuild.guild_id == guild_id),
            defaults={
                ComponentGuild.component: component_path,
                ComponentGuild.all: False,
                ComponentGuild.guild_id: guild_id,
                ComponentGuild.mode: True,
            },
        )
        if not model._was_created:
            if model.mode:
                # Switch to Disabled
                if block_inaccess:
                    raise ComponentSafetyException(
                        "Cannot disable access from within the same guild."
                    )
                await model.update_self({ComponentGuild.mode: False})
            else:
                # Remove entry
                if block_inaccess and cls.exists().where(
                    ComponentGuild.component == component_path,
                    ComponentGuild.all == False,
                ):
                    raise ComponentSafetyException(
                        "Cannot disable access from within the same guild."
                    )
                await model.remove()

        from atsume.contrib.handles.utils import reset_cache

        reset_cache()


class ComponentDM(Table):
    """Configure whether a component is enabled in DMs."""

    id: int = Serial(primary_key=True)
    component: str = Varchar()
    mode: bool = Boolean(
        default=True
    )  # True = Component is Enabled, False = Component is Disabled


class ComponentChannelHandle(Table):
    """Store channel handle configuration for components."""

    id: int = Serial(primary_key=True)
    component: str = Varchar()
    handle_name: str = Varchar()
    guild_id: int = BigInt()
    channel_id: int = BigInt(null=True)
    all: bool = Boolean(
        default=False
    )  # Whether this handle represents all channels in a Guild

    # For handles representing all channels (no channel ID), True = Include all by default, False = Exclude all by default
    # Rows representing channels override the guild's handle default, True = Channel is included, False = Channel is excluded
    mode: bool = Boolean(default=True)
