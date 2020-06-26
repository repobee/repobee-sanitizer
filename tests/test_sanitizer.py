import repobee
from repobee_sanitizer import sanitizer


def test_register():
    """Just test that there is no crash"""
    repobee.try_register_plugin(
        sanitizer, sanitizer.SanitizeRepo, sanitizer.SanitizeFile
    )
