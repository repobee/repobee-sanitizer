"""Global fixtures and setup code for the test suite."""
import sys
import pathlib
import pytest
import repobee

sys.path.append(str(pathlib.Path(__file__).parent / "helpers"))


@pytest.fixture(autouse=True)
def unregister_plugins():
    """Fixture that automatically unregisters all plugins after each test
    function. This is important for the end-to-end tests.
    """
    repobee.unregister_all_plugins()


@pytest.fixture
def sanitizer_config(tmpdir):
    """Config file which only specifies sanitizer as a plugin."""
    config_file = pathlib.Path(tmpdir) / "sanitizer_config.cnf"
    config_file.write_text("[DEFAULTS]\nplugins = sanitizer\n")
    yield config_file
