"""File sanitization module.

.. module:: _sanitize_file
    :synopsis: Module for file sanitization functionality.
"""
import pathlib

from repobee_sanitizer import _syntax
from repobee_sanitizer._syntax import Markers

import re
from typing import List, Iterable, Optional


def sanitize_file(file_abs_path: pathlib.Path) -> Optional[str]:
    """Runs the sanitization protocol on a given file. This can either remove
    the file or give back a sanitized version. File must be syntax checked
    before running this.

    Args:
        file_abs_path: The absolute file path to the file you wish to
            sanitize.

    Returns:
        The sanitized output text, but only if the file was not
        removed.
    """
    text = file_abs_path.read_text()
    lines = text.split("\n")
    if _syntax.contained_marker(lines[0]) == Markers.SHRED:
        file_abs_path.unlink()
    else:
        sanitized_string = _sanitize(lines)
        return "\n".join(sanitized_string)


def strip_file(file_abs_path: pathlib.Path) -> Optional[str]:
    """Runs the strip protocol on a given file. This will remove all sanitizer
    markers from the file. File must be syntax checked before running this.

    Args:
        file_abs_path: The absolute file path to the file you wish to
            strip.

    Returns:
        The stripped output text.
    """
    text = file_abs_path.read_text()
    lines = text.split("\n")
    stripped_string = _strip(lines)
    return "\n".join(stripped_string)


def sanitize_text(content: str) -> str:
    """A function to directly sanitize given content.

    Args:
        Content to be sanitized.
    """
    lines = content.split("\n")
    _syntax.check_syntax(lines)
    sanitized_string = _sanitize(lines)
    return "\n".join(sanitized_string)


def strip_text(content: str) -> str:
    """A function to remove sanitizer syntax from given content

    Args:
        Content to be stripped.
    """
    lines = content.split("\n")
    _syntax.check_syntax(lines)
    stripped_string = _strip(lines)
    return "\n".join(stripped_string)


def _sanitize(lines: List[str]) -> Iterable[str]:
    keep = True
    prefix_length = 0
    for line in lines:
        marker = _syntax.contained_marker(line)
        if marker == Markers.START:
            prefix = re.match(rf"(.*?){Markers.START.value}", line).group(1)
            prefix_length = len(prefix)
            keep = False
        elif marker in [Markers.REPLACE, Markers.END]:
            if marker == Markers.END:
                prefix_length = 0
            keep = True
            continue
        if keep:
            yield line[prefix_length:]


def _strip(lines: List[str]) -> Iterable[str]:
    keep = True
    for line in lines:
        marker = _syntax.contained_marker(line)
        if marker == Markers.START or marker == Markers.SHRED:
            continue
        elif marker == Markers.REPLACE:
            keep = False
        elif marker == Markers.END:
            keep = True
            continue
        if keep:
            yield line
