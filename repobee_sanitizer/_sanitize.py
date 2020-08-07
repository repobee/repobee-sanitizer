"""File sanitization module.

.. module:: _sanitize_file
    :synopsis: Module for file sanitization functionality.
"""
import pathlib

from repobee_sanitizer import _syntax, _fileutils
from repobee_sanitizer._syntax import Markers

import re
from typing import List, Iterable, Optional


def sanitize_file(
    basedir: pathlib.Path,
    relpath: _fileutils.RelativePath,
    strip: bool = False,
) -> Optional[str]:
    """Runs the sanitization protocol on a given file. This can either remove
    the file or give back a sanitized version. File must be syntax checked
    before running this.

    Args:
        file_abs_path: The absolute file path to the file you wish to
            sanitize

    Returns:
        The sanitized output text, but only if the file was not
            removed
    """
    text = relpath.read_text_relative_to(basedir)
    lines = text.split("\n")
    if _syntax.contained_marker(lines[0]) == Markers.SHRED:
        return None
    sanitized_string = _sanitize(lines, strip)
    return "\n".join(sanitized_string)


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
    prefix_length = 0
    for line in lines:
        marker = _syntax.contained_marker(line)
        if marker == Markers.START:
            prefix = re.match(rf"(.*?){Markers.START.value}", line).group(1)
            prefix_length = len(prefix) if not strip else 0
            keep = strip
        elif marker == Markers.REPLACE:
            keep = not strip
        elif marker == Markers.END:
            prefix_length = 0
            keep = True
        if keep and not marker:
            yield line[prefix_length:]
