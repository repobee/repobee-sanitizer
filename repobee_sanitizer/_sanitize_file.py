"""File sanitization module.

.. module:: _sanitize_file
    :synopsis: Module for file sanitization functionality.

.. moduleauthor:: Simon Larsén
"""
import re
import repobee_plug as plug

START_BLOCK = "REPOBEE-SANITIZER-BLOCK"
REPLACE_WITH = "REPOBEE-SANITIZER-REPLACE-WITH"
END_BLOCK = "REPOBEE-SANITIZER-END"

""" Main entry point from other files"""


def sanitize(content: str) -> str:
    """Create a sanitized version of the input.

    Args:
        content: File content to be sanitized.
    Returns:
        A sanitized version of the input.
    """
    lines = list(content.split("\n"))

    check_syntax(lines)

    sanitized_string = create_sanitized_string_as_generetor(lines)

    return "\n".join(sanitized_string)


# ADD THIS LATER TO CHECK_SYNTAX
# if re.match(r"(.*?)prefix", "line").group(1) != "":
#   raise plug.PlugError


def check_syntax(lines: list):
    last = ""
    current_line = 0
    errors = []
    for line in lines:
        current_line += 1

        if START_BLOCK in line:
            if last != "" and last != END_BLOCK:
                errors.append(
                    f"Line {current_line}: "
                    "START block must begin file or follow an END block"
                )
            last = START_BLOCK
            continue

        elif REPLACE_WITH in line:
            if last != START_BLOCK:
                errors.append(
                    f"Line {current_line}: "
                    "REPLACE-WITH block must follow START block"
                )
            last = REPLACE_WITH
            continue

        elif END_BLOCK in line:
            if last != START_BLOCK and last != REPLACE_WITH:
                errors.append(
                    f"Line {current_line}: "
                    "END block must follow START or REPLACE block"
                )
            last = END_BLOCK
            continue

    if last != END_BLOCK and last != "":
        errors.append("Final block must be an END block")

    if errors:
        raise plug.PlugError(errors)


def create_sanitized_string_as_generetor(lines: list):
    keep = True
    prefix = ""
    prefix_length = 0
    for line in lines:
        if START_BLOCK in line:
            prefix = re.match(r"(.*?)REPOBEE-SANITIZER-BLOCK", line).group(1)
            prefix_length = len(prefix)
            keep = False
        elif REPLACE_WITH in line or END_BLOCK in line:
            if END_BLOCK in line:
                prefix = ""
                prefix_length = 0
            keep = True
            continue
        if keep:
            yield line[prefix_length:]
