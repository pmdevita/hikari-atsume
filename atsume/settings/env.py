import os
from typing import Optional, TypeVar

EnvType = TypeVar("EnvType")


def env(
    key: str, var_type: type[EnvType] = str, default: Optional[EnvType] = ...
) -> EnvType:
    value = os.environ.get(key, default)
    if value is ...:
        raise ValueError(f'Environment variable "{key}" is not set.')
    try:
        cast_value = var_type(value)
    except ValueError:
        raise ValueError(
            f'Cannot cast environment variable "{key}" value "{value}" into type {var_type}.'
        )
    return cast_value
