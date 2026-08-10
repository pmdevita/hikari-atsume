import inspect
import json
from abc import abstractmethod, ABC
from enum import Enum
from functools import partial
from typing import TYPE_CHECKING, Optional, Protocol, Union, overload, Any

import hikari
from hikari import SelectMenuOption, colors, emojis, files, undefined, UndefinedType
from hikari.api import ComponentBuilder
from hikari.components import ButtonStyle, ComponentType, SpacingType
from hikari.impl import (
    ContainerComponentBuilder,
    InteractiveButtonBuilder,
    MessageActionRowBuilder,
    SectionComponentBuilder,
    SelectMenuBuilder,
    SelectOptionBuilder,
    SeparatorComponentBuilder,
    TextDisplayComponentBuilder,
    TextSelectMenuBuilder,
    ThumbnailComponentBuilder,
)

if TYPE_CHECKING:
    from atsume.components import ComponentModel


__all__ = [
    "Button",
    "TextDisplay",
    "Container",
    "ActionRow",
    "Thumbnail",
    "AtsumeComponent",
    "TopLevelComponent",
    "ButtonStyle",
    "SelectMenuOption",
]


class AtsumeComponent(ABC):
    @abstractmethod
    def build(
        self, bot: hikari.GatewayBot, model: "ComponentModel"
    ) -> ComponentBuilder:
        pass


class ComposableComponent(AtsumeComponent):
    pass


class TopLevelComponent(AtsumeComponent):
    pass


class CallbackComponent(AtsumeComponent):
    def __init__(self, callback: "CallbackProtocol", *args: Any, **kwargs: Any) -> None:
        if not inspect.iscoroutinefunction(callback):
            raise Exception(f"Callback for {self} must be async")

        self.callback = callback

    def get_callback_name(self, model: "ComponentModel") -> str:
        data: dict[str, Any] = {}
        obj = self.callback
        # Destructure partials
        if isinstance(self.callback, partial):
            data["a"] = self.callback.args
            data["k"] = self.callback.keywords
            obj = self.callback.func
        # or check if callable
        elif callable(self.callback):
            obj = self.callback
        if getattr(obj, "__self__", None) != model:
            raise Exception(
                "Component callback must be a method on the ComponentModel."
            )
        # Functions have names mypy?
        data["f"] = obj.__name__  # type: ignore[attr-defined]
        return json.dumps(data, separators=(",", ":"))


class SelectComponent(CallbackComponent, AtsumeComponent):
    TYPE: ComponentType

    def __init__(
        self,
        callback: "CallbackProtocol",
        placeholder: str | UndefinedType = undefined.UNDEFINED,
        min_values: int = 0,
        max_values: int = 1,
        disabled: bool = False,
    ) -> None:
        super().__init__(callback)
        self.placeholder = placeholder
        self.min_values = min_values
        self.max_values = max_values
        self.disabled = disabled

    def build(
        self, bot: hikari.GatewayBot, model: "ComponentModel"
    ) -> SelectMenuBuilder:
        component = SelectMenuBuilder(
            type=ComponentType.USER_SELECT_MENU,
            custom_id=self.get_callback_name(model),
            placeholder=self.placeholder,
            min_values=self.min_values,
            max_values=self.max_values,
            is_disabled=self.disabled,
        )
        return component


class CallbackProtocol(Protocol):
    async def __call__(self) -> None:
        pass


class CallbackValueProtocol(Protocol):
    async def __call__(self, value: str) -> None:
        pass


class Button(CallbackComponent, AtsumeComponent):
    def __init__(
        self,
        label: str,
        callback: CallbackProtocol,
        emoji: emojis.Emoji | UndefinedType = undefined.UNDEFINED,
        style: ButtonStyle = ButtonStyle.PRIMARY,
        disabled: bool = False,
    ) -> None:
        super().__init__(callback=callback)
        self.label = label
        self.emoji = emoji
        self.style = style
        self.disabled = disabled

    def build(
        self, bot: hikari.GatewayBot, model: "ComponentModel"
    ) -> InteractiveButtonBuilder:
        builder = InteractiveButtonBuilder(
            style=self.style,
            custom_id=self.get_callback_name(model),
            label=self.label,
            emoji=self.emoji,
            is_disabled=self.disabled,
        )
        return builder


class TextSelect(CallbackComponent, AtsumeComponent):
    def __init__(
        self,
        callback: CallbackProtocol,
        options: list[SelectOptionBuilder],
        placeholder: str | UndefinedType = undefined.UNDEFINED,
        min_values: int = 0,
        max_values: int = 1,
        disabled: bool = False,
    ) -> None:
        super().__init__(callback)
        self.options = options
        self.placeholder = placeholder
        self.min_values = min_values
        self.max_values = max_values
        self.disabled = disabled

    def build(
        self, bot: hikari.GatewayBot, model: "ComponentModel"
    ) -> ComponentBuilder:
        component = TextSelectMenuBuilder(
            custom_id=self.get_callback_name(model),
            placeholder=self.placeholder,
            min_values=self.min_values,
            max_values=self.max_values,
            is_disabled=self.disabled,
            options=self.options,
        )
        return component


class UserSelect(SelectComponent, AtsumeComponent):
    TYPE = ComponentType.USER_SELECT_MENU


