"""File sanitization module.

.. module:: _sanitize_file
    :synopsis: Module for file sanitization functionality.

.. moduleauthor:: Simon Larsén
"""

import repobee_plug as plug

START_BLOCK = "REPOBEE-SANITIZER-BLOCK"
REPLACE_WITH = "REPOBEE-SANITIZER-REPLACE-WITH"
END_BLOCK = "REPOBEE-SANITIZER-END"

BLOCKS = [START_BLOCK, REPLACE_WITH, END_BLOCK]

""" Main entry point from other files"""


def sanitize(content: str) -> str:
    """Create a sanitized version of the input.

    Args:
        content: File content to be sanitized.
    Returns:
        A sanitized version of the input.
    """
    _check_syntax(content)


def _check_syntax(content: str):
    lines = content.split("\n")
    last = ""
    for line in lines:
        if last == "":
            for b in BLOCKS:
                if b in line:
                    last = b
                    continue
        for current in BLOCKS:
            if current in line:
                if last == START_BLOCK and current != (
                    REPLACE_WITH or END_BLOCK
                ):
                    raise plug.PlugError()
                elif last == REPLACE_WITH and current != END_BLOCK:
                    raise plug.PlugError()
                elif last == END_BLOCK and current != START_BLOCK:
                    raise plug.PlugError()
