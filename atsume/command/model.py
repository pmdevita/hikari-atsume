import inspect
import logging
from collections.abc import Awaitable
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Generic,
    Optional,
    ParamSpec,
    Protocol,
    Sequence,
    Type,
    TypeVar,
    cast,
    get_args,
    overload,
)

import hikari
from hikari import (
    CommandInteraction,
    CommandInteractionOption,
    CommandOption,
    OptionType,
)
from hikari.api import SlashCommandBuilder
from pydantic import BaseModel, ConfigDict, GetPydanticSchema
from pydantic._internal._generics import PydanticGenericMetadata
from pydantic._internal._model_construction import ModelMetaclass

from atsume.command.annotations import HIKARI_TO_OPTION_TYPE
from atsume.command.context import CommandContext, Context, MessageContext
from atsume.command.exceptions import CommandNotFound
from atsume.utils.interactions import interaction_options_to_objects

if TYPE_CHECKING:
    from atsume.apps import AppConfig
    from atsume.apps.manager import ComponentManager

logger = logging.getLogger(__name__)


class CommandMetaclass(ModelMetaclass):
    def __new__(
        mcs,
        cls_name: str,
        bases: tuple[type[Any], ...],
        namespace: dict[str, Any],
        __pydantic_generic_metadata__: PydanticGenericMetadata | None = None,
        __pydantic_reset_parent_namespace__: bool = True,
        _create_model_module: str | None = None,
        **kwargs: Any,
    ) -> "CommandMetaclass | ModelMetaclass":
        if bases == (BaseModel,):
            return super().__new__(  # type: ignore
                mcs,
                cls_name,
                bases,
                namespace,
                __pydantic_generic_metadata__,
                __pydantic_reset_parent_namespace__,
                _create_model_module,
                **kwargs,
            )

        # Make the Optional fields None by default if they do not have a default
        for annotation_name, annotation in namespace.get("__annotations__", {}).items():
            args = get_args(annotation)
            if type(None) in args and annotation_name not in namespace:
                namespace[annotation_name] = None

        new_class: ModelMetaclass = cast(
            ModelMetaclass,
            super().__new__(
                mcs,
                cls_name,
                bases,
                namespace,
                __pydantic_generic_metadata__,
                __pydantic_reset_parent_namespace__,
                _create_model_module,
                **kwargs,
            ),
        )

        is_required = True
        # Check that there are no non-null fields after the first null field
        for field_name, field in new_class.model_fields.items():
            args = get_args(field.annotation)
            if type(None) in args:
                is_required = False
            elif is_required is False:
                raise Exception(
                    f'{new_class} has a required field "{field_name}" after an optional field.'
                )

        return new_class


class CommandModel(BaseModel, metaclass=CommandMetaclass):
    """
    A defined interface for use in a command. Arguments are defined in order as Pydantic fields.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)


ArgT = ParamSpec("ArgT")
CommandFunctionType = Callable[ArgT, Awaitable[None]]


class BaseCommand:
    def __init__(
        self,
        name: str,
        parent: "Optional[BaseCommand]" = None,
    ):
        self.name = name
        self.parent = parent

    @property
    def command_name(self) -> str:
        name = self.name
        if self.parent:
            name = f"{self.parent.command_name}_{name}"
        return name

    def _get_component(self) -> Optional["AppConfig"]:
        return self.parent._get_component()

    def as_option(self) -> hikari.CommandOption:
        """Represent this command as a CommandOption"""
        raise NotImplementedError()

    def get_suboptions(self) -> Optional[list[hikari.CommandOption]]:
        """This command's suboptions, representing its children. Should be used by as_option()."""
        return []

    def takes_context_type(self, ctx_class: type[Context]) -> bool:
        raise NotImplementedError()

    async def call_with_interaction(
        self,
        bot: "ComponentManager",
        interaction: CommandInteraction,
        options: Optional[Sequence[CommandInteractionOption]],
    ) -> CommandContext:
        raise NotImplementedError()

    async def call_with_args(
        self, bot: "ComponentManager", event: hikari.MessageCreateEvent, args: list[str]
    ) -> MessageContext:
        raise NotImplementedError()


