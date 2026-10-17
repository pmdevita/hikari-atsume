import os
from typing import Optional, TypeVar, overload

EnvType = TypeVar("EnvType")


_MISSING = object()

@overload
def env(key: str) -> str: ...

@overload
def env(key: str, var_type: type[EnvType]) -> EnvType: ...

@overload
def env(key: str, *, default: str) -> str: ...

@overload
def env(key: str, var_type: type[EnvType], default: EnvType) -> EnvType: ...

def env(
    key: str, var_type: Optional[type[EnvType]] = None, default: EnvType | object = _MISSING
) -> EnvType | str:
    cast = var_type or str
    value = os.environ.get(key, default)
    if value is _MISSING:
        raise ValueError(f'Environment variable "{key}" is not set.')
    try:
        cast_value = cast(value)  # type: ignore[call-arg]
    except ValueError:
        raise ValueError(
            f'Cannot cast environment variable "{key}" value "{value}" into type {var_type}.'
        )
    return cast_value
