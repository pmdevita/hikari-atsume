import hikari
from hikari import StartedEvent, StoppingEvent

from atsume.command import event
from atsume.cron import cron

from .task import _task_manager


@event
async def _on_started(bot: hikari.GatewayBot, event: StartedEvent) -> None:
    await _task_manager.fetch_tasks()


@cron("*/5 * * * *")
async def _on_cron(bot: hikari.GatewayBot) -> None:
    await _task_manager.fetch_tasks()


@event
async def _on_stopping(bot: hikari.GatewayBot, event: StoppingEvent) -> None:
    await _task_manager.cancel_tasks()
