# Mypy

Atsume supports full strict Mypy type checking. However, this requires use of a plugin as 
Mypy needs help to understand the more dynamic parts of Atsume (mostly it's settings module).

## Setup

Add the `atsume.mypy` plugin to your `mypy.ini`. Your `atsume_settings_module` should be the 
package that your `local.py` and `settings.py` files are in.

```ini
[mypy]
plugins = atsume.mypy

[mypy.plugins.atsume]
atsume_settings_module = my_project
```

Alternatively, if you use a `pyproject.toml` to configure mypy, it should look like this.

```toml
[tool.mypy]
plugins = ["atsume.mypy"]

[tool.django-stubs]
atsume_settings_module = "my_project"
```


