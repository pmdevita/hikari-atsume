import typing
from abc import ABC

from tanjun.context.base import BaseContext
from tanjun.context.message import MessageContext as TanjunMessageContext
from tanjun.context.slash import SlashContext as TanjunSlashContext
from tanjun.context.menu import MenuContext as TanjunMenuContext

# from tanjun.context.autocomplete import AutocompleteContext as TanjunAutocompleteContext
from .component import Component

# if typing.TYPE_CHECKING:
#     from atsume


class Context(BaseContext, ABC):
    """
    A subclass of `tanjun.Context` that adds a reference to the
    component object this command is running under.
    """
    _component: typing.Optional[Component]

    @property
    def component(self) -> typing.Optional[Component]:
        # <<inherited docstring from tanjun.abc.Context>>.
        return self._component


class MessageContext(Context, TanjunMessageContext):
    pass


class SlashContext(Context, TanjunSlashContext):
    pass


class MenuContext(Context, TanjunMenuContext):
    pass


# class AutocompleteContext(Context, TanjunAutocompleteContext):
#     pass
