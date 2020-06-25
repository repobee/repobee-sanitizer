"""Extension command that provides functionality for sanitizing an entire
repository.

.. module:: _sanitize_repo
    :synopsis: Extensions command that provides functionality for sanitizing an
        entire repository.
"""
import pathlib
import argparse

from typing import Optional, Mapping, List

import repobee_plug as plug
import daiquiri

from repobee_sanitizer import _sanitize_file

_ASSUMED_ENCODING = "utf8"

LOGGER = daiquiri.getLogger(__file__)


class SanitizeRepo(plug.Plugin):
    """Extension command that provides functionality for sanitizing an entire
    repository.
    """

    def _sanitize_repo(
        self, args: argparse.Namespace, api: None,
    ) -> Optional[Mapping[str, List[plug.Result]]]:
        if not args.file_list.is_file():
            raise plug.PlugError(f"No such file: {args.file_list}")

        files = [
            pathlib.Path(p.strip())
            for p in args.file_list.read_text(encoding=_ASSUMED_ENCODING)
            .strip()
            .split("\n")
        ]

        for file in files:
            text = file.read_text(encoding=_ASSUMED_ENCODING)
            sanitized_text = _sanitize_file.sanitize(text)
            file.write_text(sanitized_text)
            LOGGER.info(f"Sanitized {file}")

    def create_extension_command(self) -> plug.ExtensionCommand:
        """
        Returns:
            The sanitize-repo extension command.
        """
        parser = plug.ExtensionParser()
        parser.add_argument(
            "--file-list",
            help="Path to a list of files to sanitize. The paths should be "
            "relative to the root of the repository.",
            type=pathlib.Path,
            metavar="<path>",
            required=True,
        )
        return plug.ExtensionCommand(
            parser=parser,
            name="sanitize-repo",
            help="Sanitize the current repository.",
            description="Sanitize the current repository.",
            callback=self._sanitize_repo,
        )
