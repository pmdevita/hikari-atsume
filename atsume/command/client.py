import importlib
import logging
import shlex
from typing import TYPE_CHECKING, cast

import hikari
from hikari import (
    CommandInteraction,
    InteractionCreateEvent,
    InteractionType,
    MessageCreateEvent,
    ResponseType,
    StartingEvent,
)

from atsume.command.exceptions import CommandNotFound
from atsume.command.model import CommandMixin, RootCommand
from atsume.settings import settings

if TYPE_CHECKING:
    from atsume.component.manager import ComponentManager

logger = logging.getLogger(__name__)


class CommandManager:
    def __init__(self, manager: "ComponentManager"):
        self.manager = manager
        self.bot = self.manager.bot
        self.manager.bot.subscribe(StartingEvent, self._on_starting)
        self.manager.bot.subscribe(hikari.InteractionCreateEvent, self._on_interaction)
        self.manager.bot.subscribe(hikari.MessageCreateEvent, self._on_message)

        self.commands: dict[str, RootCommand] = {}
        for component in self.manager.component_configs:
            # Create the component and load the commands into it
            module = importlib.import_module(component.commands_path)
            module_attrs = vars(module)

            for value in module_attrs.values():
                if isinstance(value, RootCommand):
                    self.commands[value.name] = value

    async def _on_starting(self, event: StartingEvent) -> None:
        logger.info("Registering commands...")

        self.application = await self.manager.bot.rest.fetch_application()

        commands = [i.as_command() for i in self.commands.values()]

        async for guild in self.bot.rest.fetch_my_guilds():
            await self.bot.rest.set_application_commands(
                self.application, commands, guild.id
            )

    async def _on_interaction(self, event: InteractionCreateEvent) -> None:
        print(event)
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

        await interaction.create_initial_response(ResponseType.DEFERRED_MESSAGE_CREATE)

        try:
            ctx = await command.call_with_interaction(
                self.bot, interaction, interaction.options
            )

            if not ctx.has_replied:
                logger.warning(
                    f"Command {command} did not respond to the interaction command!"
                )
                await interaction.edit_initial_response("The command did not respond.")
        except:
            await interaction.edit_initial_response("An error has occurred.")
            raise

    async def _on_message(self, event: MessageCreateEvent) -> None:
        if event.message.content is None:
            return

        if not event.message.content.startswith(settings.MESSAGE_PREFIX):
            return

        command = shlex.split(event.message.content)
        print(command)

    async def _route_message_command(self, command_args: list[str]) -> CommandMixin:
        value, command_args = command_args[0], command_args[1:]

        try:
            entry_command = self.command_tree.get(value, None)

            if not entry_command:
                raise CommandNotFound(value)

            return entry_command.get_subcommand(command_args)
        except CommandNotFound as e:
            logger.info(f"Command {e.name} does not exist")
