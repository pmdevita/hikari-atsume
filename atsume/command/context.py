from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Optional

import hikari
from hikari import CommandInteraction, GatewayBot, Message, ResponseType, undefined

from atsume.discord import fetch_guild, fetch_guild_channel

if TYPE_CHECKING:
    from atsume.component.manager import ComponentManager
    from atsume.components import ComponentModel


class Context(ABC):
    bot: GatewayBot
    guild: hikari.Guild

    def __init__(self, manager: "ComponentManager"):
        self.manager = manager
        self.bot = self.manager.bot

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

    @abstractmethod
    async def respond_with_component(self, component: "ComponentModel") -> None:
        pass


class MessageContext(Context):
    def __init__(self, manager: "ComponentManager", event: hikari.MessageCreateEvent):
        super().__init__(manager)
        self._has_replied = False
        self._event = event

    async def guild(self) -> Optional[hikari.Guild]:
        channel = await fetch_guild_channel(self.bot, self._event.channel_id)
        if isinstance(channel, hikari.GuildChannel):
            return await fetch_guild(self.bot, channel.guild_id)
        raise Exception("Not in a guild")

    async def respond(
        self,
        content: undefined.UndefinedNoneOr[Any] = undefined.UNDEFINED,
        component: Optional["ComponentModel"] = None,
    ) -> Message:
        message = await self.bot.rest.create_message(
            self._event.channel_id, content=content
        )
        return message

    async def respond_with_component(self, component: "ComponentModel") -> None:
        message = await self.bot.rest.create_message(
            self._event.channel_id,
            component=component.build(self.bot),
            flags=hikari.MessageFlag.IS_COMPONENTS_V2,
        )
        await self.manager.components.register_component(message.id, component)

    @property
    def author(self) -> hikari.Member | hikari.User:
        return self._event.author


class CommandContext(Context):
    def __init__(self, manager: "ComponentManager", interaction: CommandInteraction):
        super().__init__(manager)
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
        await self.interaction.create_initial_response(
            ResponseType.MESSAGE_CREATE, content=content
        )
        self._has_replied = True

    async def respond_with_component(
        self, component: "ComponentModel", ephemeral: bool = False
    ) -> None:
        flags = hikari.MessageFlag.IS_COMPONENTS_V2
        if ephemeral:
            flags |= hikari.MessageFlag.EPHEMERAL

        await self.interaction.create_initial_response(
            response_type=ResponseType.MESSAGE_CREATE,
            components=component.build(self.bot),
            flags=flags,
        )
        message = await self.interaction.fetch_initial_response()
        self._has_replied = True
        await self.manager.components.register_component(message.id, component)

    @property
    def author(self) -> hikari.Member:
        return self.interaction.member
