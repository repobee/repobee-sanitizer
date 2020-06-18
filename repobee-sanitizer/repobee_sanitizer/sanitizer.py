"""The plugin module for repobee-sanitizer.

.. module:: sanitizer
    :synopsis: A plugin for RepoBee to sanitize master repositories before being pushed to students.

.. moduleauthor:: Simon Larsén
"""

import pathlib
import os


import argparse
import configparser
from typing import List, Mapping, Optional

import repobee_plug as plug

PLUGIN_NAME = "sanitizer"


class AdvancedExtensionCommand(plug.Plugin):
    """An advanced extension command with all of the features, including
    command line options and configuration file options.

    The command can be configured by adding the [sanitizer]
    section to the config file, and using the "name" and "age" options. For
    example:

    .. code-block:: none

        [sanitizer]
        name = Some cool name
        age = 38
    """

    def __init__(self):
        self._name = None
        self._age = None

    def _callback(
        self, args: argparse.Namespace, api: plug.API
    ) -> Optional[Mapping[str, List[plug.Result]]]:
        """A callback function that does nothing useful.

        Args:
            args: Parsed and processed args from the RepoBee CLI.
            api: A platform API instance.
        Returns:
            A mapping (str -> List[plug.Result]) that RepoBee's CLI can use for
            output.
        """
        # do whatever you want to do!
        return {
            PLUGIN_NAME: [
                plug.Result(name=PLUGIN_NAME, status=plug.Status.SUCCESS, msg=str(args))
            ]
        }

    def config_hook(self, config_parser: configparser.ConfigParser) -> None:
        """Hook into the configuration file parsing.

        Args:
            config_parser: A configuration parser.
        """
        if PLUGIN_NAME not in config_parser:
            return

        self._name = config_parser.get(PLUGIN_NAME, "name", fallback=self._name)
        self._age = config_parser.get(PLUGIN_NAME, "age", fallback=self._age)

    def create_extension_command(self) -> plug.ExtensionCommand:
        """Create an extension command.

        Returns:
            The extension command to add to the RepoBee CLI.
        """
        parser = plug.ExtensionParser()
        parser.add_argument(
            "-n",
            "--name",
            help="Your name.",
            type=str,
            required=self._name is None,
            default=self._name,
        )
        parser.add_argument(
            "-a", "--age", help="Your age.", type=int, default=self._age,
        )
        return plug.ExtensionCommand(
            parser=parser,
            name="example-command",
            help="An example command.",
            description="An example extension command.",
            callback=self._callback,
            requires_api=True,
            requires_base_parsers=[
                plug.BaseParser.REPO_NAMES,
                plug.BaseParser.STUDENTS,
            ],
        )