class ChannelSelect(SelectComponent, AtsumeComponent):
    TYPE = ComponentType.CHANNEL_SELECT_MENU


class RoleSelect(SelectComponent, AtsumeComponent):
    TYPE = ComponentType.ROLE_SELECT_MENU


class MentionableSelect(SelectComponent, AtsumeComponent):
    TYPE = ComponentType.MENTIONABLE_SELECT_MENU


class TextDisplay(AtsumeComponent):
    def __init__(self, content: str) -> None:
        self.content = content

    def build(
        self, bot: hikari.GatewayBot, model: "ComponentModel"
    ) -> TextDisplayComponentBuilder:
        return TextDisplayComponentBuilder(content=self.content)


class Thumbnail(AtsumeComponent):
    def __init__(
        self,
        media: files.Resourceish,
        description: undefined.UndefinedOr[str] = undefined.UNDEFINED,
        spoiler: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
    ) -> None:
        self.media = media
        self.description = description
        self.spoiler = spoiler

    def build(
        self, bot: hikari.GatewayBot, model: "ComponentModel"
    ) -> ThumbnailComponentBuilder:
        builder = ThumbnailComponentBuilder(
            media=self.media, description=self.description
        )
        return builder


class ActionRow(TopLevelComponent, AtsumeComponent):
    @overload
    def __init__(self, component: Button, /) -> None: ...

    @overload
    def __init__(self, component: Button, component2: Button, /) -> None: ...

    @overload
    def __init__(
        self, component: Button, component2: Button, component3: Button, /
    ) -> None: ...

    @overload
    def __init__(
        self,
        component: Button,
        component2: Button,
        component3: Button,
        component4: Button,
        /
    ) -> None: ...

    @overload
    def __init__(
        self,
        component: Button,
        component2: Button,
        component3: Button,
        component4: Button,
        component5: Button,
        /
    ) -> None: ...

    @overload
    def __init__(self, component: SelectComponent, /) -> None: ...

    def __init__(self, *components: Button | SelectComponent) -> None:
        """

        :param components: 1-5 Buttons, or 1 SelectComponent.
        """
        self.components = components

    def build(
        self, bot: hikari.GatewayBot, model: "ComponentModel"
    ) -> MessageActionRowBuilder:
        builder = MessageActionRowBuilder(components=[])
        for component in self.components:
            builder.add_component(component.build(bot, model))
        return builder


class Container(TopLevelComponent, AtsumeComponent):
    def __init__(
        self,
        *components: ActionRow | TextDisplay,
        accent_color: undefined.UndefinedOr[colors.Color] = undefined.UNDEFINED,
        spoiler: bool = False,
    ):
        self.components = components
        self.accent_color = accent_color
        self.spoiler = spoiler

    def build(
        self, bot: hikari.GatewayBot, model: "ComponentModel"
    ) -> ContainerComponentBuilder:
        builder = ContainerComponentBuilder(
            components=[], accent_color=self.accent_color, spoiler=self.spoiler
        )
        for component in self.components:
            builder.add_component(component.build(bot, model))
        return builder


class Section(TopLevelComponent, AtsumeComponent):
    @overload
    def __init__(
        self, component: TextDisplay, accessory: Button | Thumbnail, /
    ) -> None: ...

    @overload
    def __init__(
        self,
        component: TextDisplay,
        component2: TextDisplay,
        accessory: Button | Thumbnail,
        /
    ) -> None: ...

    @overload
    def __init__(
        self,
        component: TextDisplay,
        component2: TextDisplay,
        component3: TextDisplay,
        accessory: Button | Thumbnail,
        /
    ) -> None: ...

    def __init__(self, *components: TextDisplay | Button | Thumbnail) -> None:
        self.components: list[TextDisplay] = []
        accessory = None

        for component in components:
            if isinstance(component, (Button, Thumbnail)):
                if accessory is not None:
                    raise Exception("Section can only have one accessory.")
                accessory = component
            else:
                self.components.append(component)
                if len(self.components) > 3:
                    raise Exception(
                        "Section can only have up to 3 TextDisplay components."
                    )

        if accessory is None:
            raise Exception("Section must have an accessory (Button or Thumbnail).")

        self.accessory = accessory

    def build(
        self, bot: hikari.GatewayBot, model: "ComponentModel"
    ) -> ComponentBuilder:
        return SectionComponentBuilder(
            components=[component.build(bot, model) for component in self.components],
            accessory=self.accessory.build(bot, model),
        )


class Separator(TopLevelComponent, AtsumeComponent):
    class Spacing(Enum):
        SMALL = 1
        LARGE = 2

    def __init__(self, divider: bool = True, spacing: Spacing = Spacing.SMALL) -> None:
        self.divider = divider
        self.spacing = spacing

    def build(
        self, bot: hikari.GatewayBot, model: "ComponentModel"
    ) -> ComponentBuilder:
        return SeparatorComponentBuilder(
            divider=self.divider, spacing=SpacingType(self.spacing.value)
        )


class Label(TopLevelComponent, AtsumeComponent):
    def __init__(
        self, label: str, component: SelectComponent, description: Optional[str] = None
    ) -> None:
        self.label = label
        self.description = description
        self.component = component

    def build(
        self, bot: hikari.GatewayBot, model: "ComponentModel"
    ) -> ComponentBuilder:
        builder = TextDisplayComponentBuilder(content=self.label)
        return builder
