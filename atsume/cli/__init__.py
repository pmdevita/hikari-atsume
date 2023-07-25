"""
Functions for Atsume's command line tools. Atsume has two command line interfaces:

- `atsume` (the library CLI), the tool included with the installation of the library in your Python environment
- `manage.py` (the project CLI), the tool used within your Atsume project for managing and running it.

"""

import importlib
from pathlib import Path

from atsume.cli.base import cli, CLIContext

CLI_EXTENSIONS = [
    "atsume.alembic.cli",
    "atsume.bot",
    "atsume.cli.component",
]
"""The default list of CLI extensions to load. This may be extensible in the future."""

__all__ = ["run_command", "CLI_EXTENSIONS"]


def run_command(project_dir: Path | str) -> None:
    """
    Run the project CLI. This loads all of the
    CLI extensions and then calls the main click group. This is what is called by your
    project's `manage.py` file.
    """
    for extension in CLI_EXTENSIONS:
        module = importlib.import_module(extension)
    context = cli.context_class
    if not issubclass(context, CLIContext):
        raise ValueError("CLI's context is not the custom class.")
    if isinstance(project_dir, str):
        project_dir = Path(project_dir)
    context.project_dir = project_dir
    cli()
