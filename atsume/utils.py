import importlib.util


def module_to_path(module_path):
    module = importlib.util.find_spec(module_path)
    path = module.submodule_search_locations[0]
    return path
