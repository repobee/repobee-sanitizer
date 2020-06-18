"""File sanitization module.

.. module:: _sanitize_file
    :synopsis: Module for file sanitization functionality.

.. moduleauthor:: Simon Larsén
"""

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
