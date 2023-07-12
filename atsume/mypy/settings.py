import typing

import mypy.types
import mypy.checker
import mypy.nodes
from mypy.plugin import Plugin, AttributeContext

# With a lot of help from the Django mypy plugin
# https://github.com/typeddjango/django-stubs/blob/master/mypy_django_plugin/transformers/settings.py


class SettingsPlugin(Plugin):
    def get_attribute_hook(
        self, fullname: str
    ) -> typing.Callable[[AttributeContext], mypy.types.Type] | None:
        if not fullname.startswith("atsume.settings.Settings"):
            return None
        if fullname.startswith("atsume.settings.Settings._"):
            return None

        property_name = fullname[len("atsume.settings.Settings.") :]

        def func(ctx: AttributeContext) -> mypy.types.Type:
            api = ctx.api
            if not isinstance(api, mypy.checker.TypeChecker):
                raise ValueError("Not a Typechecker")
            global_settings: mypy.nodes.MypyFile | None = api.modules.get(
                "atsume.settings.default_settings"
            )
            if not global_settings:
                raise ValueError(f"Error getting global Atsume settings")
            sym: mypy.nodes.SymbolTableNode | None = global_settings.names.get(
                property_name
            )
            if not sym:
                raise ValueError(f"Unable to get symbol {property_name}")
            if not sym.type:
                raise ValueError(f"Symbol {sym} has no type?")
            return sym.type

        return func


def plugin(version: str) -> typing.Type[SettingsPlugin]:
    return SettingsPlugin
