import dataclasses
from typing import Any, Optional

import hikari
from hikari import TextInputStyle, UndefinedOr, undefined
from hikari.impl import TextInputBuilder


class ModalModelMetaclass(type):
    def __new__(
        mcs,
        cls_name: str,
        bases: tuple[type[Any], ...],
        namespace: dict[str, Any],
        **kwargs: Any,
    ) -> "ModalModel | type":
        if bases == ():
            return super().__new__(mcs, cls_name, bases, namespace, **kwargs)

        annotations = namespace.get("__annotations__", {})

        fields = []
        for field_name, field in namespace.items():
            if field_name.startswith("_"):
                continue

            if not isinstance(field, TextInput):
                raise ValueError(
                    f"Field {field_name} on ModalModel {cls_name} is not a TextInput"
                )

            annotation = annotations.get(field_name)
            if not (annotation == str or annotation == Optional[str]):
                raise ValueError(
                    f"Field {field_name} on ModalModel {cls_name} must have either a str or Optional[str] annotation."
                )

            field.id = field_name
            field.required = annotation == str
            fields.append(field)
        namespace["_fields"] = fields

        return super().__new__(mcs, cls_name, bases, namespace, **kwargs)


class ModalModel(metaclass=ModalModelMetaclass):
    _fields: list["TextInput"]

    def build(self, bot: hikari.GatewayBot):
        components = []
        for field in self._fields:
            components.append(
                TextInputBuilder(
                    custom_id=field.id,
                    label=field.label or field.id,
                    required=field.required,
                    min_length=field.min_length,
                    max_length=field.max_length,
                    placeholder=field.placeholder,
                )
            )
        return components


@dataclasses.dataclass
class TextInput:
    label: Optional[str] = (None,)
    style: TextInputStyle = (TextInputStyle.SHORT,)
    min_length: Optional[int] = (None,)
    max_length: Optional[int] = (None,)
    value: UndefinedOr[str] = (undefined.UNDEFINED,)
    placeholder: UndefinedOr[str] = undefined.UNDEFINED

    def __get__(self, instance, owner):
        pass
