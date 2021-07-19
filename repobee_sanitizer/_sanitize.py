"""File sanitization module.

.. module:: _sanitize_file
    :synopsis: Module for file sanitization functionality.
"""

from repobee_sanitizer import _syntax
from repobee_sanitizer._syntax import Markers

from typing import List, Iterable, Optional


def sanitize_text(lines: List[str], strip: bool = False) -> Optional[str]:
    """A function to directly sanitize given content. Text must be syntax
    checked first.

    Args:
        Content to be sanitized
    """
    if _syntax.contained_marker(lines[0]) == Markers.SHRED:
        return None
    sanitized_string = _sanitize(lines, strip)
    return "\n".join(sanitized_string)


def _sanitize(lines: List[str], strip: bool = False) -> Iterable[str]:
    keep = True
    prefix = ""
    in_replace = False
    for line in lines:
        marker = _syntax.contained_marker(line)
        if marker == Markers.START:
            prefix = _syntax.search_prefix(line)
            keep = strip
        elif marker == Markers.REPLACE:
            keep = not strip
            in_replace = True
        elif marker == Markers.END:
            keep = True
            in_replace = False
        if keep and not marker:
            yield line.replace(
                prefix, "", 1
            ) if prefix and in_replace else line
