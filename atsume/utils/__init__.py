import importlib.util
import typing


def module_to_path(module_path: str) -> str:
    """
    Find the file path to a given Python module path
    :param module_path: A Python module path
    :return: A file path.
    """
    module = importlib.util.find_spec(module_path)
    if not module:
        raise ModuleNotFoundError()
    path = (
        module.submodule_search_locations[0]
        if module.submodule_search_locations
        else module.origin
    )
    if not path:
        raise Exception(f"Couldn't load module {module_path}")
    return path


def pad_number(num: int, pad: int) -> str:
    """
    Pad a given number with leading zeros.
    :param num: The number to pad.
    :param pad: The minimum length to pad for.
    :return: The padded number as a string.
    """
    n = str(num)
    return "".join(["0" for i in range(pad - len(n))]) + n


# Define some specification, see documentation
P = typing.ParamSpec("P")
T = typing.TypeVar("T")


# For a help about decorator with parameters see
# https://stackoverflow.com/questions/5929107/decorators-with-parameters
def copy_kwargs(
    kwargs_call: typing.Callable[P, typing.Any]
) -> typing.Callable[[typing.Callable[..., T]], typing.Callable[P, T]]:
    """Decorator does nothing but returning the cast original function"""

    def return_func(func: typing.Callable[..., T]) -> typing.Callable[P, T]:
        return typing.cast(typing.Callable[P, T], func)

    return return_func