class SubCallsMixin(BaseCommand):
    """A composable class for commands that have child nodes."""

    def __init__(
        self,
        name: str,
        parent: "Optional[BaseCommand]" = None,
    ):
        super().__init__(name, parent)
        self._subcommands: dict[str, "BaseCommand"] = {}

    def get_subcommand(self, command_args: list[str]) -> Optional["CommandMixin"]:
        # No way to go further, command or bust
        if len(command_args) == 0:
            if isinstance(self, CommandMixin):
                return self
            # Not a command, throw
            raise CommandNotFound(self.name)

        value, command_args = command_args[0], command_args[1:]

        try:
            # Can we go a layer further down?
            command = self._subcommands.get(value, None)

            # If we can't go deeper and if this was a callable command, return it
            if not command and isinstance(self, CommandMixin):
                return self

            # Try to resolve a command from the layer further down
            if isinstance(command, SubCallsMixin):
                return command.get_subcommand(command_args)

            # This isn't a command, and the subcommands couldn't find one either
            raise CommandNotFound()
        except CommandNotFound as e:
            e.prepend_command_word(value)
            raise e

    def as_option(self) -> hikari.CommandOption:
        cmd = CommandOption(
            type=OptionType.SUB_COMMAND_GROUP,
            name=self.name,
            description=f"Description of {self.name}",
            options=self.get_suboptions(),
        )

        return cmd

    def takes_context_type(self, ctx_class: type[Context]) -> bool:
        return any(
            [i.takes_context_type(ctx_class) for i in self._subcommands.values()]
        )

    def get_suboptions(self) -> list[hikari.CommandOption]:
        return [
            i.as_option()
            for i in self._subcommands.values()
            if i.takes_context_type(CommandContext)
        ]

    async def call_with_interaction(
        self,
        bot: "ComponentManager",
        interaction: CommandInteraction,
        options: Optional[Sequence[CommandInteractionOption]],
    ) -> CommandContext:
        if options is None:
            raise Exception("Call to command group with no further options?", options)

        if len(options) != 1:
            raise Exception("Call to command group with more than one option?", options)

        if (
            options[0].type == OptionType.SUB_COMMAND_GROUP
            or options[0].type == OptionType.SUB_COMMAND
        ):
            print("calling subgroup/subcommand", options[0])
            try:
                subcommand = self._subcommands[options[0].name]
            except KeyError:
                raise Exception(f"Unknown subcommand {options[0].name}")
            return await subcommand.call_with_interaction(
                bot, interaction, options[0].options
            )

        raise Exception(
            "Call to command group with one non-sub command option?", options
        )

    async def call_with_args(
        self, bot: "ComponentManager", event: hikari.MessageCreateEvent, args: list[str]
    ):
        if len(args) == 0:
            raise CommandNotFound(None)

        subcommand = self._subcommands.get(args[0], None)
        if subcommand is None:
            raise CommandNotFound(args[0])

        try:
            return await subcommand.call_with_args(bot, event, args[1:])
        except CommandNotFound as e:
            e.prepend_command_word(args[0])
            raise e


class HasSubCommandMixin(SubCallsMixin):
    """A composable class for commands that have a subcommand registered to them."""

    @overload
    def subcommand(self, name: CommandFunctionType[ArgT]) -> "SubCommand[ArgT]": ...

    @overload
    def subcommand(
        self, name: Optional[str] = None, description: Optional[str] = None
    ) -> "Callable[[CommandFunctionType[ArgT]], SubCommand[ArgT]]": ...

    def subcommand(
        self,
        name: Optional[str] | CommandFunctionType[ArgT] = None,
        description: Optional[str] = None,
    ) -> "SubCommand[ArgT] | Callable[[CommandFunctionType[ArgT]], SubCommand[ArgT]]":
        if callable(name):
            return SubCommand(name)

        def wrapper(func: CommandFunctionType[ArgT]) -> "SubCommand[ArgT]":
            command = SubCommand(func, name=name, description=description, parent=self)
            if command.name in self._subcommands:
                raise Exception(
                    f"{self} already has a subgroup or subcommand registered as name {command.name}."
                )

            self._subcommands[command.name] = command
            return command

        return wrapper


