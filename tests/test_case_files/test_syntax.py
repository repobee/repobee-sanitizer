import pytest

from repobee_sanitizer import _syntax
import repobee_plug as plug


def test_check_syntax_with_empty_string():
    """Check_syntax is a public function, therefore we have to check what
    happens if we give it an empty string.
    """
    with pytest.raises(plug.PlugError) as exc:
        _syntax.check_syntax("")

    assert "There are no markers in the file" in exc.value
