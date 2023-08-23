import typing

import mypy.types
import mypy.checker
import mypy.nodes
from mypy.options import Options
from mypy.plugin import Plugin, AttributeContext


class SettingsPlugin(Plugin):
    """
    Due to the way settings load dynamically
    from the global defaults and user config, it's not possible to type check this purely through
    type hints. This plugin resolves types for settings by examining the typing of the default setting.

    This plugin is based on a similar plugin for Django's mypy typing.
    https://github.com/typeddjango/django-stubs/blob/master/mypy_django_plugin/transformers/settings.py

    """

    def __init__(
        self, options: Options, atsume_settings_module: typing.Optional[str] = None
    ):
        super().__init__(options)
        self.atsume_project_module: typing.Optional[str] = None
        if atsume_settings_module:
            self.atsume_project_module = atsume_settings_module

    def get_attribute_hook(
        self, fullname: str
    ) -> typing.Callable[[AttributeContext], mypy.types.Type] | None:
        """
        If given a settings property, return the type hint for that setting.
        :param fullname: The module path of the variable
        :return: A function which can be called to resolve it.
        """
        if not fullname.startswith("atsume.settings.Settings"):
            return None
        if fullname.startswith("atsume.settings.Settings._"):
            return None

        property_name = fullname[len("atsume.settings.Settings.") :]

        def func(ctx: AttributeContext) -> mypy.types.Type:
            api = ctx.api
            if not isinstance(api, mypy.checker.TypeChecker):
                raise ValueError("Not a Typechecker")
            project_settings: mypy.nodes.MypyFile | None = None
            local_settings: mypy.nodes.MypyFile | None = None
            global_settings: mypy.nodes.MypyFile | None = api.modules.get(
                "atsume.settings.default_settings"
            )
            if not global_settings:
                raise ValueError(f"Error getting global Atsume settings")
            if self.atsume_project_module:
                project_settings = api.modules.get(
                    f"{self.atsume_project_module}.settings"
                )
                local_settings = api.modules.get(f"{self.atsume_project_module}.local")
                if not project_settings:
                    raise ValueError(
                        f"Error getting project Atsume settings {self.atsume_project_module}.settings"
                    )
                if not local_settings:
                    raise ValueError(
                        f"Error getting global Atsume settings {self.atsume_project_module}.local"
                    )
            sym: mypy.nodes.SymbolTableNode | None = global_settings.names.get(
                property_name
            )
            if sym is None and self.atsume_project_module:
                assert project_settings is not None
                assert local_settings is not None
                sym = project_settings.names.get(property_name)
                if sym is None:
                    sym = local_settings.names.get(property_name)

            if sym is None:
                ctx.api.fail(
                    f"'Settings' object has no attribute {property_name!r}", ctx.context
                )
                return ctx.default_attr_type
            if not sym.type:
                raise ValueError(f"Symbol {sym} has no type?")
            return sym.type

        return func


def plugin(version: str) -> typing.Type[SettingsPlugin]:
    return SettingsPlugin
