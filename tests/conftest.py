"""Global fixtures and setup code for the test suite."""
import sys
import pathlib
import pytest

sys.path.append(str(pathlib.Path(__file__).parent / "helpers"))

@pytest.fixture
def sanitizer_config(tmpdir):
    """Config file which only specifies sanitizer as a plugin."""
    config_file = pathlib.Path(tmpdir) / "sanitizer_config.cnf"
    config_file.write_text("[DEFAULTS]\nplugins = sanitizer\n")
    yield config_file
