from _repobee import plugin

from repobee_sanitizer import sanitizer


def test_register():
    """Just test that there is no crash"""
    plugin.register_plugins([sanitizer])
