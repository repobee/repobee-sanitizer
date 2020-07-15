"""File sanitization module.

.. module:: _sanitize_file
    :synopsis: Module for file sanitization functionality.
"""
from repobee_sanitizer import _syntax

import re
from typing import List, Iterable


def sanitize(content: str) -> str:
    """Create a sanitized version of the input.

    Args:
        content: Raw file content to be sanitized.
    Returns:
        A sanitized version of the input.
    """
    lines = content.split("\n")
    _syntax.check_syntax(lines)
    sanitized_string = _sanitize(lines)
    return "\n".join(sanitized_string)


def _sanitize(lines: List[str]) -> Iterable[str]:
    keep = True
    prefix_length = 0
    for line in lines:
        if _syntax.START_BLOCK in line:
            prefix = re.match(rf"(.*?){_syntax.START_BLOCK}", line).group(1)
            prefix_length = len(prefix)
            keep = False
        elif _syntax.REPLACE_WITH in line or _syntax.END_BLOCK in line:
            if _syntax.END_BLOCK in line:
                prefix_length = 0
            keep = True
            continue
        if keep:
            yield line[prefix_length:]
