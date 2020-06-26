"""The plugin module for repobee-sanitizer.

.. module:: sanitizer
    :synopsis: A plugin for RepoBee to sanitize master repositories before
        being pushed to students.

.. moduleauthor:: Simon Larsén
"""

from repobee_sanitizer._sanitize_repo import SanitizeRepo
from repobee_sanitizer._sanitize_file import SanitizeFile

__all__ = [SanitizeRepo.__name__, SanitizeFile.__name__]
