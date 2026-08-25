from typing import Annotated, Type

import hikari
from hikari import OptionType, Snowflakeish
from pydantic import GetPydanticSchema, ValidationInfo
from pydantic_core import core_schema


def validate_member(tp, handler):
    def validate(
        value: Snowflakeish | hikari.Member, info: ValidationInfo
    ) -> hikari.Member:
        return value

    return core_schema.with_info_before_validator_function(
        validate, core_schema.int_schema()
    )


Member = Annotated[hikari.Member, GetPydanticSchema(validate_member)]


HIKARI_TO_OPTION_TYPE: dict[Type, OptionType] = {
    hikari.Member: OptionType.USER,
    hikari.GuildChannel: OptionType.CHANNEL,
    hikari.Role: OptionType.ROLE,
    int: OptionType.INTEGER,
    float: OptionType.FLOAT,
    str: OptionType.STRING,
    bool: OptionType.BOOLEAN,
}
