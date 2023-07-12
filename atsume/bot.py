import importlib
import importlib.util
import logging
import sys
import typing

import aiohttp
import alluka
import hikari
import click
import tanjun

from atsume.settings import settings
from atsume.component.component_config import ComponentConfig
from atsume.component.decorators import AtsumeEventListener
from atsume.permissions import (
    import_permission_class,
    AbstractComponentPermissions,
    permission_check,
)
from atsume.cli.base import cli
from atsume.db.manager import hook_database, database
from atsume.component.manager import manager as component_manager
from atsume.middleware.loader import attach_middleware
from atsume.utils import module_to_path


def initialize_atsume(bot_module: str) -> None:
    settings._initialize(bot_module)
    sys.path.insert(0, module_to_path(bot_module))
    if settings.HIKARI_LOGGING:
        logging.basicConfig(level=logging.DEBUG)
    # This needs to get done before we load any database models
    database._create_database()


def initialize_discord() -> typing.Tuple[hikari.GatewayBot, tanjun.Client]:
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
    initialize_atsume(bot_module)
    bot, client = initialize_discord()
    attach_middleware(client)
    load_components(client)
    return bot


@cli.command("run")
@click.pass_obj
def start_bot(bot: hikari.GatewayBot) -> None:
    bot.run()


def load_components(client: tanjun.abc.Client) -> None:
    permission_class = import_permission_class(settings.COMPONENT_PERMISSIONS_CLASS)
    component_manager._load_components()
    for component_config in component_manager.component_configs:
        load_component(client, component_config, permission_class)


def load_component(
    client: tanjun.abc.Client,
    component_config: ComponentConfig,
    permission_class: typing.Type[AbstractComponentPermissions],
) -> None:
    try:
        models_module = importlib.import_module(component_config.models_path)
    except ModuleNotFoundError:
        logging.warning(f"Was not able to load database models for {component_config}")

    # Create the component and load the commands into it
    component = tanjun.Component(name=component_config.name)
    module = importlib.import_module(component_config.commands_path)
    module_attrs = vars(module)
    component.load_from_scope(scope=module_attrs)
    # Create the permissions class and check and add it to the component
    permissions = permission_class(component_config.module_path)
    component.add_check(permission_check(permissions))

    # Todo: Remove this once this feature is added to Tanjun
    # Temporary fix: Add event listeners and schedulers to the component
    for value in module_attrs.values():
        if isinstance(value, AtsumeEventListener):
            value.permissions = permissions
            component.add_listener(value.event_type, value)
        # if isinstance(value, tanjun.schedules.TimeSchedule):
        #     component.add_schedule(value)
    client.add_component(component)
