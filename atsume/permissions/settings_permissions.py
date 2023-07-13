import logging

from atsume.settings import settings
from .base import AbstractComponentPermissions

logger = logging.getLogger(__name__)


class SettingsPermissions(AbstractComponentPermissions):
    """
    Permissions implementation that can be configured through Atsume's settings.
    """

    def __init__(self, component_path: str):
        self.component_path = component_path

    def allow_in_dm(self) -> bool:
        result = (
            self.component_path in settings.COMPONENT_DM_PERMISSIONS
            or self.component_path in settings.COMPONENT_ALL_GUILDS_PERMISSIONS
        )
        logger.info(
            f"{'Allowing' if result else 'Denying'} {self.component_path} in DM"
        )
        return result

    def allow_in_guild(self, guild_id: int) -> bool:
        result = (
            self.component_path
            in settings.COMPONENT_GUILD_PERMISSIONS.get(guild_id, [])
            or self.component_path in settings.COMPONENT_ALL_GUILDS_PERMISSIONS
        )
        logger.info(
            f"{'Allowing' if result else 'Denying'} {self.component_path} in Guild {guild_id}"
        )
        return result
