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
    _gitutils,
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


class _SanitizeError(plug.PlugError):
    def __init__(self, msg: str, cause: Optional[Exception] = None):
        self.msg = msg
        super().__init__(msg, cause)


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
        converter=lambda s: pathlib.Path(s).resolve(strict=True),
        default=".",
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
        help=(
            "create and commit to a special branch 'sanitizer-pull-request'"
            "to safely merge using pull requests"
        ),
    )

    def command(self) -> Optional[plug.Result]:
        try:
            self._validate_input()
            result_message = (
                self._sanitize_no_commit()
                if self.no_commit
                else self._sanitize_to_target_branch()
            )
            status = plug.Status.SUCCESS
        except _SanitizeError as err:
            result_message = err.msg
            status = plug.Status.ERROR

        return plug.Result(
            name="sanitize-repo", msg=result_message, status=status
        )

    def _sanitize_no_commit(self) -> str:
        LOGGER.info("Executing dry run")
        file_relpaths = _sanitize_repo.discover_dirty_files(self.repo_root)
        errors = _sanitize_repo.sanitize_files(self.repo_root, file_relpaths)

        if errors:
            raise _SanitizeError(msg=_format.format_error_string(errors))

        return "Successfully sanitized repo"

    def _sanitize_to_target_branch(self) -> str:
        LOGGER.info(f"Sanitizing repo and updating {self.target_branch}")
        effective_target_branch = self._resolve_effective_target_branch(
            self.repo_root
        )
        try:
            errors = _sanitize_repo.sanitize_to_target_branch(
                self.repo_root, effective_target_branch, self.commit_message
            )
            if errors:
                raise _SanitizeError(msg=_format.format_error_string(errors))
        except _gitutils.EmptyCommitError:
            return (
                "No diff between target branch and sanitized output. "
                f"No changes will be made to branch: {self.target_branch}"
            )

        return "Successfully sanitized repo" + (
            f" to pull request branch\n\nrun 'git switch "
            f"{effective_target_branch}' to checkout the branch"
        )

    def _resolve_effective_target_branch(self, repo_root: pathlib.Path) -> str:
        if self.create_pr_branch:
            return _gitutils.create_pr_branch(repo_root, self.target_branch)
        return self.target_branch

    def _validate_input(self) -> plug.Result:
        message = _gitutils.check_repo_state(self.repo_root)
        if message and not self.force:
            raise _SanitizeError(msg=message)

        if self.create_pr_branch:
            if not self.target_branch:
                raise _SanitizeError(
                    msg="Can not create a pull request without a target "
                    "branch, please specify --target-branch"
                )
            elif not _gitutils.branch_exists(
                self.repo_root, self.target_branch
            ):
                raise _SanitizeError(
                    msg=f"Can not create a pull request branch from "
                    f"non-existing target branch {self.target_branch}"
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
