from abc import ABC, abstractmethod
from typing import Any, Optional

import hikari
from hikari import CommandInteraction, GatewayBot, undefined

from atsume.discord import fetch_guild


class Context(ABC):
    bot: GatewayBot
    guild: hikari.Guild

    @abstractmethod
    async def guild(self) -> Optional[hikari.Guild]:
        pass

    @abstractmethod
    async def respond(
        self, content: undefined.UndefinedNoneOr[Any] = undefined.UNDEFINED
    ) -> None:
        pass

    @property
    @abstractmethod
    def author(self) -> hikari.Member:
        pass


class CommandInteractionContext(Context):
    def __init__(self, bot: hikari.GatewayBot, interaction: CommandInteraction):
        self.bot = bot
        self._interaction = interaction
        self._has_replied = False

    @property
    def interaction(self) -> CommandInteraction:
        return self._interaction

    @property
    def has_replied(self) -> bool:
        return self._has_replied

    async def guild(self) -> Optional[hikari.Guild]:
        if self.interaction.guild_id:
            return await fetch_guild(self.bot, self.interaction.guild_id)
        return None

    async def respond(
        self, content: undefined.UndefinedNoneOr[Any] = undefined.UNDEFINED
    ) -> None:
        await self.interaction.edit_initial_response(content)
        self._has_replied = True

    @property
    def author(self) -> hikari.Member:
        return self.interaction.member
