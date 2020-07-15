"""Functions and constants relating to the syntax of repobee-sanitizer.

.. module:: _syntaxhelpers
    :synopsis: Functions and constants relating to the syntax of
    repobee-sanitizer.
"""
import pathlib
from typing import List

import re
import repobee_plug as plug

from repobee_sanitizer import _fileutils

START_BLOCK = "REPOBEE-SANITIZER-START"
REPLACE_WITH = "REPOBEE-SANITIZER-REPLACE-WITH"
END_BLOCK = "REPOBEE-SANITIZER-END"

SANITIZER_MARKERS = (
    START_BLOCK,
    REPLACE_WITH,
    END_BLOCK,
)


def check_syntax(lines: List[str]) -> None:
    """Checks if the input adheres to proper sanitizer syntax using proper
    markers:
    REPOBE-SANITIZER-START:
        REQUIRED: Must be the first marker in a file. For every START
        marker there must be a END markers.
    REPOBEE-SANITIZER-REPLACE-WITH:
        OPTIONAL: Must be between a START and END marker.
    REPOBEE_SANITIZER-END:
        REQUIRED: Must (only) exist for every START marker.
    Prefixes: A marker kan be prefixed with any character(s)
        (Ex: // for java comments). Prefix is determined before the START
        block and MUST be used before the other markers in the same block,
        as well as the lines between the REPLACE and END markers if that
        block has a REPLACE marker.

    Args:
        lines: List containing every line of a text file as one element in the
        list.
    Raises:
        plug.PlugError: Invalid Syntax.
    """
    last = END_BLOCK
    errors = []
    prefix = ""
    has_blocks = False
    for line_number, line in enumerate(lines, start=1):
        if START_BLOCK in line:
            has_blocks = True
            if last != END_BLOCK:
                errors.append(
                    f"Line {line_number}: "
                    "START block must begin file or follow an END block"
                )
            prefix = re.match(rf"(.*?){START_BLOCK}", line).group(1)
            last = START_BLOCK
        elif REPLACE_WITH in line:
            if last != START_BLOCK:
                errors.append(
                    f"Line {line_number}: "
                    "REPLACE-WITH block must follow START block"
                )
            last = REPLACE_WITH
        elif END_BLOCK in line:
            if last not in [START_BLOCK, REPLACE_WITH]:
                errors.append(
                    f"Line {line_number}: "
                    "END block must follow START or REPLACE block"
                )
            last = END_BLOCK

        if (last == REPLACE_WITH or END_BLOCK in line) and not line.startswith(
            prefix
        ):
            errors.append(f"Line {line_number}: Missing prefix")

    if last != END_BLOCK:
        errors.append("Final block must be an END block")

    if not has_blocks:
        errors.append("There are no markers in the file")

    if errors:
        raise plug.PlugError(errors)


def file_is_dirty(
    relpath: _fileutils.RelativePath, repo_root: pathlib.Path
) -> bool:
    """Checks if a file contains any markers, therefore telling us if it needs
    to be sanitized or not.

    Args:
        repo_root: The root directory of the repository containing the file.
        relpath: The file's relative path to repo_root.
    Returns:
        A boolean value. True if the file is dirty, false if not.
    """
    if relpath.is_binary:
        return False

    content = relpath.read_text_relative_to(repo_root).split("\n")
    for line in content:
        for marker in SANITIZER_MARKERS:
            if marker in line:
                return True
    return False
