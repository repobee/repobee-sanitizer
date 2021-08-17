import pathlib
import git

from datetime import datetime

import repobee_plug as plug


class EmptyCommitError(plug.PlugError):
    pass


def create_pr_branch(repo_path: pathlib.Path, target_branch: str) -> str:
    """Create a new branch from the target_branch that we sanitize to
    and a pull request can be created from.

    Args:
        repo_path: Path to the repository
        target_branch: The branch to create the pull request branch from

    Returns:
        The target branch name with an added timestamp
    """
    pr_branch_name = (
        target_branch + "-pr-" + datetime.now().strftime("%Y/%m/%d_%H.%M.%S")
    )

    repo = git.Repo(str(repo_path))
    repo.git.branch(pr_branch_name, target_branch)

    return pr_branch_name


def branch_exists(repo_path: pathlib.Path, target_branch: str) -> bool:
    repo = git.Repo(str(repo_path))
    return target_branch in [branch.name for branch in repo.branches]


def _git_commit_on_branch(
    repo_root: pathlib.Path, target_branch: str, commit_message: str
):
    repo = git.Repo(str(repo_root))
    repo.git.symbolic_ref("HEAD", f"refs/heads/{target_branch}")
    repo.git.add(".", "--force")
    try:
        repo.git.commit("-m", commit_message)
    except git.GitCommandError as exc:
        assert "nothing to commit, working tree clean" in str(exc)
        raise EmptyCommitError() from exc


def _git_fetch(
    src_repo_path: pathlib.Path,
    src_branch: str,
    dst_repo_path: pathlib.Path,
    dst_branch: str,
):
    dst_repo = git.Repo(str(dst_repo_path))
    src_repo_uri = f"file://{src_repo_path.absolute()}"
    dst_repo.git.fetch(src_repo_uri, f"{src_branch}:{dst_branch}")


def _clean_repo(repo_path: pathlib.Path):
    """Resets working tree and index to HEAD. This is to untracked files as
    well as uncommitted changes.
    """
    repo = git.Repo(str(repo_path))
    repo.git.reset("--hard")
    repo.git.clean("-dfx")
