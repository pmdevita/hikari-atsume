from abc import abstractmethod

import hikari.components
from hikari.api import ComponentBuilder
from pydantic import BaseModel

from .blocks import (
    ActionRow,
    AtsumeComponent,
    Button,
    ButtonStyle,
    ChannelSelect,
    Container,
    MentionableSelect,
    RoleSelect,
    Section,
    SelectMenuOption,
    TextDisplay,
    TextSelect,
    Thumbnail,
    TopLevelComponent,
    UserSelect,
)
from .modal import ModalModel, TextInput

__all__ = [
    "ComponentModel",
    "AtsumeComponent",
    "Button",
    "ActionRow",
    "ButtonStyle",
    "SelectMenuOption",
    "TopLevelComponent",
    "Container",
    "TextDisplay",
    "TextInput",
    "ModalModel",
    "TextSelect",
    "UserSelect",
    "ChannelSelect",
    "RoleSelect",
    "MentionableSelect",
    "Section",
    "Thumbnail",
]


class ComponentModel(BaseModel):
    @abstractmethod
    def render(
        self, bot: hikari.GatewayBot
    ) -> TopLevelComponent | list[TopLevelComponent]:
        raise NotImplementedError()

    def build(self, bot: hikari.GatewayBot) -> list[ComponentBuilder]:
        components = self.render(bot)
        if not isinstance(components, list):
            components = [components]

        built = []
        for component in components:
            built.append(component.build(bot, self))
        return built


class InteractionContext:
    def __init__(self, interaction: hikari.ComponentInteractionCreateEvent):
        self.interaction = interaction

    def open_modal(self):
        pass
