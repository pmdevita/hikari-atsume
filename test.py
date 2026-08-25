from typing import Any, Type


class DescTest:
    _state = None

    def __get__(self, instance, owner):
        print(instance, owner)
        return self.state

    def __set__(self, instance, value):
        print("setting to", value)


class DescMethods:
    name = DescTest()

    def __init__(self):
        self._key = "_uninitialized"  # Will be changed by the Component's metaclass

    def _set_state(self, key):
        pass

    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls, *args, **kwargs)
        return DescTest(), obj

    def change_state(self):
        print("hi")
        print(self.state)
        self.state = "changed"


class ComponentBase(type):
    def __new__(
        cls: Type["ComponentBase"],
        name: str,
        bases: tuple[type, ...],
        class_dict: dict[str, Any],
    ):
        # if len(bases) == 0:
        #     return

        for key, value in class_dict.items():
            if isinstance(value, DescMethods):
                value._key = key

        obj = super().__new__(cls, name, bases, class_dict)
        return obj


class Component(metaclass=ComponentBase):
    pass


class UIComponent(Component):
    name, name_methods = DescMethods()

    def render(self):
        print(self.name)
        self.name_methods.change_state()
        print(self.name)
        print(self.name_methods.state)


a = UIComponent()
print(a.render())
