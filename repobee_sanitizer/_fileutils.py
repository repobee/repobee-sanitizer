"""Functions for dealing with the file system.

.. module:: _fileutils
    :synopsis: Functions for dealing with the file system.
"""
import subprocess
import pathlib
import collections
import sys


class RelativePath(
    collections.namedtuple("RelativePath", "relpath encoding".split())
):
    """Data structure containing a relative path, and the file encoding of the
    file from which the relative path was created. The read and write methods
    must be used relative to some base directory.
    """

    def read_text_relative_to(self, basedir: pathlib.Path) -> str:
        """Read text from this relative path's file with the expected encoding,
        rooted in basedir.

        Args:
            basedir: The base directory which the path is relative to.
        Returns:
            The content of the file this path points to relative to the base
            directory, using the encoding of the original file.
        """
        return (basedir / self.relpath).read_text(encoding=self.encoding)

    def write_text_relative_to(self, data: str, basedir: pathlib.Path) -> None:
        """Write the provided string to the file at this path's location
        relative to the basedir, using the encoding of the original file this
        path was created from.

        Args:
            data: Data to write.
            basedir: The base directory to which this path is relative.
        """
        (basedir / self.relpath).write_text(data=data, encoding=self.encoding)

    @property
    def is_binary(self):
        return self.encoding == "binary"

    def __str__(self) -> str:
        return str(self.relpath)


def create_relpath(
    abspath: pathlib.Path, basedir: pathlib.Path
) -> RelativePath:
    """Wrap a path in a RelativePath, with an inferred encoding.

    Args:
        abspath: Absolute path to the path to wrap. Must be contained in
            basedir, or a subdirectory of it.
        basedir: The base directory to which the RelativePath will be relative.
    Returns:
        A RelativePath wrapper around a path.
    """
    if not abspath.is_absolute():
        raise ValueError(
            f"Argument 'abspath' must be absolute, but was: '{abspath}'"
        )
    abspath.resolve(strict=True)
    abspath.relative_to(basedir)

    relpath = abspath.relative_to(basedir)
    encoding = _infer_encoding(abspath)
    return RelativePath(relpath=relpath, encoding=encoding)


def _infer_encoding(path: pathlib.Path) -> str:
    """Use the ``file`` command to guess the encoding of a file."""
    proc = subprocess.run(
        ["file", "--mime-encoding", "--brief", str(path)], capture_output=True
    )
    return proc.stdout.decode(encoding=sys.getdefaultencoding()).strip()
