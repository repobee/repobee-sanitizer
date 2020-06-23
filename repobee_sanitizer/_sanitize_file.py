"""File sanitization module.

.. module:: _sanitize_file
    :synopsis: Module for file sanitization functionality.

.. moduleauthor:: Simon Larsén
"""
import re
import repobee_plug as plug
from typing import List, Iterable

START_BLOCK = "REPOBEE-SANITIZER-BLOCK"
REPLACE_WITH = "REPOBEE-SANITIZER-REPLACE-WITH"
END_BLOCK = "REPOBEE-SANITIZER-END"


def sanitize(content: str) -> str:
    """Create a sanitized version of the input.

    Args:
        content: File content to be sanitized.
    Returns:
        A sanitized version of the input.
    """
    lines = list(content.split("\n"))
    _check_syntax(lines)
    sanitized_string = _sanitize(lines)
    return "\n".join(sanitized_string)


def _check_syntax(lines: List[str]) -> None:
    last = END_BLOCK
    errors = []
    prefix = ""
    for line_number, line in enumerate(lines, start=1):
        if START_BLOCK in line:
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

    if errors:
        raise plug.PlugError(errors)


def _sanitize(lines: List[str]) -> Iterable[str]:
    keep = True
    prefix_length = 0
    for line in lines:
        if START_BLOCK in line:
            prefix = re.match(rf"(.*?){START_BLOCK}", line).group(1)
            prefix_length = len(prefix)
            keep = False
        elif REPLACE_WITH in line or END_BLOCK in line:
            if END_BLOCK in line:
                prefix_length = 0
            keep = True
            continue
        if keep:
            yield line[prefix_length:]
