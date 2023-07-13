"""
# Command Line Tools

Utilities for running Atsume's command line tools.

"""

import importlib
from pathlib import Path

from atsume.cli.base import cli, CLIContext

CLI_EXTENSIONS = [
    "atsume.alembic.cli",
    "atsume.bot",
    "atsume.cli.component",
]
"""The default list of CLI extensions to load."""


def run_command(project_dir: Path | str) -> None:
    """
    Run the Atsume project command line tools. This loads all of the
    CLI extensions and then calls the main click group.
    :return:
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
