import asyncio
import importlib
import logging
import shlex

import hikari

from typing import TYPE_CHECKING, cast

from hikari import (
    StartingEvent,
    InteractionCreateEvent,
    CommandInteraction,
    InteractionType,
    ResponseType,
    MessageCreateEvent,
)

from atsume.command.context import CommandInteractionContext
from atsume.command.model import Command, command_model_context
from atsume.settings import settings
from atsume.utils.interactions import interaction_options_to_objects

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

        self.commands = {}
        for component in self.manager.component_configs:
            # Create the component and load the commands into it
            module = importlib.import_module(component.commands_path)
            module_attrs = vars(module)

            for value in module_attrs.values():
                if isinstance(value, Command):
                    self.commands[value.name] = value

    async def _on_starting(self, event: StartingEvent):
        logger.info("Registering commands...")

        self.application = await self.manager.bot.rest.fetch_application()

        commands = [i.as_slash_command(self.bot) for i in self.commands.values()]

        async for guild in self.bot.rest.fetch_my_guilds():
            await self.bot.rest.set_application_commands(
                self.application, commands, guild.id
            )

    async def _on_interaction(self, event: InteractionCreateEvent):
        print(event)
        match event.interaction.type:
            case InteractionType.APPLICATION_COMMAND:
                await self._on_application_command(
                    cast(CommandInteraction, event.interaction)
                )
            case _:
                pass

    async def _on_application_command(self, interaction: CommandInteraction):
        command = self.commands.get(interaction.command_name, None)

        if command is None:
            await interaction.create_initial_response(
                ResponseType.MESSAGE_CREATE, "Unknown command."
            )
            return

        await interaction.create_initial_response(ResponseType.DEFERRED_MESSAGE_CREATE)

        try:
            kwargs = await interaction_options_to_objects(self.bot, interaction)

            options = command.command_model(**kwargs)
            ctx = CommandInteractionContext(self.bot, interaction)

            await command(ctx, options)

            if not ctx.has_replied:
                logger.warning(
                    f"Command {command} did not respond to the interaction command!"
                )
                await interaction.edit_initial_response("The command did not respond.")
        except:
            await interaction.edit_initial_response("An error has occurred.")
            raise

    async def _on_message(self, event: MessageCreateEvent):
        if event.message.content is None:
            return

        if not event.message.content.startswith(settings.MESSAGE_PREFIX):
            return

        command = shlex.split(event.message.content)
        print(command)
