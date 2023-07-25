from pathlib import Path

TEMPLATE_DIR = Path(__file__).parent / "templates"

IGNORE_SUFFIX = {".pyc"}


def create_template(
    template_name: Path | str, dest: Path | str, **template_args: str
) -> None:
    """
    Create files from a template at a destination path,
    replacing template placeholders with given values.
    """
    template_path = TEMPLATE_DIR / template_name
    if not template_path.exists() or not template_path.is_dir():
        raise ValueError(f'Template "{template_name}" does not exist')
    if isinstance(dest, str):
        dest = Path(dest)
    # We go folder by folder down through the template
    for full_path in template_path.glob("*"):
        relative_path = full_path.relative_to(template_path)
        if full_path.is_dir():
            # Do any replacements we need on the folder's name
            folder_name = full_path.name
            folder_name = replace_in_string(folder_name, **template_args)
            new_folder_relative_path = relative_path.parent / folder_name
            # Create the folder
            (dest / new_folder_relative_path).mkdir(parents=True, exist_ok=True)
            # Start copying from inside the template folder into our new folder
            create_template(full_path, dest / new_folder_relative_path, **template_args)
        else:
            if full_path.suffix in IGNORE_SUFFIX:
                continue
            # Open the template file, perform any replacements, and save as the new template file
            with open(full_path, "r") as template_file:
                template = template_file.read()
                template = replace_in_string(template, **template_args)
                with open(dest / relative_path, "w") as dest_file:
                    dest_file.write(template)


def replace_in_string(string: str, **replacements: str) -> str:
    """Replace values in a string following key->value in the given dictionary."""
    for find, replace in replacements.items():
        string = string.replace(find, replace)
    return string
