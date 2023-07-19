"""
# Atsume Bot

These are a set of functions called to coordinate the bootstrapping of the Atsume framework.
You probably shouldn't ever have to call these unless you're building something on top of them.

"""

import importlib
import importlib.util
import logging
import os
import sys
import typing

import aiohttp
import alluka
import hikari
import click
import hupper
import tanjun

from atsume.settings import settings
from atsume.component.component_config import ComponentConfig
from atsume.component.decorators import (
    BaseCallback,
    AtsumeEventListener,
    AtsumeComponentClose,
    AtsumeComponentOpen,
    AtsumeTimeSchedule,
)
from atsume.cli.base import cli
from atsume.db.manager import database
from atsume.component.manager import manager as component_manager
from atsume.component import Component
from atsume.middleware.loader import attach_middleware
from atsume.utils import module_to_path


def initialize_atsume(bot_module: str) -> None:
    """
    Initializes Atsume's settings and database. Should be called first
    when bootstrapping the framework.
    """
    settings._initialize(bot_module)
    sys.path.insert(0, module_to_path(bot_module))
    if settings.HIKARI_LOGGING:
        logging.basicConfig(level=logging.DEBUG)
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

    client = tanjun.Client.from_gateway_bot(
        bot, declare_global_commands=True, mention_prefix=False
    )
    if settings.MESSAGE_PREFIX:
        client.add_prefix(settings.MESSAGE_PREFIX)
    return bot, client


def create_bot(bot_module: str) -> hikari.GatewayBot:
    """
    Given the module path for an Atsume project, bootstrap the framework and load it.
    The bootstrapping steps in order are:
    1. `initialize_atsume`
    2. `initialize_discord`
    3. `atsume.middleware.loader.attach_middleware`
    4. `load_components`
    :param bot_module:
    :return:
    """
    initialize_atsume(bot_module)
    bot, client = initialize_discord()
    attach_middleware(client)
    load_components(client)
    return bot


@cli.command("run")
@click.option("--reload", is_flag=True, default=False)
@click.pass_obj
def start_bot(bot: hikari.GatewayBot, reload: bool) -> None:
    if reload:
        reloader = hupper.start_reloader("atsume.bot.autoreload_start_bot")
        reloader.watch_files()
    else:
        bot.run()


def autoreload_start_bot():
    bot = create_bot(os.environ["ATSUME_SETTINGS_MODULE"])
    bot.run()


def load_components(client: tanjun.abc.Client) -> None:
    """
    Load the ComponentConfigs as dictated by the settings and then load the component for each of them.
    :param client:
    :return:
    """
    component_manager._load_components()
    for component_config in component_manager.component_configs:
        load_component(client, component_config)


def load_component(
    client: tanjun.abc.Client, component_config: ComponentConfig
) -> None:
    """
    Load a Component from its config, attach permissions, and attach it to the client.
    :param client:
    :param component_config:
    :param permission_class:
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
    client.add_component(component)
