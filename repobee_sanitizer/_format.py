"""Functions and constants relating to the formating of errors used in
    repobee-sanitizer.

.. module:: _format
    :synopsis: Functions and constants relating to the formating of text used
        in repobee-sanitizer.
"""
import collections

from typing import List

Error = collections.namedtuple("Error", "line msg")

FileWithErrors = collections.namedtuple(
    "FileWithErrors", "file_rel_path errors"
)


def format_error_string(files_with_errors: List[FileWithErrors]) -> str:
    """Takes a list of named tuples containing a files name, and a list of
    errors and what lines they are found on. The list is then converted into a
    properly formatted string to be printed on the command line.

    Args:
        files_with_errors: List of named tuples containing a files name paired
        with a list of named tuples containing errors and what line they are
        found on in that file.

    Returns:
        A properly formated output string describing all found errors.

    """
    formated_str = [
        f"Syntax errors detected in {len(files_with_errors)} file(s):\n"
    ]
    for file in files_with_errors:
        formated_str.append(f"\n{file.file_rel_path}\n")
        for error in file.errors:
            linestr = f"Line {error.line}: "
            formated_str.append(
                f"    {linestr if error.line else 'Global: '}{error.msg}\n"
            )

    return "".join(formated_str)


def format_success_string(ignore_list: [str], files_not_found: [str]) -> str:
    """Return a message stating that sanitization was successfull. If given a
    list of files that were ignored during sanitization, the message will
    state which these were.

    Args:
        ignore_list: List of the names of files that are ignored during
            sanitization.

    Returns:
        A properly formated output string describing what was done.
    """

    formated_str = ["Successfully sanitized repo"]

    found_files = [file for file in ignore_list if file not in files_not_found]
    if found_files:
        formated_str.append(
            f"\n\nIgnore-list specified, ignored {len(list(found_files))} "
            "file(s):\n"
        )
        for file in found_files:
            formated_str.append(f"\n\t{file}")

    if files_not_found:
        formated_str.append(
            f"\n\nCould not find {len(list(files_not_found))} specified "
            "file(s):\n"
        )
        for file in files_not_found:
            formated_str.append(f"\n\t{file}")

    return "".join(formated_str)
