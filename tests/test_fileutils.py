import pytest
import pathlib
import tempfile

from repobee_sanitizer import _fileutils


class TestCreateRelativePath:
    """Tests for the create_smart_relpath function."""

    def test_raises_if_abspath_is_not_absolute(self, tmpdir):
        basedir = pathlib.Path(tmpdir)
        abspath = basedir / "some_file"
        abspath.write_text("some content")

        relpath = abspath.relative_to(basedir)
        with pytest.raises(ValueError) as exc_info:
            _fileutils.create_relpath(abspath=relpath, basedir=basedir)

        assert "Argument 'abspath' must be absolute" in str(exc_info.value)

    def test_raises_if_abspath_does_not_exist(self, tmpdir):
        basedir = pathlib.Path(tmpdir)
        with tempfile.NamedTemporaryFile(dir=basedir) as tmpfile:
            # tmpfile is destroyed when exiting this context manager
            non_existing_file = pathlib.Path(tmpfile.name)

        with pytest.raises(FileNotFoundError) as exc_info:
            _fileutils.create_relpath(
                abspath=non_existing_file, basedir=basedir
            )

        assert f"No such file or directory: '{non_existing_file}'" in str(
            exc_info.value
        )

    def test_raises_if_abspath_is_not_contained_in_basedir(self, tmpdir):
        basedir = pathlib.Path(tmpdir)
        with tempfile.NamedTemporaryFile() as tmpfile:
            abspath = pathlib.Path(tmpfile.name)

            with pytest.raises(ValueError) as exc_info:
                _fileutils.create_relpath(abspath=abspath, basedir=basedir)

        assert f"'{abspath}' does not start with '{basedir}'" in str(
            exc_info.value
        )
