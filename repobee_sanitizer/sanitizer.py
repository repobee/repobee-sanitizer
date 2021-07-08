"""The plugin module for repobee-sanitizer.

.. module:: sanitizer
    :synopsis: A plugin for RepoBee to sanitize master repositories before
        being pushed to students.
"""
import pathlib
from typing import Optional

import daiquiri

import repobee_plug as plug
from repobee_sanitizer import (
    _sanitize,
    _syntax,
    _format,
    _sanitize_repo,
    _fileutils,
)

PLUGIN_NAME = "sanitizer"
LOGGER = daiquiri.getLogger(__file__)

sanitize_category = plug.cli.category(
    "sanitize",
    action_names=["repo", "file"],
    help="sanitize repositories and files based on markup",
    description="provides functionality to manage files to be deleted or "
    "modified based on a simple markup language",
)


class SanitizeRepo(plug.Plugin, plug.cli.Command):
    """Extension command that provides functionality for sanitizing an entire
    repository.
    """

    __settings__ = plug.cli.command_settings(
        help="sanitize a git repository",
        description="automatically identifies and sanitizes files in a git "
        "repository",
        action=sanitize_category.repo,
    )
    repo_root = plug.cli.option(
        short_name="-r",
        help="manually provide path to the root of git repository",
        converter=pathlib.Path,
        default=pathlib.Path("."),
    )
    commit_message = plug.cli.option(
        short_name="-m", default="Update task template", configurable=True
    )
    force = plug.cli.flag(
        help="ignore warnings for uncommitted files in the repository"
    )
    mode_mutex = plug.cli.mutually_exclusive_group(
        no_commit=plug.cli.flag(
            help="sanitizes on the current branch without creating a commit"
        ),
        target_branch=plug.cli.option(
            help="branch to commit the sanitized output to"
        ),
        __required__=True,
    )
    create_pr_branch = plug.cli.flag(
        short_name="-p",
        help="create and push to a special branch 'sanitizer-pull-request' to safely merge using pull requests in github",
    )

    def command(self) -> Optional[plug.Result]:
        repo_root = self.repo_root.absolute()
        message = _sanitize_repo.check_repo_state(repo_root)
        if message and not self.force:
            return plug.Result(
                name="sanitize-repo", msg=message, status=plug.Status.ERROR
            )

        if self.no_commit:
            LOGGER.info("Executing dry run")
            file_relpaths = _sanitize_repo.discover_dirty_files(repo_root)
            errors = _sanitize_repo.sanitize_files(repo_root, file_relpaths)
        else:
            LOGGER.info(f"Sanitizing repo and updating {self.target_branch}")
            try:
                errors = _sanitize_repo.sanitize_to_target_branch(
                    repo_root,
                    self.target_branch,
                    self.commit_message,
                    self.create_pr_branch,
                )
            except _sanitize_repo.EmptyCommitError:
                return plug.Result(
                    name="sanitize-repo",
                    msg="No diff between target branch and sanitized output. "
                    f"No changes will be made to branch: {self.target_branch}",
                    status=plug.Status.WARNING,
                )

        if errors:
            return plug.Result(
                name="sanitize-repo",
                msg=_format.format_error_string(errors),
                status=plug.Status.ERROR,
            )

        return plug.Result(
            name="sanitize-repo",
            msg="Successfully sanitized repo",
            status=plug.Status.SUCCESS,
        )


class SanitizeFile(plug.Plugin, plug.cli.Command):
    __settings__ = plug.cli.command_settings(
        help="sanitize target file",
        description="Sanitizes the target input file and saves the output in "
        "the specified outfile",
        action=sanitize_category.file,
    )

    infile = plug.cli.positional(converter=pathlib.Path)
    outfile = plug.cli.positional(converter=pathlib.Path)
    strip = plug.cli.flag(
        help="instead of sanitizing, remove all sanitizer markup from the file"
    )

    def command(self) -> Optional[plug.Result]:
        """A callback function that runs the sanitization protocol on a given
        file.

        Returns:
            Result if the syntax is invalid, otherwise nothing.
        """

        infile_encoding = _fileutils.guess_encoding(self.infile)
        infile_content = self.infile.read_text(encoding=infile_encoding).split(
            "\n"
        )

        errors = _syntax.check_syntax(infile_content)
        if errors:
            file_errors = [_format.FileWithErrors(self.infile.name, errors)]
            msg = _format.format_error_string(file_errors)

            return plug.Result(
                name="sanitize-file", msg=msg, status=plug.Status.ERROR
            )

        result = _sanitize.sanitize_text(infile_content, strip=self.strip)
        if result:
            self.outfile.write_text(result, encoding=infile_encoding)

        return plug.Result(
            name="sanitize-file",
            msg="Successfully sanitized file",
            status=plug.Status.SUCCESS,
        )
