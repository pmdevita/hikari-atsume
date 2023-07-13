"""
# Command Line Tools

Utilities for running Atsume's command line tools.

"""

import importlib

from atsume.cli.base import cli

CLI_EXTENSIONS = [
    "atsume.alembic.cli",
    "atsume.bot",
]
"""The default list of CLI extensions to load."""


def run_command() -> None:
    """
    Run the Atsume project command line tools. This loads all of the
    CLI extensions and then calls the main click group.
    :return:
    """
    for extension in CLI_EXTENSIONS:
        module = importlib.import_module(extension)
    cli()
