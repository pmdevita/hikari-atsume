import importlib
import importlib.util
import logging
import sys
import typing
import os

import aiohttp
import alluka
import hikari
import click
import tanjun

from atsume.settings import settings
from atsume.component.component_config import ComponentConfig
from atsume.component.decorators import AtsumeEventListener
from atsume.permissions import import_permission_class, AbstractComponentPermissions, permission_check
from atsume.db.manager import hook_database, database
from atsume.component.manager import manager as component_manager

@click.command()
@click.argument("bot_module")
def start_bot(bot_module: str):
    settings._initialize(bot_module)
    sys.path.insert(0, module_to_path(bot_module))

    if settings.HIKARI_LOGGING:
        logging.basicConfig(level=logging.DEBUG)

    # This needs to get done before we load any database models
    database._create_database()

    bot = hikari.impl.GatewayBot(settings.TOKEN, intents=hikari.Intents(settings.INTENTS))
    client = tanjun.Client.from_gateway_bot(bot, declare_global_commands=True, mention_prefix=False)
    if settings.MESSAGE_PREFIX:
        client.add_prefix(settings.MESSAGE_PREFIX)

    hook_aiohttp(client)
    hook_database(client)

    permission_class = import_permission_class(settings.COMPONENT_PERMISSIONS_CLASS)
    component_manager._load_components()
    for component_config in component_manager.component_configs:
        load_component(client, component_config, permission_class)

    bot.run()


def hook_aiohttp(client: alluka.Injected[tanjun.abc.Client]):
    @client.with_client_callback(tanjun.ClientCallbackNames.STARTING)
    async def on_starting(client: alluka.Injected[tanjun.abc.Client]) -> None:
        client.set_type_dependency(aiohttp.ClientSession, aiohttp.ClientSession())

    @client.with_client_callback(tanjun.ClientCallbackNames.CLOSED)
    async def on_closed(session: alluka.Injected[aiohttp.ClientSession]) -> None:
        await session.close()


def module_to_path(module_path):
    module = importlib.util.find_spec(module_path)
    path = module.submodule_search_locations[0]
    return path


def load_component(client: alluka.Injected[tanjun.abc.Client], component_config: ComponentConfig,
                   permission_class: typing.Type[AbstractComponentPermissions]):
    try:
        models_module = importlib.import_module(component_config.models_path)
    except ModuleNotFoundError:
        pass

    # Create the component and load the commmands into it
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


if __name__ == '__main__':
    start_bot()
