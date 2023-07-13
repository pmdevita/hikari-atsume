#!/usr/bin/env python
"""Atsume's command-line utility for administrative tasks."""
"""
Code adapted from Django.
Copyright (c) Django Software Foundation and individual contributors.
All rights reserved.
"""

import os
import sys
from pathlib import Path


def main() -> None:
    """Run administrative tasks."""
    # Bootstrap this folder into the Python path
    project_dir = Path(__file__).parent
    sys.path.append(str(project_dir))
    # Set the management module path
    os.environ.setdefault("ATSUME_SETTINGS_MODULE", "project_name")
    try:
        from atsume.cli import run_command
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Atsume. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    run_command(project_dir)


if __name__ == "__main__":
    main()
