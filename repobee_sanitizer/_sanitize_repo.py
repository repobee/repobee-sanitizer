"""Extension command that provides functionality for sanitizing an entire
repository.

.. module:: _sanitize_repo
    :synopsis: Extensions command that provides functionality for sanitizing an
        entire repository.
"""
import pathlib
import argparse
import shutil
import tempfile

from typing import Optional, Mapping, List

import repobee_plug as plug
import daiquiri
import git

from repobee_sanitizer import _sanitize

_ASSUMED_ENCODING = "utf8"

LOGGER = daiquiri.getLogger(__file__)


class SanitizeRepo(plug.Plugin):
    """Extension command that provides functionality for sanitizing an entire
    repository.
    """

    def _sanitize_repo(
        self, args: argparse.Namespace, api: None,
    ) -> Optional[Mapping[str, List[plug.Result]]]:
        message = _check_repo_state(args.repo_root)
        if message:
            return plug.Result(
                name="sanitize-repo", msg=message, status=plug.Status.ERROR,
            )

        assert args.file_list or args.discover_files, "Missing arguments"
        file_relpaths = (
            _parse_file_list(args.file_list)
            if args.file_list
            else _discover_dirty_files(args.repo_root)
        )

        if args.no_commit:
            LOGGER.info("Executing dry run")
            _sanitize_files(args.repo_root, file_relpaths)
        else:
            LOGGER.info(f"Sanitizing repo and updating {args.target_branch}")
            _sanitize_to_target_branch(
                args.repo_root, file_relpaths, args.target_branch
            )

    def create_extension_command(self) -> plug.ExtensionCommand:
        """
        Returns:
            The sanitize-repo extension command.
        """
        parser = plug.ExtensionParser()
        parser.add_argument(
            "-r",
            "--repo-root",
            help="Path to the worktree root of the repository to sanitize.",
            type=pathlib.Path,
            metavar="path",
            default=pathlib.Path("."),
        )
        files_mutex_grp = parser.add_mutually_exclusive_group(required=True)
        files_mutex_grp.add_argument(
            "-f",
            "--file-list",
            help="Path to a list of files to sanitize. The paths should be "
            "relative to the root of the repository.",
            type=pathlib.Path,
            metavar="path",
        )
        files_mutex_grp.add_argument(
            "-d",
            "--discover-files",
            help="Find and sanitize all files in the repository that contain "
            "at least one sanitizer marker.",
            action="store_true",
        )
        mode_mutex_grp = parser.add_mutually_exclusive_group(required=True)
        mode_mutex_grp.add_argument(
            "-t",
            "--target-branch",
            help="Name of the branch to commit the sanitized files to.",
            metavar="branch",
            type=str,
        )
        mode_mutex_grp.add_argument(
            "--no-commit",
            help="Sanitize the worktree in the repo without committing.",
            action="store_true",
        )
        return plug.ExtensionCommand(
            parser=parser,
            name="sanitize-repo",
            help="Sanitize the current repository.",
            description="Sanitize the current repository.",
            callback=self._sanitize_repo,
        )


def _parse_file_list(file_list) -> List[pathlib.Path]:
    if not file_list.is_file():
        raise plug.PlugError(f"No such file: {file_list}")

    return [
        p.strip()
        for p in file_list.read_text(encoding=_ASSUMED_ENCODING)
        .strip()
        .split("\n")
    ]


def _discover_dirty_files(repo_root) -> List[pathlib.Path]:
    """
    Returns:
        A list of relative file paths for files that need to be sanitized.
    """
    git_dir_relpath = ".git"
    return [
        file
        for file in list(repo_root.rglob("*"))
        if file.is_file()
        and (file.relative_to(repo_root).parts[0] != git_dir_relpath)
        and _file_is_dirty(file)
    ]


def _file_is_dirty(file: pathlib.Path) -> bool:
    content = file.read_text(encoding=_ASSUMED_ENCODING).split("\n")
    for line in content:
        for marker in _sanitize.SANITIZER_MARKERS:
            if marker in line:
                return True
    return False


def _sanitize_files(
    basedir: pathlib.Path, file_relpaths: List[pathlib.Path]
) -> None:
    """Sanitize the provided files."""
    for relpath in file_relpaths:
        file = basedir / relpath
        text = file.read_text(encoding=_ASSUMED_ENCODING)
        sanitized_text = _sanitize.sanitize(text)
        file.write_text(sanitized_text)
        LOGGER.info(f"Sanitized {file}")


def _sanitize_to_target_branch(
    repo_path: pathlib.Path,
    file_relpaths: List[pathlib.Path],
    target_branch: str,
) -> None:
    """Create a commit on the target branch of the specified repo with
    sanitized versions of the provided files, without modifying the
    working tree or HEAD of the repo.

    Args:
        repo_path: Path to the repository.
        file_relpaths: A list of paths relative to the root of the working
            tree that should be sanitized.
        target_branch: The branch to create the commit on.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_copy_path = pathlib.Path(tmpdir) / "repo"
        shutil.copytree(src=repo_path, dst=repo_copy_path)
        _sanitize_files(repo_copy_path, file_relpaths)
        _git_commit_on_branch(repo_copy_path, target_branch)
        _git_fetch(
            src_repo_path=repo_copy_path,
            src_branch=target_branch,
            dst_repo_path=repo_path,
            dst_branch=target_branch,
        )


def _check_repo_state(repo_root) -> Optional[str]:
    repo = git.Repo.init(repo_root)
    if repo.head.commit.diff():
        return "There are uncommitted staged files in the repo"
    if repo.untracked_files:
        return "There are untracked files in the repo"
    if repo.index.diff(None):
        return "There are uncommitted unstaged files in the repo"
    return None


def _git_commit_on_branch(repo_root: pathlib.Path, target_branch: str):
    repo = git.Repo(str(repo_root))
    repo.git.symbolic_ref("HEAD", f"refs/heads/{target_branch}")
    repo.git.add(".", "--force")
    repo.git.commit("-m", "'Sanitize files'")


def _git_fetch(
    src_repo_path: pathlib.Path,
    src_branch: str,
    dst_repo_path: pathlib.Path,
    dst_branch: str,
):
    dst_repo = git.Repo(str(dst_repo_path))
    src_repo_uri = f"file://{src_repo_path.absolute()}"
    dst_repo.git.fetch(src_repo_uri, f"{src_branch}:{dst_branch}")
