"""
# Project CLI

Command line tools for generating an Atsume project.

"""
import click
import os

from atsume.templates import create_template


@click.group()
def cli() -> None:
    """
    This is the Click command group used by the Atsume command line tool.
    """
    pass


@cli.command("startproject")
@click.argument("project_name")
def start_project(project_name: str) -> None:
    """
    Command to scaffold a new Atsume project.
    :param project_name: The name of the resulting project.
    """
    dest = os.getcwd()
    create_template("project", dest, project_name=project_name)
