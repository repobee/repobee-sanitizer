"""File sanitization module.

.. module:: _sanitize_file
    :synopsis: Module for file sanitization functionality.
"""
import pathlib

from repobee_sanitizer import _syntax

import re
from typing import List, Iterable, Optional


def sanitize_file(file_abs_path: pathlib.Path) -> Optional[str]:
    """Runs the sanitization protocol on a given file. This can either remove
    the file or give back a sanitized version

    Args:
        file_abs_path:
            The absolute file path to the file you wish to sanitize.

    Returns:
        We return the sanitized output text, but only if the file
        was not removed.
    """
    text = file_abs_path.read_text()
    lines = text.split("\n")
    _syntax.check_syntax(lines)
    if _syntax.contained_marker(lines[0]) == _syntax.Markers.SHRED:
        file_abs_path.unlink()
    else:
        sanitized_string = _sanitize(lines)
        return "\n".join(sanitized_string)


def sanitize_text(content: str) -> str:
    """A function to directly sanitize given content.

    Args:
        Content to be sanitized.
    """
    lines = content.split("\n")
    _syntax.check_syntax(lines)
    sanitized_string = _sanitize(lines)
    return "\n".join(sanitized_string)


def _sanitize(lines: List[str]) -> Iterable[str]:
    keep = True
    prefix_length = 0
    for line in lines:
        marker = _syntax.contained_marker(line)
        if marker == _syntax.Markers.START:
            prefix = re.match(
                rf"(.*?){_syntax.Markers.START.value}", line
            ).group(1)
            prefix_length = len(prefix)
            keep = False
        elif marker in [_syntax.Markers.REPLACE, _syntax.Markers.END]:
            if marker == _syntax.Markers.END:
                prefix_length = 0
            keep = True
            continue
        if keep:
            yield line[prefix_length:]
