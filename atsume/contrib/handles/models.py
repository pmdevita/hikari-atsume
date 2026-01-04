from piccolo.columns import BigInt, Boolean, Serial, Varchar
from piccolo.table import Table


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
        model = (
            await cls.objects()
            .where(
                (ComponentGuild.component == component_name)
                & (ComponentGuild.all == True)
            )
            .first()
        )
        if model:
            return model.mode
        return False  # Default to disabled mode

    @classmethod
    async def toggle_global_mode(cls, component_name: str, enabled: bool) -> None:
        """Toggle the global mode for a component."""
        model = await cls.objects().get_or_create(
            (ComponentGuild.component == component_name) & (ComponentGuild.all == True),
            defaults={
                ComponentGuild.component: component_name,
                ComponentGuild.all: True,
                ComponentGuild.mode: enabled,
            },
        )
        if not model._was_created:
            await model.update_self({ComponentGuild.mode: enabled})

    @classmethod
    async def get_guilds(cls, component_name: str) -> list["ComponentGuild"]:
        """Get the list of guild IDs for a component based on its global mode."""
        return await cls.objects().where(
            (ComponentGuild.component == component_name) & (ComponentGuild.all == False)
        )

    @classmethod
    async def toggle_guild(cls, component_name: str, guild_id: int) -> None:
        """Toggle a guild's inclusion/exclusion for a component."""
        # Toggling cycles mode true -> false -> removed
        model = await cls.objects().get_or_create(
            (ComponentGuild.component == component_name)
            & (ComponentGuild.all == False)
            & (ComponentGuild.guild_id == guild_id),
            defaults={
                ComponentGuild.component: component_name,
                ComponentGuild.all: False,
                ComponentGuild.guild_id: guild_id,
                ComponentGuild.mode: True,
            },
        )
        if not model._was_created:
            if model.mode:
                # Switch to Disabled
                await model.update_self({ComponentGuild.mode: False})
            else:
                # Remove entry
                await model.remove()


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
