import importlib

from atsume.cli.base import cli

CLI_EXTENSIONS = [
    "atsume.alembic.cli",
    "atsume.bot",
]


def run_command() -> None:
    for extension in CLI_EXTENSIONS:
        module = importlib.import_module(extension)
    cli()
