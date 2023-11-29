"""
These are a set of functions called to coordinate the bootstrapping of the Atsume framework.
You probably shouldn't ever have to call these unless you're building something on top of them.

"""
import gc
import importlib
import importlib.util
import logging
import os
import sys
import typing

import hikari
import click
import hupper  # type: ignore
import tanjun

from atsume.settings import settings
from atsume.component.decorators import (
    BaseCallback,
    AtsumeEventListener,
    AtsumeComponentClose,
    AtsumeComponentOpen,
    AtsumeTimeSchedule,
    AtsumeIntervalSchedule,
)
from atsume.cli.base import cli
from atsume.db.manager import database
from atsume.component.manager import manager as component_manager
from atsume.component import Component, ComponentConfig
from atsume.extensions.loader import attach_extensions, load_module_class
from atsume.utils import module_to_path


def initialize_atsume(bot_module: str) -> None:
    """
    Initializes Atsume's settings and database. Should be called first
    when bootstrapping the framework.
    """
    settings._initialize(bot_module)
    path = module_to_path(bot_module)
    if path not in sys.path:
        sys.path.insert(0, module_to_path(bot_module))
    if settings.HIKARI_LOGGING:
        logging.basicConfig(level=logging.DEBUG)
    if not settings.DISABLE_UVLOOP:
        try:
            if sys.platform != "win32":
                import uvloop

                uvloop.install()
                logging.info("Enabling uvloop...")
        except ImportError:
            pass

    # This needs to get done before we load any database models
    database._create_database()


def initialize_discord() -> typing.Tuple[hikari.GatewayBot, tanjun.Client]:
    """
    Instantiate the Hikari bot and Tanjun client. Should be called after
    `initialize_atsume`.
    :return:
    """
    bot = hikari.impl.GatewayBot(
        settings.TOKEN, intents=hikari.Intents(settings.INTENTS)
    )

    if settings.VOICE_COMPONENT:
        bot._voice = load_module_class(
            settings.VOICE_COMPONENT, hikari.impl.VoiceComponentImpl
        )(bot)

    global_commands = not settings.DEBUG and settings.GLOBAL_COMMANDS

    client = tanjun.Client.from_gateway_bot(
        bot, declare_global_commands=global_commands, mention_prefix=False
    )
    if settings.MESSAGE_PREFIX:
        client.add_prefix(settings.MESSAGE_PREFIX)
    return bot, client


def create_bot(
    bot_module: str, declare_global_commands: bool = True
) -> hikari.GatewayBot:
    """
    Given the module path for an Atsume project, bootstrap the framework and load it.
    The bootstrapping steps in order are:

    1. :py:func:`initialize_atsume`
    2. :py:func:`initialize_discord`
    3. :py:func:`atsume.extensions.loader.attach_extensions`
    4. :py:func:`load_components`

    :param bot_module: The module path for the Atsume project to start.
    :param declare_global_commands: Whether slash commands should be declared as global commands to Discord.
    :return: An initialized :py:class:`hikari.GatewayBot` object.
    """
    initialize_atsume(bot_module)
    bot, client = initialize_discord()
    attach_extensions(client)
    load_components(client)
    return bot


def run_bot(bot: hikari.GatewayBot) -> None:
    bot.run(asyncio_debug=settings.DEBUG)


@cli.command("run")
@click.pass_obj
def start_bot(bot: hikari.GatewayBot) -> None:
    """
    The project CLI command to run the bot

    :param bot: The bot instance to run.
    """
    if settings.DEBUG:
        # IDK if this is necessary but might reduce overhead
        del bot
        gc.collect()
        reloader = hupper.start_reloader("atsume.bot.autoreload_start_bot")
    else:
        run_bot(bot)


def autoreload_start_bot() -> None:
    bot = create_bot(os.environ["ATSUME_SETTINGS_MODULE"])
    run_bot(bot)


def load_components(client: tanjun.abc.Client) -> None:
    """
    Load the ComponentConfigs as dictated by the settings and then load the component for each of them.

    :param client: The Tanjun Client to load the components on to.
    """
    component_manager._load_components()
    for component_config in component_manager.component_configs:
        load_component(client, component_config)


def load_component(
    client: tanjun.abc.Client, component_config: ComponentConfig
) -> None:
    """
    Load a Component from its config, attach permissions, and attach it to the client.

    :param client: A Tanjun Client to attach the component to.
    :param component_config: The ComponentConfig to attach it to.
    :return:
    """
    try:
        models_module = importlib.import_module(component_config.models_path)
    except ModuleNotFoundError:
        logging.warning(f"Was not able to load database models for {component_config}")

    # Create the component and load the commands into it
    component = Component(name=component_config.name)
    module = importlib.import_module(component_config.commands_path)
    module_attrs = vars(module)
    component.load_from_scope(scope=module_attrs)
    # Create the permissions class and check and add it to the component
    if component_config.permissions:
        component.set_permissions(component_config.permissions)

    # Todo: Remove this once this feature is added to Tanjun
    # Update: Might not since we're appending in extra functionality here
    for value in module_attrs.values():
        if isinstance(value, BaseCallback):
            value._component = component
            if isinstance(value, AtsumeEventListener):
                if component_config.permissions:
                    value.permissions = component_config.permissions
                component.add_listener(value.event_type, value)
            elif isinstance(value, AtsumeComponentOpen):
                component.add_on_open(value)
            elif isinstance(value, AtsumeComponentClose):
                component.add_on_close(value)
            elif isinstance(value, AtsumeTimeSchedule):
                component.add_schedule(value.as_time_schedule())
            elif isinstance(value, AtsumeIntervalSchedule):
                component.add_schedule(value.as_interval())
    client.add_component(component)
