import ormar
import typing
import inspect
from ormar.models.metaclass import ModelMetaclass as OrmarModelMetaclass
from atsume.component.manager import manager
from atsume.db.manager import database

if typing.TYPE_CHECKING:
    from atsume.component.component_config import ComponentConfig


class ModelMeta(ormar.ModelMeta):
    _qual_name: str
    component_config: "ComponentConfig"
    name: typing.Optional[str] = None
    plural_name: typing.Optional[str] = None

    @classmethod
    def get_name(cls) -> str:
        return cls.name if cls.name else cls._qual_name

    @classmethod
    def get_plural_name(cls) -> str:
        return cls.plural_name if cls.plural_name else f"{cls.get_name()}s"


class ModelMetaclass(OrmarModelMetaclass):
    @staticmethod
    def __new__(
        mcs: "ModelMetaclass",
        name: str,
        bases: typing.Any,
        attrs: dict[str, typing.Any],
    ) -> OrmarModelMetaclass:
        if attrs["__module__"] == "atsume.db.models":
            return super().__new__(mcs, name, bases, attrs)

        config = manager.get_config_from_models_path(attrs["__module__"])
        assert config is not None

        # If this model doesn't have a table name set, create one from the app name and its name
        if "Meta" not in attrs:

            class Meta(ModelMeta):
                _qual_name = attrs["__qualname__"].lower()

            attrs["Meta"] = Meta

        meta: ModelMeta = attrs["Meta"]

        if not hasattr(meta, "component_config"):
            meta.component_config = config

        if not hasattr(meta, "tablename"):
            meta.tablename = (
                f"{meta.component_config.name.lower()}_{meta.get_plural_name()}"
            )

        if not hasattr(meta, "database") and database.database:
            meta.database = database.database

        if not hasattr(meta, "metadata"):
            meta.metadata = config._model_metadata

        model_class = super().__new__(mcs, name, bases, attrs)
        config._models.append(model_class)
        return model_class


class Model(ormar.Model, metaclass=ModelMetaclass):
    pass
