# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import pathlib
import sys
import tomllib
from datetime import datetime

project_root = pathlib.Path(__file__).parents[1]
sys.path.insert(0, project_root.resolve().as_posix())

with open(project_root / "pyproject.toml", "rb") as f:
    pyproject = tomllib.load(f)

project = "hikari-atsume"
copyright = f"{datetime.now().year}, Peter DeVita"
author = "Peter DeVita"
release = pyproject["tool"]["poetry"]["version"]

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    # "autodoc2",
    "sphinx.ext.autodoc",
    "autoapi.extension",
    "sphinx.ext.intersphinx",
    "myst_parser",
    "sphinxcontrib.asyncio",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
autodoc2_packages = [
    "../atsume",
]

myst_enable_extensions = ["colon_fence"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = 'alabaster'
html_theme = "furo"
html_static_path = ["_static"]


autoapi_root = "reference"
autoapi_dirs = ["../atsume"]
autodoc_typehints = "description"


autoapi_options = [
    "members",
    "show-inheritance",
    "show-module-summary",
    "imported-members",
]
autoapi_template_dir = "_templates"

autoapi_add_toctree_entry = True
# autoapi_keep_files = True
autoapi_member_order = "groupwise"

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "aiohttp": ("https://docs.aiohttp.org/en/stable", None),
    "attrs": ("https://www.attrs.org/en/stable/", None),
    "hikari": ("https://docs.hikari-py.dev/en/latest/", None),
    "tanjun": ("https://tanjun.cursed.solutions/", None),
}
