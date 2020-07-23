"""Helper functions for the test suite."""

import pathlib

from typing import Iterable, Tuple

INPUT_FILENAME = "input.in"
OUTPUT_FILENAME = "output.out"

TEST_CASE_DIR = pathlib.Path(__file__).parent.parent / "test_case_files"

VALID_CASES_BASEDIR = TEST_CASE_DIR / "valid"
INVALID_CASES_BASEDIR = TEST_CASE_DIR / "invalid"
RESOURCES_BASEDIR = pathlib.Path(__file__).parent.parent / "resources"


def discover_test_cases(
    test_case_base: pathlib.Path,
) -> Iterable[pathlib.Path]:
    """Return a list of all test case directories that are direct or indirect
    children of the base path.
    """

    def _is_test_dir(d):
        if not d.is_dir():
            return

        children = [f.name for f in d.iterdir()]
        return INPUT_FILENAME in children and OUTPUT_FILENAME in children

    return filter(_is_test_dir, test_case_base.rglob("*"))


def generate_valid_test_cases():
    valid_test_case_dirs = discover_test_cases(VALID_CASES_BASEDIR)
    marked_args = [
        (read_valid_test_case_files(case_dir), case_dir)
        for case_dir in valid_test_case_dirs
    ]
    args = [arg for arg, _ in marked_args]
    ids = [str(id_.relative_to(VALID_CASES_BASEDIR)) for _, id_ in marked_args]
    return args, ids


def generate_invalid_test_cases():
    invalid_files = list(INVALID_CASES_BASEDIR.glob("*.in"))
    ids = [str(f.relative_to(INVALID_CASES_BASEDIR)) for f in invalid_files]
    return [f.absolute() for f in invalid_files], ids


def read_valid_test_case_files(test_case_dir: pathlib.Path) -> Tuple[str, str]:
    inp = (test_case_dir / INPUT_FILENAME).read_text(encoding="utf8")
    out = (test_case_dir / OUTPUT_FILENAME).read_text(encoding="utf8")
    return inp, out


def get_test_image_path() -> pathlib.Path:
    return RESOURCES_BASEDIR / "RepoBee_favicon.png"


def get_resource(resource_name: str) -> pathlib.Path:
    return RESOURCES_BASEDIR / resource_name
