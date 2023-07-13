"""
# Project CLI

Command line tools for generating an Atsume project.

"""
import click
import os

from atsume.templates import create_template


@click.group()
def cli() -> None:
    pass


@cli.command("startproject")
@click.argument("project_name")
def start_project(project_name: str) -> None:
    dest = os.getcwd()
    create_template("project", dest, project_name=project_name)