class HasSubGroupMixin(SubCallsMixin):
    """A composable class for commands that have a subgroup"""

    def subgroup(self, name: str) -> "SubGroup":
        group = SubGroup(name=name, parent=self)
        if group.name in self._subcommands:
            raise Exception(
                f"{self} already has a subgroup or subcommand registered as name {group.name}."
            )

        self._subcommands[group.name] = group
        return group


class CommandMixin(BaseCommand, Generic[ArgT]):
    """A composable class for callable commands. It wraps a user function to turn it into a command."""

    def __init__(
        self,
        func: CommandFunctionType[ArgT],
        name: Optional[str] = None,
        description: Optional[str] = None,
        parent: "Optional[BaseCommand]" = None,
    ):
        if not inspect.iscoroutinefunction(func):
            raise Exception(
                f"Command {name} with function name {func.__name__} is not an async function."
            )
        self.func = func

        if name is None:
            name = self.func.__name__

        super().__init__(name, parent)

        if description is None:
            description = f"Description of {self.name}"

        self.description = description

        signature = inspect.signature(self.func)
        context_model: list[Context] = []
        command_model: Optional[Type[CommandModel]] = None

        for param in signature.parameters.values():
            args = get_args(param.annotation)
            if args:
                # Is this a union of Contexts?
                if all([issubclass(i, Context) for i in args]):
                    context_model = list(args)
                continue
            if issubclass(param.annotation, Context):
                context_model = [param.annotation]

            if issubclass(param.annotation, CommandModel):
                if command_model is None:
                    command_model = param.annotation
                else:
                    raise Exception(
                        "Command is taking more than one CommandModel argument."
                    )

        self.command_model: Optional[Type[CommandModel]] = command_model
        self.context_model = context_model

    async def __call__(self, *args: ArgT.args, **kwargs: ArgT.kwargs) -> None:
        await self.func(*args, **kwargs)

    def as_option(self) -> CommandOption:
        cmd = CommandOption(
            type=OptionType.SUB_COMMAND,
            name=self.name,
            description=self.description,
            options=self.get_suboptions(),
        )

        return cmd

    def get_suboptions(self) -> Optional[list[hikari.CommandOption]]:
        return self.params_as_options() + super().get_suboptions()

    def params_as_options(self):
        options = []
        if self.command_model:
            for field_name, field in self.command_model.model_fields.items():
                options.append(
                    type_annotation_to_option(
                        field_name, field.description, field.annotation
                    )
                )
        return options

    async def call_with_interaction(
        self,
        bot: "ComponentManager",
        interaction: CommandInteraction,
        options: Optional[Sequence[CommandInteractionOption]],
    ) -> CommandContext:
        ctx = CommandContext(bot, interaction)
        if self.command_model:
            kwargs = await interaction_options_to_objects(bot.bot, interaction, options)
            options = self.command_model(**kwargs)
            await self(ctx, options)
        else:
            await self(ctx)
        return ctx

    async def call_with_args(
        self, bot: "ComponentManager", event: hikari.MessageCreateEvent, args: list[str]
    ) -> MessageContext:
        if not self.takes_context_type(MessageContext):
            raise CommandNotFound()

        kwargs = {}
        options = self.command_model(**kwargs)
        ctx = MessageContext(bot, event)

        component = self._get_component()
        if component and component.permissions:
            channel = await ctx.channel()
            if isinstance(channel, hikari.GuildChannel):
                if not await component.permissions.allow_in_guild(channel.guild_id):
                    logger.debug(f"Blocked command {command} due to permissions.")
                    return ctx
            else:
                if not await component.permissions.allow_in_dm():
                    logger.debug(f"Blocked command {command} due to permissions.")
                    return ctx

        await self(ctx, options)
        return ctx

    def takes_context_type(self, ctx_class: type[Context]) -> bool:
        return ctx_class in self.context_model


