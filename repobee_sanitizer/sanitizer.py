"""The plugin module for repobee-sanitizer.

.. module:: sanitizer
    :synopsis: A plugin for RepoBee to sanitize master repositories before
        being pushed to students.

.. moduleauthor:: Simon Larsén
"""

import argparse
import pathlib
from typing import List, Mapping, Optional

import repobee_plug as plug

from repobee_sanitizer import _sanitize
from repobee_sanitizer._sanitize_repo import SanitizeRepo  # noqa: F401

PLUGIN_NAME = "sanitizer"


def _sanitize_file(
    args: argparse.Namespace, api: plug.API
) -> Optional[Mapping[str, List[plug.Result]]]:
    """A callback function that does nothing useful.

    Args:
        args: Parsed and processed args from the RepoBee CLI.
        api: A platform API instance.
    Returns:
        A mapping (str -> List[plug.Result]) that RepoBee's CLI can use for
        output.
    """
    text = args.infile.read_text(encoding="utf8")
    result = _sanitize.sanitize(text)
    args.outfile.write_text(result, encoding="utf8")


@plug.repobee_hook
def create_extension_command() -> plug.ExtensionCommand:
    parser = plug.ExtensionParser()
    parser.add_argument(
        "infile", help="File to sanitize", type=pathlib.Path,
    )
    parser.add_argument(
        "outfile", help="Output path", type=pathlib.Path,
    )
    return plug.ExtensionCommand(
        parser=parser,
        name="sanitize-file",
        help="Sanitizes files",
        description=(
            "Iterate over files, removing"
            "code between certain START- and END-markers"
            ", also supporting REPLACE-WITH markers."
            "This allows a file to contain two versions"
            "at the same time"
        ),
        callback=_sanitize_file,
    )
