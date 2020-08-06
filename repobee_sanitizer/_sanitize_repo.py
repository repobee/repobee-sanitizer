"""Helper functions for the sanitize repo command

.. module:: _sanitize_repo
    :synopsis: Helper functions for the sanitize repo command
"""
import pathlib
import shutil
import tempfile

from typing import Optional, List

import repobee_plug as plug
import daiquiri
import git

from repobee_sanitizer import _sanitize, _fileutils, _syntax, _format

PLUGIN_NAME = "sanitizer"

LOGGER = daiquiri.getLogger(__file__)


def check_repo_state(repo_root) -> Optional[str]:
    try:
        repo = git.Repo(repo_root)
    except git.InvalidGitRepositoryError as exc:
        raise plug.PlugError(f"Not a git repository: '{repo_root}'") from exc

    message = ""
    help_message = "\n\nUse --force to ingore this warning and sanitize anyway"

    if repo.head.commit.diff():
        message = "There are uncommitted staged files in the repo"
    if repo.untracked_files:
        message = "There are untracked files in the repo"
    if repo.index.diff(None):
        message = "There are uncommitted unstaged files in the repo"

    return message + help_message if message else None


def discover_dirty_files(
    repo_root: pathlib.Path,
) -> List[_fileutils.RelativePath]:
    """
    Returns:
        A list of relative file paths for files that need to be sanitized.
    """
    git_dir_relpath = ".git"
    relpaths = (
        _fileutils.create_relpath(path, repo_root)
        for path in repo_root.rglob("*")
        if path.is_file()
        and path.relative_to(repo_root).parts[0] != git_dir_relpath
    )
    return [sp for sp in relpaths if _syntax.file_is_dirty(sp, repo_root)]


def sanitize_files(
    basedir: pathlib.Path, file_relpaths: List[_fileutils.RelativePath]
) -> List[_format.FileWithErrors]:
    """Checks the syntax of the provided files and reports any found errors.
    If any errors are found, report errors and exits. If there are no errors,
    then all files are sanitized."""
    files_with_errors = []

    for relpath in file_relpaths:
        text = relpath.read_text_relative_to(basedir)
        errors = _syntax.check_syntax(text.split("\n"))
        if errors:
            files_with_errors.append(_format.FileWithErrors(relpath, errors))

    if files_with_errors:
        return files_with_errors

    for relpath in file_relpaths:
        file_abspath = basedir / str(relpath)
        sanitized_text = _sanitize.sanitize_file(basedir, relpath)
        if sanitized_text is None:
            file_abspath.unlink()
            LOGGER.info(f"Shredded file {relpath}")
        else:
            relpath.write_text_relative_to(
                data=sanitized_text, basedir=basedir
            )
            LOGGER.info(f"Sanitized {relpath}")

    return []


def sanitize_to_target_branch(
    repo_path: pathlib.Path, target_branch: str,
) -> List[_format.FileWithErrors]:
    """Create a commit on the target branch of the specified repo with
    sanitized versions of the provided files, without modifying the
    working tree or HEAD of the repo.

    Args:
        repo_path: Path to the repository.
        file_relpaths: A list of paths relative to the root of the working
            tree that should be sanitized.
        target_branch: The branch to create the commit on.

    Returns:
        List of errors if any errors are found, otherwise an empty list.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_copy_path = pathlib.Path(tmpdir) / "repo"
        shutil.copytree(src=repo_path, dst=repo_copy_path)
        _clean_repo(repo_copy_path)
        file_relpaths = discover_dirty_files(repo_copy_path)
        errors = sanitize_files(repo_copy_path, file_relpaths)
        if errors:
            return errors
        _git_commit_on_branch(repo_copy_path, target_branch)
        _git_fetch(
            src_repo_path=repo_copy_path,
            src_branch=target_branch,
            dst_repo_path=repo_path,
            dst_branch=target_branch,
        )

    return []


def _clean_repo(repo_path: pathlib.Path):
    """Resets working tree and index to HEAD. This is to untracked files as
    well as uncommitted changes.
    """
    repo = git.Repo(str(repo_path))
    repo.git.reset("--hard")
    repo.git.clean("-dfx")


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
