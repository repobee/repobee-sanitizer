"""Functions and constants relating to the syntax of repobee-sanitizer.

.. module:: _syntaxhelpers
    :synopsis: Functions and constants relating to the syntax of
        repobee-sanitizer.
"""
import enum
import pathlib
from typing import List

import re
import repobee_plug as plug

from repobee_sanitizer import _fileutils


class Markers(enum.Enum):
    """The markers that define sanitizer blocks."""

    START = "REPOBEE-SANITIZER-START"
    REPLACE = "REPOBEE-SANITIZER-REPLACE-WITH"
    END = "REPOBEE-SANITIZER-END"


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
    last = Markers.END.value
    errors = []
    prefix = ""
    has_blocks = False
    for line_number, line in enumerate(lines, start=1):
        if Markers.START.value in line:
            has_blocks = True
            if last != Markers.END.value:
                errors.append(
                    f"Line {line_number}: "
                    "START block must begin file or follow an END block"
                )
            prefix = re.match(rf"(.*?){Markers.START.value}", line).group(1)
            last = Markers.START.value
        elif Markers.REPLACE.value in line:
            if last != Markers.START.value:
                errors.append(
                    f"Line {line_number}: "
                    "REPLACE-WITH block must follow START block"
                )
            last = Markers.REPLACE.value
        elif Markers.END.value in line:
            if last not in [Markers.START.value, Markers.REPLACE.value]:
                errors.append(
                    f"Line {line_number}: "
                    "END block must follow START or REPLACE block"
                )
            last = Markers.END.value

        if (
            last == Markers.REPLACE.value or Markers.END.value in line
        ) and not line.startswith(prefix):
            errors.append(f"Line {line_number}: Missing prefix")

    if last != Markers.END.value:
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
        for marker in Markers:
            if marker.value in line:
                return True
    return False
