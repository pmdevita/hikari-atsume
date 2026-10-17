from datetime import datetime
from importlib import import_module

from hikari import Snowflake
from piccolo.columns import JSON, BigInt, Serial, Timestamp, Varchar
from piccolo.table import Table

from atsume.components import ComponentModel


class WindowState(Table):
    id: int = Serial(primary_key=True)
    message_id: int = BigInt()
    module_path: str = Varchar()
    component_class: str = Varchar()
    window_state: dict = JSON()
    modified_date: datetime = Timestamp(auto_update=datetime.now)

    def deserialize_to_component(self) -> ComponentModel:
        component_module = import_module(self.module_path)
        component_class: ComponentModel = getattr(
            component_module,
            self.component_class,
        )

        component = component_class.model_validate_json(self.window_state)
        return component

    @classmethod
    async def serialize_from_component(
        cls, message_id: Snowflake, component: ComponentModel
    ) -> "WindowState":
        defaults = {
            WindowState.message_id: message_id,
            WindowState.module_path: component.__class__.__module__,
            WindowState.component_class: component.__class__.__name__,
            WindowState.window_state: component.model_dump(),
        }

        model = await cls.objects().get_or_create(
            WindowState.message_id == message_id, defaults=defaults
        )
        if not model._was_created:
            await model.update_self(defaults)

        return model
