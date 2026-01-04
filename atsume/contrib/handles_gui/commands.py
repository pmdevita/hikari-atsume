from functools import partial
from typing import Optional

import hikari
from hikari import Snowflake
from hikari.impl import SelectOptionBuilder

from atsume.command import CommandModel, command
from atsume.command.context import CommandContext, MessageContext
from atsume.components import (
    ActionRow,
    Button,
    ComponentModel,
    Container,
    InteractionContext,
    TextDisplay,
    TopLevelComponent,
)
from atsume.components.blocks import (
    Section,
    Separator,
    TextSelect,
    Thumbnail,
    UserSelect,
)


class Config(CommandModel):
    pass


class PanelTest(ComponentModel):
    clicks: int = 0
    message_index: int = 0
    selected_values: list[str] = []
    select_disabled: bool = False
    selected_user: Optional[int] = None

    def get_message(self, index: int) -> str:
        match index:
            case 0:
                return "This is the first message!"
            case 1:
                return "This is the second message!"
            case 2:
                return "This is the third message!"
            case 3:
                return "This is the fourth message!"

    async def render(self, bot: hikari.GatewayBot) -> list[TopLevelComponent]:
        selected_user_placeholder = "Select a user!"
        if self.selected_user:
            selected_user = await bot.rest.fetch_user(self.selected_user)
            selected_user_placeholder = f"Selected user: {selected_user.display_name}"

        return [
            Container(
                TextDisplay(self.get_message(self.message_index)),
                TextDisplay(f"# Button has been clicked {self.clicks} time(s)!"),
                ActionRow(
                    Button("First", partial(self.button_callback, 0)),
                    Button("Second", partial(self.button_callback, 1)),
                    Button("Third", partial(self.button_callback, 2)),
                    Button("Fourth", partial(self.button_callback, 3)),
                ),
            ),
            Separator(),
            ActionRow(Button("Toggle Select Disabled", self.toggle_select_disabled)),
            ActionRow(
                TextSelect(
                    self.string_select,
                    options=[
                        SelectOptionBuilder(
                            label="label",
                            value="value",
                            is_default="value" in self.selected_values,
                        ),
                        SelectOptionBuilder(
                            label="another option",
                            value="value2",
                            is_default="value2" in self.selected_values,
                        ),
                        SelectOptionBuilder(
                            label="third option",
                            value="value3",
                            is_default="value3" in self.selected_values,
                        ),
                    ],
                    placeholder="Select me!",
                    disabled=self.select_disabled,
                )
            ),
            Separator(spacing=Separator.Spacing.LARGE),
            Section(
                TextDisplay("hello there"),
                Thumbnail("https://placecats.com/millie/300/150"),
            ),
            ActionRow(
                UserSelect(self.user_select, placeholder=selected_user_placeholder)
            ),
        ]

    async def button_callback(self, ctx: InteractionContext, index: int) -> None:
        print("button callback")
        self.clicks += 1
        self.message_index = index

    async def string_select(self, ctx: InteractionContext, *values: str) -> None:
        print("string select callback", values)
        self.selected_values = list(values)
        self.clicks += 1

    async def toggle_select_disabled(self, ctx: InteractionContext) -> None:
        print("toggle select disabled callback")
        self.select_disabled = not self.select_disabled
        self.clicks += 1

    async def user_select(self, ctx: InteractionContext, *values: Snowflake) -> None:
        print("user select callback", values)
        self.selected_user = int(values[0]) if values else None
        self.clicks += 1


@command("panel_test")
async def panel_test(ctx: CommandContext | MessageContext, args: Config):
    await ctx.respond_with_component(PanelTest())
