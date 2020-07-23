"""Extension command that provides functionality for sanitizing a single file.

.. module:: _sanitize_file
    :synopsis: Extension command that provides functionality for
        sanitizing a single file.
"""

import argparse
import pathlib
from typing import Optional

import repobee_plug as plug

from repobee_sanitizer import _sanitize, _syntax


PLUGIN_NAME = "sanitizer"


class SanitizeFile(plug.Plugin):
    def _sanitize_file(
        self, args: argparse.Namespace, api: plug.API
    ) -> Optional[plug.Result]:
        """A callback function that runs the sanitization protocol on a given
        file.

        Args: args: Parsed and processed args from the RepoBee CLI. api: A
            platform API instance.

        Returns: An optional plug.PlugResult if the syntax is invalid,
            otherwise nothing.
        """
        errors = _syntax.check_syntax(args.infile.read_text().split("\n"))
        if errors:
            msg = []
            for error in errors:
                msg.append(f"Line {error.line}: {error.msg}\n")

            return plug.Result(
                name="sanitize-file",
                msg="".join(msg),
                status=plug.Status.ERROR,
            )

        result = _sanitize.sanitize_file(args.infile)
        if result:
            args.outfile.write_text(result)

    @plug.repobee_hook
    def create_extension_command(self) -> plug.ExtensionCommand:
        parser = plug.ExtensionParser()
        parser.add_argument(
            "infile", help="File to sanitize", type=pathlib.Path,
        )
        parser.add_argument(
            "outfile", help="Output path", type=pathlib.Path,
        )
        return plug.ExtensionCommand(
            parser=parser,
            name="sanitize-file",
            help="Sanitizes files",
            description=(
                "Iterate over files, removing"
                "code between certain START- and END-markers"
                ", also supporting REPLACE-WITH markers."
                "This allows a file to contain two versions"
                "at the same time"
            ),
            callback=self._sanitize_file,
        )
