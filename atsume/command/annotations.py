from typing import Annotated, Any

import hikari
from hikari import Snowflakeish, GatewayBot, OptionType
from pydantic import (
    BeforeValidator,
    GetCoreSchemaHandler,
    GetPydanticSchema,
    ValidationInfo,
)
from pydantic_core import CoreSchema, core_schema

# from pydantic_async_validation import ValidationInfo
from hikari.api import cache

from atsume.command.context import Context


def validate_member(tp, handler):
    def validate(
        value: Snowflakeish | hikari.Member, info: ValidationInfo
    ) -> hikari.Member:
        return value

    return core_schema.with_info_before_validator_function(
        validate, core_schema.int_schema()
    )


Member = Annotated[hikari.Member, GetPydanticSchema(validate_member)]


HIKARI_TO_OPTION_TYPE: dict[Any, OptionType] = {
    hikari.Member: OptionType.USER,
    hikari.GuildChannel: OptionType.CHANNEL,
    int: OptionType.INTEGER,
    float: OptionType.FLOAT,
    str: OptionType.STRING,
    bool: OptionType.BOOLEAN,
}
