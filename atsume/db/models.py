import dataclasses

import ormar
import typing

from ormar import OrmarConfig
from ormar.models.helpers import merge_or_generate_pydantic_config
from ormar.models.metaclass import ModelMetaclass as OrmarModelMetaclass
from pydantic._internal._generics import PydanticGenericMetadata

from atsume.component.manager import manager
from atsume.db.manager import database

if typing.TYPE_CHECKING:
    from atsume.component.component_config import ComponentConfig


@dataclasses.dataclass
class AtsumeConfig:
    qual_name: str
    component_config: "ComponentConfig"
    name: typing.Optional[str] = None
    plural_name: typing.Optional[str] = None

    def get_name(self) -> str:
        return self.name if self.name else self.qual_name

    def get_plural_name(self) -> str:
        return self.plural_name if self.plural_name else f"{self.get_name()}s"

    def get_default_table_name(self) -> str:
        return f"{self.component_config.name.lower()}_{self.get_plural_name()}"


class OrmarAttrs(dict[str, typing.Any]):
    """Ormar currently sets (not appends) ignored_types so we need to stop it from doing that"""

    def __getitem__(self, item: str) -> typing.Any:
        if item == "model_config":
            return super().__getitem__(item).copy()
        return super().__getitem__(item)

    def __setitem__(self, key: str, value: typing.Any) -> None:
        if key == "model_config":
            return
        super().__setitem__(key, value)


class ModelMetaclass(OrmarModelMetaclass):
    """
    A subclass of the Ormar ModelMetaclass. Adds and configures some extra properties during
    Model class creation.
    """

    def __new__(  # type: ignore # noqa: CCR001
        mcs: "ModelMetaclass",
        name: str,
        bases: typing.Any,
        attrs: dict[str, typing.Any],
        __pydantic_generic_metadata__: typing.Union[
            PydanticGenericMetadata, None
        ] = None,
        __pydantic_reset_parent_namespace__: bool = True,
        _create_model_module: typing.Union[str, None] = None,
        **kwargs,
    ) -> type:
        # This condition is true when the Atsume ModelMetaclass itself is being created.
        # Since this isn't a normal model class creation, many properties are missing so
        # the rest of this should be skipped.
        if attrs["__module__"] == "atsume.db.models":
            return super().__new__(mcs, name, bases, attrs)

        # Get the component config for the component this model belongs to.
        config = manager.get_config_from_models_path(attrs["__module__"])
        assert config is not None

        qual_name = attrs["__qualname__"].lower()

        # If this model doesn't have a Meta class property, create it
        if "atsume_config" not in attrs:
            atsume_config = AtsumeConfig(qual_name, config)
            attrs["atsume_config"] = atsume_config
        else:
            atsume_config = attrs["atsume_config"]
            if not isinstance(atsume_config, AtsumeConfig):
                raise Exception(
                    f"Model {name}'s atsume_config property needs to be an AtsumeConfig instance."
                )

        atsume_config.qual_name = attrs["__qualname__"].lower()
        atsume_config.component_config = config

        if "ormar_config" not in attrs:
            ormar_config = OrmarConfig()
            attrs["ormar_config"] = ormar_config
        else:
            ormar_config = attrs["ormar_config"]

        if ormar_config.tablename is None:
            ormar_config.tablename = atsume_config.get_default_table_name()

        if database.database:
            ormar_config.database = database.database

        ormar_config.metadata = config._model_metadata

        # Since we are blocking Ormar from touching the model_config,
        # we need to perform some operations for it
        merge_or_generate_pydantic_config(attrs, name)
        attrs["model_config"]["ignored_types"] = attrs["model_config"].get(
            "ignored_types", tuple()
        ) + (OrmarConfig, AtsumeConfig)
        attrs["model_config"]["from_attributes"] = True

        model_class = typing.cast(
            ModelMetaclass,
            super().__new__(
                mcs,
                name,
                bases,
                OrmarAttrs(attrs),
                __pydantic_generic_metadata__,
                __pydantic_reset_parent_namespace__,
                _create_model_module,
                **kwargs,
            ),
        )
        config._models.append(model_class)
        return model_class


class Model(ormar.Model, metaclass=ModelMetaclass):
    """Class to compose the Ormar Model class with Atsume's custom ModelMetaclass"""

    pass
