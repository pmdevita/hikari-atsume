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

        result = (
            await ComponentGuild.select(ComponentGuild.mode)
            .where(
                (ComponentGuild.component == self.component_path)
                & ((ComponentGuild.guild_id == guild_id) | (ComponentGuild.all == True))
            )
            .order_by(ComponentGuild.all, ascending=True)
            .first()
        )

        if result:
            value = result["mode"]
        # There's no permission configured at all, default to False
        else:
            value = False

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
