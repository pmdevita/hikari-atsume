import asyncio
from datetime import datetime
from random import randrange
from typing import Callable, Protocol
from zoneinfo import ZoneInfo

import hikari
from croniter import croniter
from hikari import StartedEvent, StoppingEvent

from atsume.apps.manager import manager
from atsume.settings import settings
from atsume.utils.async_utils import task_exception_wrapper

MAX_WAIT_TIME = 60 * 60 * 6  # 6 Hours


class InvalidCronExpression(ValueError):
    def __init__(self, exp: str) -> None:
        super().__init__(f"{exp} is an invalid cron expression.")


class CronFuncProtocol(Protocol):
    async def __call__(self, bot: hikari.GatewayBot) -> None: ...


class ScheduleManager:
    def __init__(self):
        self.crons = []
        self.tasks = []
        self.has_started = False
        manager.bot.event_manager.subscribe(StartedEvent, self.queue_crons)
        manager.bot.event_manager.subscribe(StoppingEvent, self.cancel_crons)

    def add_cron(self, exp: str, func: CronFuncProtocol) -> None:
        self.crons.append((exp, func))
        if self.has_started:
            self.tasks.append(run_cron_task(exp, func))

    async def queue_crons(self, event: StartedEvent) -> None:
        if self.has_started:
            return
        for cron in self.crons:
            self.tasks.append(asyncio.create_task(run_cron_task(cron[0], cron[1])))
        self.has_started = True

    async def cancel_crons(self, event: StoppingEvent) -> None:
        for task in self.tasks:
            task.cancel()


@task_exception_wrapper
async def run_cron_task(exp: str, func):
    target = datetime.now(ZoneInfo(settings.TIMEZONE)).timestamp()
    iter = croniter(exp, start_time=target)
    while True:
        target = iter.next(float)
        now = datetime.now(ZoneInfo(settings.TIMEZONE)).timestamp()

        # Periodically wake up and resleep to avoid clock drift
        while now < target:
            remaining_time = target - now
            # Jitter time to avoid thundering herd
            await asyncio.sleep(min(MAX_WAIT_TIME + randrange(-10, 10), remaining_time))
            now = datetime.now(ZoneInfo(settings.TIMEZONE)).timestamp()

        await task_exception_wrapper(func)(manager.bot)


_schedule = ScheduleManager()


def cron(cron_expression: str) -> Callable[[CronFuncProtocol], CronFuncProtocol]:
    if not croniter.is_valid(cron_expression, strict=True):
        raise InvalidCronExpression(cron_expression)

    def wrapper(f: CronFuncProtocol) -> CronFuncProtocol:
        _schedule.add_cron(cron_expression, f)
        return f

    return wrapper
