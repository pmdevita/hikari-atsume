import abc


class AbstractComponentPermissions(abc.ABC):
    @abc.abstractmethod
    def __init__(self, component_path: str):
        ...

    @abc.abstractmethod
    def allow_in_guild(self, guild_id: int) -> bool:
        ...

    @abc.abstractmethod
    def allow_in_dm(self) -> bool:
        ...
