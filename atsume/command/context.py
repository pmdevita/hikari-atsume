from abc import ABC, abstractmethod
from typing import Any

import hikari
from hikari import GatewayBot, CommandInteraction, undefined

from atsume.discord import fetch_guild


class Context(ABC):
    bot: GatewayBot
    guild: hikari.Guild

    @abstractmethod
    async def guild(self):
        pass

    @abstractmethod
    async def respond(
        self, content: undefined.UndefinedNoneOr[Any] = undefined.UNDEFINED
    ):
        pass

    @property
    @abstractmethod
    def author(self):
        pass


class CommandInteractionContext(Context):
    def __init__(self, bot: hikari.GatewayBot, interaction: CommandInteraction):
        self.bot = bot
        self.interaction = interaction
        self._has_replied = False

    async def guild(self):
        return fetch_guild(self.bot, self.interaction.guild_id)

    @property
    def has_replied(self):
        return self._has_replied

    async def respond(
        self, content: undefined.UndefinedNoneOr[Any] = undefined.UNDEFINED
    ):
        await self.interaction.edit_initial_response(content)
        self._has_replied = True

    @property
    def author(self):
        return self.interaction.member
