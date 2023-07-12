import importlib.util
import typing


def module_to_path(module_path: str) -> str:
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
    n = str(num)
    return "".join(["0" for i in range(pad - len(n))]) + n
