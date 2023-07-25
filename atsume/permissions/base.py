import abc


class AbstractComponentPermissions(abc.ABC):
    """
    Abstract class for Atsume's permission system. Initialized with the module path
    of a Component, and is called to determine if it should be permitted to act
    in the guild or DM. Can be subclassed to implement your own permissions check.
    """

    @abc.abstractmethod
    def __init__(self, component_path: str):
        ...

    @abc.abstractmethod
    def allow_in_guild(self, guild_id: int) -> bool:
        """Should this Component be allowed to run in the given guild ID?"""
        ...

    @abc.abstractmethod
    def allow_in_dm(self) -> bool:
        """Should this Component be allowed to run in DMs?"""
        ...
