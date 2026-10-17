import asyncio
import json
import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable, Generic, Optional, ParamSpec, TypeVar, overload
from zoneinfo import ZoneInfo

from atsume.contrib.schedule.models import ScheduledTask
from atsume.settings import settings
from atsume.utils.async_utils import task_exception_wrapper

ParamT = ParamSpec("ParamT")
Result = TypeVar("Result")


logger = logging.getLogger(__name__)


SCHEDULE_FETCH_AHEAD = getattr(settings, "SCHEDULE_FETCH_AHEAD", 300)


def get_function_path(func: Callable[Any]) -> str:
    return func.__module__ + "." + func.__name__


class TaskManager:
    def __init__(self):
        self.tasks: dict[int, asyncio.Task[Any]] = {}
        self.path_registry: dict[str, Callable[..., Any]] = {}
        self.name_registry: dict[str, Callable[..., Any]] = {}

    def register_task(self, func: Callable[..., Any], name: Optional[str] = None):
        path = get_function_path(func)
        self.path_registry[path] = func
        if name:
            self.name_registry[name] = func

    def get_cutoff(self):
        return datetime.now(tz=ZoneInfo("UTC")) + timedelta(
            seconds=SCHEDULE_FETCH_AHEAD
        )

    async def fetch_tasks(self):
        tasks = await ScheduledTask.objects().where(
            ScheduledTask.scheduled_date <= self.get_cutoff(),
            ScheduledTask.status == ScheduledTask.Status.SCHEDULED,
        )

        for task in tasks:
            if task.id in self.tasks:
                continue
            task_func = self.get_task(task)
            if not task_func:
                continue
            async_task = asyncio.create_task(
                self.run_task(
                    task.id, task.scheduled_date, task_func, task.args, task.kwargs
                )
            )
            self.tasks[task.id] = async_task

    async def schedule_task(self, task: "Task", dt: datetime) -> None:
        scheduled_task = await ScheduledTask.objects().create(
            task_name=task.name,
            task_path=task.path,
            scheduled_date=dt,
            status=ScheduledTask.Status.SCHEDULED,
            args=task.args,
            kwargs=task.kwargs,
        )
        if dt <= self.get_cutoff() and scheduled_task.id not in self.tasks:
            async_task = asyncio.create_task(
                self.run_task(scheduled_task.id, dt, task.func, task.args, task.kwargs)
            )
            self.tasks[scheduled_task.id] = async_task

    @task_exception_wrapper
    async def run_task(
        self, id: int, dt: datetime, func: Callable[..., Any], args: Any, kwargs: Any
    ) -> None:
        delta = dt - (datetime.now(ZoneInfo("UTC")))
        args_obj = json.loads(args)
        kwargs_obj = json.loads(kwargs)

        await asyncio.sleep(delta.total_seconds())
        await task_exception_wrapper(func)(*args_obj, **kwargs_obj)
        await ScheduledTask.update(
            {ScheduledTask.status: ScheduledTask.Status.COMPLETE}
        ).where(ScheduledTask.id == id)
        self.tasks.pop(id)

    def get_task(self, db_task: ScheduledTask) -> Optional[Callable[..., Any]]:
        task_func = None
        if db_task.task_name:
            task_func = self.name_registry.get(db_task.task_name)
        if task_func is None:
            task_func = self.name_registry.get(db_task.task_path)
        if task_func is None:
            logger.warning(
                f"ScheduledTask {db_task}'s function cannot be found, task cannot be scheduled!"
            )
        return task_func

    async def cancel_tasks(self) -> None:
        for id in list(self.tasks.keys()):
            task = self.tasks.pop(id)
            task.cancel()


_task_manager = TaskManager()


class Task(Generic[ParamT, Result]):
    def __init__(
        self,
        func: Callable[ParamT, Result],
        args: ParamT.args,
        kwargs: ParamT.kwargs,
        name: Optional[str] = None,
    ) -> None:
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.name = name
        self.path = get_function_path(func)

    async def run(self) -> Result:
        return self.func(*self.args, **self.kwargs)

    async def schedule(self, dt: datetime) -> None:
        await _task_manager.schedule_task(self, dt)


@overload
def task(func: Callable[ParamT, Result]) -> Callable[ParamT, Task[ParamT, Result]]: ...


@overload
def task(
    func: str,
) -> Callable[[Callable[ParamT, Result]], Callable[ParamT, Task[ParamT, Result]]]: ...


def task(
    func: Callable[ParamT, Result] | str,
) -> (
    Callable[ParamT, Task[ParamT, Result]]
    | Callable[[Callable[ParamT, Result]], Callable[ParamT, Task[ParamT, Result]]]
):
    """
    Wrap a function to turn it into a schedule-able task.

    @task
    async def my_task(a: int, b: float) -> None:
        ...

    You can define a function name to make use more portable.

    @task("my_app.my_task")
    async def my_task(a: int, b: float) -> None:
        ...

    """
    if isinstance(func, str):

        def register_func(f: Callable[ParamT, Result]) -> Task[ParamT, Result]:
            _task_manager.register_task(f, func)

            @wraps(f)
            def call_func(
                *args: ParamT.args, **kwargs: ParamT.kwargs
            ) -> Task[ParamT, Result]:
                return Task(f, args, kwargs, name=func)

            return call_func

        return register_func
    else:
        _task_manager.register_task(func)

        @wraps(func)
        def call_func(
            *args: ParamT.args, **kwargs: ParamT.kwargs
        ) -> Task[ParamT, Result]:
            return Task(func, args, kwargs)

        return call_func