class RootCommand(SubCallsMixin, BaseCommand):
    """A composable class for a top level command node."""

    def __init__(
        self,
        name: str,
        parent: "Optional[BaseCommand]" = None,
    ):
        super().__init__(name, parent)
        self.component: Optional["AppConfig"] = None

    def _get_component(self) -> Optional["AppConfig"]:
        return self.component

    def as_command(self) -> SlashCommandBuilder:
        cmd = hikari.impl.SlashCommandBuilder(
            name=self.name, description=f"Description of {self.name}"
        )
        for option in self.get_suboptions():
            cmd.add_option(option)
        return cmd


class Command(
    CommandMixin[ArgT], RootCommand, HasSubGroupMixin, HasSubCommandMixin, BaseCommand
):
    def __init__(
        self,
        func: CommandFunctionType[ArgT],
        name: Optional[str] = None,
        description: Optional[str] = None,
    ):
        super().__init__(func, name, description, None)


class Group(RootCommand, HasSubGroupMixin, HasSubCommandMixin, BaseCommand):
    def __init__(self, name: str):
        super().__init__(name)


class SubCommand(CommandMixin[ArgT], BaseCommand):
    pass


class SubGroup(HasSubCommandMixin, BaseCommand):
    pass


def type_annotation_to_option(
    name: str, description: Optional[str], field_type: Any, is_required: bool = True
) -> CommandOption:
    args: Sequence[Any] = get_args(field_type)

    if len(args) == 0:
        # We've reached the bottom
        try:
            option_type = HIKARI_TO_OPTION_TYPE[field_type]
        except ValueError:
            raise Exception(
                f"Unable to map type {field_type} for Discord slash command."
            )

        if description is None:
            description = f"Description for {name}"

        return CommandOption(
            type=option_type,
            name=name,
            description=description,
            is_required=is_required,
        )

    # Filter out anything we don't need
    if len(args) > 1:
        new_args = []
        for a in args:
            # Optional type hint, isn't required
            if a is type(None):
                is_required = False
                continue

            if isinstance(a, GetPydanticSchema):
                continue

            new_args.append(a)

        args = new_args

    if len(args) > 1:
        raise Exception("Not sure what to do here", args)

    return type_annotation_to_option(name, description, args[0], is_required)


@overload
def command(name: CommandFunctionType[ArgT]) -> Command[ArgT]: ...


@overload
def command(
    name: Optional[str] = None, description: Optional[str] = None
) -> Callable[[CommandFunctionType[ArgT]], Command[ArgT]]: ...


def command(
    name: Optional[str] | CommandFunctionType[ArgT] = None,
    description: Optional[str] = None,
) -> Command[ArgT] | Callable[[CommandFunctionType[ArgT]], Command[ArgT]]:
    """Register a top level command."""
    if callable(name):
        return Command(name)

    def wrapper(func: CommandFunctionType[ArgT]) -> Command[ArgT]:
        return Command(func, name=name, description=description)

    return wrapper


EventType = TypeVar("EventType", bound=hikari.Event)


class EventHandlerProtocol(Protocol):
    async def __call__(self, bot: hikari.GatewayBot, event: EventType) -> None:
        pass


class Event:
    def __init__(self, func: EventHandlerProtocol) -> None:
        self.func = func
        signature = inspect.signature(self.func)
        event_parameter = list(signature.parameters.values())[1]
        self.event = event_parameter.annotation
        self.__name__ = func.__name__
        self.__signature__ = signature
        self.bot: Optional[hikari.GatewayBot] = None
        self.component: Optional["AppConfig"] = None

    async def __call__(self, *args, **kwargs) -> None:
        assert self.bot is not None
        await self.func(self.bot, *args, **kwargs)


def event(func: EventHandlerProtocol) -> Event:
    """Register an event handler."""
    return Event(func)
