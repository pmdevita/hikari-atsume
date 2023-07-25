import click

from atsume.cli.base import cli, CLIContext

from atsume.templates import create_template


@cli.command("startapp")
@click.argument("component_name")
@click.pass_context
def start_component(ctx: click.Context, component_name: str) -> None:
    """
    Click command to scaffold a new component for an Atsume project.`
    """
    parent_ctx = ctx.parent
    if not isinstance(parent_ctx, CLIContext):
        raise ValueError("startapp wasn't able to get the highest level of context")
    create_template(
        "component",
        parent_ctx.project_dir,
        component_name=component_name,
        component_upper_name=component_name[0].upper() + component_name[1:],
    )
