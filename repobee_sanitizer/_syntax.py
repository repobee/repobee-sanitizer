"""Functions and constants relating to the syntax of repobee-sanitizer.

.. module:: _syntaxhelpers
    :synopsis: Functions and constants relating to the syntax of
        repobee-sanitizer.
"""
import enum
import pathlib
from typing import List, Optional

import re

from repobee_sanitizer import _fileutils, _format


class Markers(enum.Enum):
    """The markers that define sanitizer blocks."""

    START = "REPOBEE-SANITIZER-START"
    REPLACE = "REPOBEE-SANITIZER-REPLACE-WITH"
    END = "REPOBEE-SANITIZER-END"
    SHRED = "REPOBEE-SANITIZER-SHRED"


def check_syntax(lines: List[str]) -> List[_format.Error]:
    """Checks if the input adheres to proper sanitizer syntax using proper
    markers:

    The grammar is defined below in EBNF-like manner. Note that the syntax is
    not context- free as prefixes are defined on a per-block basis, so it's not
    possible to perfectly describe the syntax with EBNF.

    .. code-block:: raw

        FILE ::=
            SHRED_MARKER MARKERLESS_LINE* |
            (MARKERLESS_LINE* ((BLOCK | PREFIXED_BLOCK) MARKERLESS_LINE*)+)
        BLOCK ::=
            START_MARKER
            MARKERLESS_LINE*
            (REPLACE_MARKER
            MARKERLESS_LINE*)?
            END_MARKER
        PREFIXED_BLOCK ::=
            PREFIX START_MARKER
            MARKERLESS_LINE*
            (PREFIX REPLACE_MARKER
            (PREFIX MARKERLESS_LINE)*)?
            PREFIX END_MARKER
        START_MARKER ::= "REPOBEE-SANITIZER-START\n"
        REPLACE_MARKER ::= "REPOBEE-SANITIZER-REPLACE-WITH\n"
        END_MARKER ::= "REPOBEE-SANITIZER-END\n"
        SHRED_MARKER :: = "REPOBEE-SANITIZER-SHRED"
        MARKERLESS_LINE ::= line without sanitizer markers
        PREFIX ::= a sequence of characters that is defined for each block
            as any sequence that appears before the START_MARKER of that
            particular PREFIXED_BLOCK.


    Args:
        lines: List containing every line of a text file as one element in the
            list.
    Raises:
        A list of named tuples containing all found errors and their line
            number.
    """
    last = Markers.END
    prefix = ""
    has_blocks = lines and contained_marker(lines[0]) == Markers.SHRED

    errors = _check_shred_syntax(lines)
    if errors:
        return errors

    for line_number, line in enumerate(lines, start=1):

        def _error(msg):
            errors.append(_format.Error(line_number, msg))

        marker = contained_marker(line)
        if marker == Markers.START:
            has_blocks = True
            if last != Markers.END:
                _error("START block must begin file or follow an END block")
            prefix = re.match(rf"(.*?){Markers.START.value}", line).group(1).strip()
            last = Markers.START
        elif marker == Markers.REPLACE:
            if last != Markers.START:
                _error("REPLACE-WITH block must follow START block")
            last = Markers.REPLACE
        elif marker == Markers.END:
            if last not in [Markers.START, Markers.REPLACE]:
                _error("END block must follow START or REPLACE block")
            last = Markers.END

        if (
            last == Markers.REPLACE or marker == Markers.END
        ) and not line.lstrip().startswith(prefix):
            _error(f"Missing prefix: {prefix}")

        if marker == Markers.END:
            prefix = ""

    if last != Markers.END:
        errors.append(_format.Error(None, "Final block must be an END block"))

    if not (has_blocks or errors):
        errors.append(_format.Error(None, "There are no markers in the file"))

    return errors


def file_is_dirty(
    relpath: _fileutils.RelativePath, repo_root: pathlib.Path
) -> bool:
    """Checks if a file contains any markers, therefore telling us if it needs
    to be sanitized or not.

    Args:
        repo_root: The root directory of the repository containing the file.
        relpath: The file's relative path to repo_root.
    Returns:
        A boolean value. True if the file is dirty, false if not.
    """
    if relpath.is_binary:
        return False

    lines = relpath.read_text_relative_to(repo_root).split("\n")
    return any(map(contained_marker, lines))


def _check_shred_syntax(lines: List[str]) -> List[_format.Error]:
    """Tells us whether or not the text has valid usage of the shred marker.
    Valid syntax is, if a shred marker is on the first line of text then on
    every line other than the first, there should be no markers. If there is
    no shred marker on the first line, then there should not be one later.

    Args:
        lines: The file to check syntax for as a list of one string per
        line.
    Returns:
        A list of named tuples with all errors and their line numbers
    """
    errors = []
    has_shred_marker = (
        contained_marker(lines[0] if lines else "") == Markers.SHRED
    )
    for line_number, line in enumerate(lines, start=1):

        def _error(msg):
            errors.append(_format.Error(line_number, msg))

        marker = contained_marker(line)
        if marker == Markers.SHRED and line_number != 1:
            _error("SHRED marker only allowed on line 1")
        elif marker and marker != Markers.SHRED and has_shred_marker:
            _error("Marker is dissallowed after SHRED marker")
    return errors


def contained_marker(line: str) -> Optional[Markers]:
    """Find any marker contained in the line of text.

    Args:
        line: A single line of text.
    Returns:
        A :py:class:Markers: contained in the line, or ``None`` if there is no
        marker in the line.
    """
    for marker in Markers:
        if marker.value in line:
            return marker
    return None
