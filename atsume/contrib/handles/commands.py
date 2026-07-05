from functools import partial
from typing import Optional

import hikari
from hikari.impl import SelectOptionBuilder

from atsume.command.context import CommandContext
from atsume.component.manager import manager
from atsume.components import (
    ActionRow,
    Button,
    ComponentModel,
    Container,
    InteractionContext,
    Separator,
    TextDisplay,
    TextSelect,
    TopLevelComponent,
)

from ...command import command
from .models import ComponentGuild, ComponentSafetyException

# Create your commands here.


class GuildsConfigPanel(ComponentModel):
    selected_component: Optional[str] = None
    messages: list[str] = []

    async def render(
        self, bot: hikari.GatewayBot
    ) -> TopLevelComponent | list[TopLevelComponent]:
        panel: list[TopLevelComponent] = [
            ActionRow(
                TextSelect(
                    self.component_select,
                    options=[
                        SelectOptionBuilder(
                            c.verbose_name,
                            c.name,
                            is_default=c.name == self.selected_component,
                        )
                        for c in manager.component_configs
                    ],
                    placeholder="Select a component",
                )
            )
        ]

        if self.messages:
            for m in self.messages:
                panel.insert(0, TextDisplay(f"❌ {m}"))
            self.messages = []

        if self.selected_component:
            # Is this component in global whitelist or blacklist mode?
            is_enabled = await ComponentGuild.get_global_mode(self.selected_component)

            # Get state for guilds
            guild_models = await ComponentGuild.get_guilds(self.selected_component)
            guild_state = {model.guild_id: model.mode for model in guild_models}

            guilds = await manager.bot.rest.fetch_my_guilds()

            guild_options = []
            verbose_name = [
                c.verbose_name
                for c in manager.component_configs
                if c.name == self.selected_component
            ][0]
            for guild in guilds:
                guild_mode = "Default"
                if guild.id in guild_state:
                    guild_mode = "Enabled" if guild_state[guild.id] else "Disabled"
                guild_options.append(
                    SelectOptionBuilder(f"{guild.name} ({guild_mode})", str(guild.id))
                )

            panel.extend(
                [
                    Separator(),
                    Container(
                        TextDisplay(
                            f"By default, {verbose_name} is **{"Enabled" if is_enabled else "Disabled"}** globally."
                        ),
                        ActionRow(
                            Button(
                                "Toggle Global Mode",
                                partial(
                                    self.toggle_global_mode,
                                    self.selected_component,
                                    not is_enabled,
                                ),
                            )
                        ),
                        ActionRow(
                            TextSelect(
                                partial(self.toggle_guild, self.selected_component),
                                options=guild_options,
                                placeholder="Guild Overrides",
                                min_values=0,
                                max_values=len(guild_options),
                            )
                        ),
                    ),
                ]
            )

        return panel

    async def component_select(
        self, ctx: InteractionContext, value: Optional[str] = None
    ) -> None:
        self.selected_component = value

    async def toggle_global_mode(
        self, ctx: InteractionContext, component_name: str, to_whitelist: bool
    ) -> None:
        if self.selected_component != component_name:
            return
        ensure_guild_id = None
        if component_name == "handles":
            ensure_guild_id = ctx.interaction.interaction.guild_id
        try:
            await ComponentGuild.set_global_mode(
                component_name, to_whitelist, ensure_guild_id=ensure_guild_id
            )
        except ComponentSafetyException as e:
            self.messages.append(str(e))

    async def toggle_guild(
        self, ctx: InteractionContext, component_name: str, guild_id: str
    ) -> None:
        if self.selected_component != component_name:
            return
        try:
            await ComponentGuild.toggle_guild(
                component_name,
                int(guild_id),
                block_inaccess=(
                    component_name == "handles"
                    and ctx.interaction.interaction.guild_id == int(guild_id)
                ),
            )
        except ComponentSafetyException as e:
            self.messages.append(str(e))


@command("config")
async def config(ctx: CommandContext) -> None:
    await ctx.respond_with_component(GuildsConfigPanel(), ephemeral=True)
