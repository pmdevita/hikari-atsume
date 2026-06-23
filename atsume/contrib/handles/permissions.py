from atsume.contrib.handles.models import ComponentDM, ComponentGuild
from atsume.permissions import AbstractComponentPermissions


class DatabasePermissions(AbstractComponentPermissions):
    def __init__(self, component_path: str) -> None:
        super().__init__(component_path)
        self._guild_cache = {}
        self._dm = None

    def reset_cache(self):
        self._guild_cache = {}
        self._dm = None

    async def allow_in_guild(self, guild_id: int) -> bool:
        if guild_id in self._guild_cache:
            return self._guild_cache[guild_id]

        value = await ComponentGuild.exists().where(
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
        self._guild_cache[guild_id] = value
        return value

    async def allow_in_dm(self) -> bool:
        if self._dm is not None:
            return self._dm

        value = await ComponentDM.exists().where(
            ComponentDM.component == self.component_path
        )
        self._dm = value
        return value
