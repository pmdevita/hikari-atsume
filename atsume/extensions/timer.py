import asyncio
import traceback
import typing
from datetime import datetime, timedelta
import weakref
from zoneinfo import ZoneInfo

import alluka
import hikari.events.guild_events
import tanjun
import logging

logger = logging.getLogger(__name__)

CallableArgs = typing.TypeVar("CallableArgs")
CallableKwargs = typing.TypeVar("CallableKwargs")


class TimerTask:
    def __init__(
        self,
        timer: "Timer",
        time: datetime,
        callback: typing.Callable[..., typing.Awaitable[None]],
        args: typing.Optional[list[CallableArgs]] = None,
        kwargs: typing.Optional[dict[str, CallableKwargs]] = None,
        repeat: typing.Optional[timedelta] = None,
    ) -> None:
        self.timer = timer
        self.time = time
        self._callback = callback
        self.repeat = repeat
        self._cancelled = False
        self._run = False
        self.args = args if args else []
        self.kwargs = kwargs if kwargs else {}

    async def callback(self) -> None:
        if self._cancelled:
            logger.warning(
                f"Callback was attempted on a cancelled task {self._callback}!"
            )

        if not self.repeat:
            self._run = True  # Done in case the running task wants to know if it should cancel it
        try:
            await self._callback(*self.args, **self.kwargs)
        except:
            print(traceback.format_exc())

        if self.repeat:
            self.time += self.repeat
            # Readd instead of recreate so API doesn't lose handler to the task
            self.timer._readd_task(self)

    @property
    def has_run(self) -> bool:
        return self._run

    def cancel(self) -> None:
        self._cancel()

    def _cancel(self, unregister: bool = True) -> None:
        if self._cancelled:
            logger.warning(f"Callback was cancelled twice {self._callback}!")
            return
        if self._run:
            logger.warning(f"Cancelling task that was already run {self._callback}!")
            return
        self._cancelled = True
        if unregister:
            self.timer.cancel(self)

    def __repr__(self) -> str:
        return f"TimerTask({self.time}, {self._callback})"

    def __bool__(self) -> bool:
        # This is so you can do if timer_obj and if it's true, cancel it
        return not self.has_run


class Timer:
    def __init__(self) -> None:
        self.tasks: list[TimerTask] = []
        self._current_timer: typing.Optional[asyncio.Task[None]] = None
        self._running_task: typing.Optional[asyncio.Task[None]] = None
        self._sort_task: typing.Optional[asyncio.Task[None]] = None
        self.timezone = datetime(2020, 1, 1, 1).astimezone().tzinfo
        self._has_started = False  # Wait until the bot has started to send off tasks

    def sort_tasks(self) -> None:
        if not self._has_started:
            return
        self._sort_task = asyncio.create_task(self._sort_tasks())

    async def _sort_tasks(self) -> None:
        """Resort tasks and reschedule the timer task with the newest time"""
        if not self.tasks:
            return

        self.tasks = sorted(self.tasks, key=lambda x: x.time)
        next_time = self.tasks[0].time
        if self._current_timer:
            self._current_timer.cancel()
        self._current_timer = asyncio.create_task(self._timer_job(next_time))
        self._needs_sort = False
        self._sort_task = None

    async def _timer_job(self, time: datetime) -> None:
        """Wait until the next task"""
        wait_time = time - datetime.now(self.timezone)
        wait_time_secs = wait_time.total_seconds()
        if wait_time_secs > 0:
            await asyncio.sleep(wait_time_secs)
        self._running_task = asyncio.create_task(self._run_jobs())
        self._current_timer = None

    async def _run_jobs(self) -> None:
        now = datetime.now(self.timezone)
        # Retrieve all tasks that need to be run
        # Bit awkward but avoids potentially unsafe getting of index 0
        jobs_to_run = []
        while True:
            if len(self.tasks) > 0:
                if self.tasks[0].time <= now:
                    jobs_to_run.append(self.tasks.pop(0))
                    continue
            break
        for job in jobs_to_run:
            try:
                await job.callback()
            except Exception as e:
                print(e)
        self.sort_tasks()
        self._running_task = None

    def schedule_task(
        self,
        time: datetime,
        callback: typing.Callable[..., typing.Awaitable[None]],
        args: typing.Optional[list[CallableArgs]] = None,
        kwargs: typing.Optional[dict[str, CallableKwargs]] = None,
        repeat: typing.Optional[timedelta] = None,
    ) -> TimerTask:
        if time.tzinfo is None:
            time = time.astimezone(self.timezone)

        if kwargs and args:
            callback(*args, **kwargs)

        task = TimerTask(self, time, callback, repeat=repeat, args=args, kwargs=kwargs)
        self.tasks.append(task)
        self.sort_tasks()
        return task

    def _readd_task(self, task: TimerTask) -> None:
        self.tasks.append(task)
        self._needs_sort = True
        self.sort_tasks()

    def cancel(self, task: TimerTask) -> None:
        self.tasks.remove(task)
        try:
            self.sort_tasks()
        except RuntimeError as e:
            print("Tried scheduling balancing after task cancel, got", e)

    def _start(self) -> None:
        if self._has_started:
            logger.warning("Timer was started again!")
            return
        self._has_started = True
        self.sort_tasks()

    async def close(self) -> None:
        while len(self.tasks):
            task = self.tasks.pop(0)
            task._cancel(unregister=False)


def hook_extension(c: tanjun.Client) -> None:
    c.set_type_dependency(Timer, Timer())

    @c.with_client_callback(tanjun.ClientCallbackNames.STARTED)
    async def on_started(timer: alluka.Injected[Timer]) -> None:
        timer._start()

    @c.with_client_callback(tanjun.ClientCallbackNames.CLOSING)
    async def on_closing(timer: alluka.Injected[Timer]) -> None:
        await timer.close()
