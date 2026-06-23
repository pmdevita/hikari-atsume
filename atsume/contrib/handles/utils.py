from atsume.component.manager import manager
from atsume.contrib.handles.permissions import DatabasePermissions


def reset_cache():
    for component in manager.component_configs:
        if isinstance(component.permissions, DatabasePermissions):
            component.permissions.reset_cache()
