import importlib
import logging
import shlex
from typing import TYPE_CHECKING, Optional, cast

import hikari
from hikari import CommandInteraction
from hikari import Event as HikariBaseEvent
from hikari import (
    GuildJoinEvent,
    InteractionCreateEvent,
    InteractionType,
    MessageCreateEvent,
    ResponseType,
    StartingEvent,
)

from atsume.command.context import CommandContext
from atsume.command.exceptions import CommandNotFound
from atsume.command.model import Event, RootCommand
from atsume.settings import settings

if TYPE_CHECKING:
    from atsume.apps.manager import ComponentManager

logger = logging.getLogger(__name__)


class CommandManager:
    def __init__(self, manager: "ComponentManager"):
        self.manager = manager
        self.bot = self.manager.bot
        self.manager.bot.subscribe(StartingEvent, self._on_starting)
        self.manager.bot.subscribe(GuildJoinEvent, self._on_guild_join)
        self.manager.bot.subscribe(hikari.InteractionCreateEvent, self._on_interaction)
        self.manager.bot.subscribe(hikari.MessageCreateEvent, self._on_message)

        self.commands: dict[str, RootCommand] = {}
        self.events: dict[hikari.Event, list[Event]] = {}
        for component in self.manager.component_configs:
            # Create the component and load the commands into it
            module = importlib.import_module(component.commands_path)
            module_attrs = vars(module)

            for value in module_attrs.values():
                if isinstance(value, RootCommand):
                    self.commands[value.name] = value
                    value.component = component
                if isinstance(value, Event):
                    if value.event not in self.events:
                        self.events[value.event] = []
                    self.events[value.event].append(value)
                    value.bot = self.bot
                    value.component = component

        for event, funcs in self.events.items():
            for func in funcs:
                self.manager.bot.subscribe(event, func)

    async def _on_starting(self, event: StartingEvent) -> None:
        await self._register_commands(event)

    async def _on_guild_join(self, event: GuildJoinEvent) -> None:
        await self._register_commands(event)

    async def _register_commands(self, event: Optional[HikariBaseEvent] = None):
        logger.info("Registering commands...")

        self.application = await self.manager.bot.rest.fetch_application()

        commands = [
            i.as_command()
            for i in self.commands.values()
            if i.takes_context_type(CommandContext)
        ]

        if isinstance(event, GuildJoinEvent):
            # Single register
            await self.bot.rest.set_application_commands(
                self.application, commands, event.guild_id
            )
        else:
            async for guild in self.bot.rest.fetch_my_guilds():
                await self.bot.rest.set_application_commands(
                    self.application, commands, guild.id
                )

    async def _on_interaction(self, event: InteractionCreateEvent) -> None:
        match event.interaction.type:
            case InteractionType.APPLICATION_COMMAND:
                await self._on_application_command(
                    cast(CommandInteraction, event.interaction)
                )
            case _:
                pass

    async def _on_application_command(self, interaction: CommandInteraction) -> None:
        command = self.commands.get(interaction.command_name, None)

        if command is None:
            await interaction.create_initial_response(
                ResponseType.MESSAGE_CREATE, "Unknown command."
            )
            return

        # await interaction.create_initial_response(ResponseType.DEFERRED_MESSAGE_CREATE)

        if command.component and command.component.permissions:
            if not await command.component.permissions.allow_in_guild(
                interaction.guild_id
            ):
                logger.debug(f"Blocked command {command} due to permissions.")
                await interaction.create_initial_response(
                    ResponseType.MESSAGE_CREATE, "Command could not be run."
                )
                return

        ctx = None
        try:
            ctx = await command.call_with_interaction(
                self.manager, interaction, interaction.options
            )

            # Context might be None if command wasn't called
            if ctx is None:
                return

            if not ctx.has_replied:
                logger.warning(
                    f"Command {command} did not respond to the interaction command!"
                )
                await interaction.create_initial_response(
                    response_type=ResponseType.MESSAGE_CREATE,
                    content="The command did not respond.",
                )
        except:
            if ctx and not ctx.has_replied:
                await interaction.create_initial_response(
                    response_type=ResponseType.MESSAGE_CREATE,
                    content="An error has occurred.",
                )
            raise

    async def _on_message(self, event: MessageCreateEvent) -> None:
        if event.message.content is None:
            return

        if not event.message.content.startswith(settings.MESSAGE_PREFIX):
            return

        command = shlex.split(
            event.message.content.removeprefix(settings.MESSAGE_PREFIX).strip()
        )

        first, args = command[0], command[1:]

        try:
            entry_command = self.commands.get(first, None)

            if not entry_command:
                raise CommandNotFound(None)

            await entry_command.call_with_args(self.manager, event, args)
        except CommandNotFound as e:
            e.prepend_command_word(first)
            logger.info(f"Command {e.name} does not exist")
