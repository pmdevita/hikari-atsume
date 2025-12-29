import json
from typing import TYPE_CHECKING

import hikari
from hikari import ResponseType

from atsume.components import ComponentModel, InteractionContext

if TYPE_CHECKING:
    from atsume.component.manager import ComponentManager as TopManager


class ComponentManager:
    def __init__(self, manager: "TopManager"):
        self.manager = manager
        self.bot = self.manager.bot
        self.windows: dict[hikari.Snowflake, ComponentModel] = {}
        print("subbed")
        self.bot.subscribe(
            hikari.ComponentInteractionCreateEvent, self._on_component_interaction
        )

    def register_component(self, message_id, model):
        self.windows[message_id] = model

    async def _on_component_interaction(
        self, event: hikari.ComponentInteractionCreateEvent
    ):
        print("interaction!")
        message = event.interaction.message
        window = self.windows.get(message.id, None)
        if not window:
            print("No window model instance found")
            return

        callback = json.loads(event.interaction.custom_id)
        if not hasattr(window, callback["f"]):
            print(f"Window doesn't have func {callback["f"]}???")
            return

        print("fields_set", window.model_fields_set)

        interaction_ctx = InteractionContext(event)

        if callback.get("a", None) or callback.get("k", None):
            await getattr(window, callback["f"])(
                interaction_ctx, *callback.get("a", ()), **callback.get("k", {})
            )
        else:
            await getattr(window, callback["f"])(
                interaction_ctx, *event.interaction.values
            )
        rendered = window.build(self.bot)
        # await event.interaction.message.edit(component=rendered)
        await event.interaction.create_initial_response(
            response_type=ResponseType.MESSAGE_UPDATE, components=rendered
        )

        # await event.interaction.edit_initial_response(component=rendered)
        print("updated!")
