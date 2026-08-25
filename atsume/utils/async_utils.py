import traceback
from typing import Callable

from atsume.utils.types import ParamT, ReturnT


def task_exception_wrapper(f: Callable[ParamT, ReturnT]) -> Callable[ParamT, ReturnT]:
    async def wrapper(*args: ParamT.args, **kwargs: ParamT.kwargs) -> ReturnT:
        try:
            return await f(*args, **kwargs)
        except Exception:
            print(traceback.print_exc())

    return wrapper
