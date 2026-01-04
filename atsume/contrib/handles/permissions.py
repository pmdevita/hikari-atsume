from atsume.contrib.handles.models import ComponentDM, ComponentGuild
from atsume.permissions import AbstractComponentPermissions


class DatabasePermissions(AbstractComponentPermissions):
    async def allow_in_guild(self, guild_id: int) -> bool:
        return await ComponentGuild.exists().where(
            (ComponentGuild.component == self.component_path)
            # Not individually disabled
            & ComponentGuild.component.not_in(
                ComponentGuild.select(ComponentGuild.component).where(
                    (ComponentGuild.guild_id == guild_id)
                    & (ComponentGuild.mode == False)
                )
            )
            # Not globally disabled or is individually enabled
            & ComponentGuild.component.is_in(
                ComponentGuild.select(ComponentGuild.component).where(
                    # Either globally enabled
                    ((ComponentGuild.all == True) & (ComponentGuild.mode == True))
                    # Or individually enabled
                    | (
                        (ComponentGuild.guild_id == guild_id)
                        & (ComponentGuild.mode == True)
                    )
                )
            )
        )

    async def allow_in_dm(self) -> bool:
        return await ComponentDM.exists().where(
            ComponentDM.component == self.component_path
        )
