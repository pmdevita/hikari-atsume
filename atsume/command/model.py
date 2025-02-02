import dataclasses
import inspect
import re
from contextlib import contextmanager
from contextvars import ContextVar
from inspect import isfunction
from typing import (
    Any,
    TypedDict,
    Callable,
    TypeVar,
    ParamSpec,
    Generic,
    Optional,
    Type,
    get_args,
    cast,
    overload,
    Generator,
)


from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Generator

from hikari import GatewayBot, CommandOption, OptionType
from hikari.api import SlashCommandBuilder
from pydantic import BaseModel, ConfigDict, GetPydanticSchema
from pydantic._internal._generics import PydanticGenericMetadata
from pydantic._internal._model_construction import ModelMetaclass
from pydantic_async_validation import AsyncValidationModelMixin

from atsume.command.annotations import HIKARI_TO_OPTION_TYPE

_init_context_var = ContextVar("_init_context_var", default=None)


@contextmanager
def command_model_context(value: dict[str, Any]) -> Generator:
    token = _init_context_var.set(value)
    try:
        yield
    finally:
        _init_context_var.reset(token)


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
    ):
        if bases == (BaseModel,):
            return super().__new__(
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
        for annotation_name, annotation in namespace["__annotations__"].items():
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


class Command(Generic[ArgT]):
    def __init__(
        self,
        func: Callable[ArgT, None],
        name: Optional[str] = None,
        description: Optional[str] = None,
        parent: "Optional[Command]" = None,
    ):
        self.func = func
        self.subcommands = []
        self.parent = parent

        if name is None:
            name = self.func.__name__

        self.name = name

        if description is None:
            description = f"Description of {self.name}"

        self.description = description

        signature = inspect.signature(self.func)
        command_model: Optional[Type[CommandModel]] = None

        for param in signature.parameters.values():
            if issubclass(param.annotation, CommandModel):
                if command_model is None:
                    command_model = param.annotation
                else:
                    raise Exception(
                        "Command is taking more than one CommandModel argument."
                    )

        self.command_model: Optional[Type[CommandModel]] = command_model

    async def __call__(self, *args: ArgT.args, **kwargs: ArgT.kwargs) -> None:
        return await self.func(*args, **kwargs)

    def as_slash_command(self, bot: GatewayBot) -> SlashCommandBuilder:
        command_builder = bot.rest.slash_command_builder(self.name, self.description)

        for field_name, field in self.command_model.model_fields.items():
            option = type_annotation_to_option(
                field_name, field.description, field.annotation
            )
            command_builder.add_option(option)

        return command_builder

    @overload
    def subcommand(self, func: Callable[ArgT, None]) -> "Command[ArgT]":
        ...

    @overload
    def subcommand(
        self, name: Optional[str] = None, description: Optional[str] = None
    ) -> "Callable[[Callable[ArgT, None]], Command[ArgT]]":
        ...

    def subcommand(
        self, name: Optional[str] = None, description: Optional[str] = None
    ) -> "Command[ArgT] | Callable[[Callable[ArgT, None]], Command[ArgT]]":
        if isfunction(name):
            return Command(name)

        def wrapper(func: Callable[ArgT, None]) -> Command[ArgT]:
            command = Command(func, name=name, description=description, parent=self)
            self.subcommands.append(command)
            return command

        return wrapper


def type_annotation_to_option(
    name, description: Optional[str], field_type, is_required=True
):
    args = get_args(field_type)

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
            if a == type(None):
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
def command(func: Callable[ArgT, None]) -> Command[ArgT]:
    ...


@overload
def command(
    name: Optional[str] = None, description: Optional[str] = None
) -> Callable[[Callable[ArgT, None]], Command[ArgT]]:
    ...


def command(
    name: Optional[str] = None, description: Optional[str] = None
) -> Command[ArgT] | Callable[[Callable[ArgT, None]], Command[ArgT]]:
    if isfunction(name):
        return Command(name)

    def wrapper(func: Callable[ArgT, None]) -> Command[ArgT]:
        return Command(func, name=name, description=description)

    return wrapper
