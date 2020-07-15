import pytest
import pathlib
import tempfile

from repobee_sanitizer import _fileutils

import testhelpers


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


class TestRelativePath:
    """Tests for the RelativePath class."""

    def test_read_iso8859_1_encoded_file(self):
        """Currently, guessing ISO8859 encodings with the file command often
        only gives ``ISO8859``, which is not a complete encoding (i.e. it
        should be ``ISO8859-1``, ``ISO8859-2``, etc).
        """
        basedir = testhelpers.RESOURCES_BASEDIR
        abspath = testhelpers.get_resource("iso8859-1-encoded-file.txt")
        expected_text = (
            "Hello I'm Simon Larsén and this file is encoded in ISO8859-1"
        )

        relpath = _fileutils.create_relpath(abspath=abspath, basedir=basedir)

        assert relpath.read_text_relative_to(basedir).strip() == expected_text
