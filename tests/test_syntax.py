from repobee_sanitizer import _syntax


def test_check_syntax_with_empty_string():
    """Check_syntax is a public function, therefore we have to check what
    happens if we give it an empty string. If it returns a anything, we know
    that it has the proper behavior, since it should fail on an empty file.
    """
    assert _syntax.check_syntax([""])
