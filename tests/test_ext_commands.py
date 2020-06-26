import collections
import pathlib

import pytest
import repobee

import testhelpers

_FileInfo = collections.namedtuple(
    "_FileInfo", "expected_text abspath relpath".split()
)
_FakeRepoInfo = collections.namedtuple(
    "_FakeRepoInfo", "root_path file_list_path file_infos"
)


def test_sanitize_valid_file(sanitizer_config, tmpdir):
    test_case_dir = (
        testhelpers.VALID_CASES_BASEDIR
        / "replace"
        / "prefixed"
        / "junit_test_case"
    )
    inp_text, out_text = testhelpers.read_valid_test_case_files(test_case_dir)

    infile = pathlib.Path(tmpdir) / "input.in"
    infile.write_text(inp_text)
    outfile = pathlib.Path(tmpdir) / "output.out"

    repobee.main(
        f"repobee --config-file {sanitizer_config} sanitize-file "
        f"{infile} {outfile}".split()
    )

    assert outfile.read_text(encoding="utf8") == out_text


def test_sanitize_repo_dictate_mode(sanitizer_config, fake_repo):
    """Test sanitize repo with a list of files to sanitize."""
    repobee.main(
        f"repobee --config-file {sanitizer_config} sanitize-repo "
        f"--file-list {fake_repo.file_list_path} "
        f"--repo-root {fake_repo.root_path}".split()
    )

    asserted = False
    for file_info in fake_repo.file_infos:
        asserted = True
        assert file_info.abspath.read_text("utf8") == file_info.expected_text
    assert asserted


@pytest.fixture
def fake_repo(tmpdir) -> _FakeRepoInfo:
    """Setup a fake repository to sanitize."""
    fake_repo = pathlib.Path(tmpdir)
    file_infos = []
    for raw_case, id_ in zip(*testhelpers.generate_valid_test_cases()):
        input_text, expected_output_text = raw_case
        output_path = fake_repo / id_
        output_path.parent.mkdir(parents=True)
        output_path.write_text(input_text)
        file_infos.append(
            _FileInfo(
                expected_text=expected_output_text,
                abspath=output_path,
                relpath=pathlib.Path(id_),
            )
        )

    file_list = fake_repo / "file_list.txt"
    file_list_content = "\n".join([str(c.relpath) for c in file_infos])
    file_list.write_text(file_list_content)

    return _FakeRepoInfo(
        root_path=fake_repo, file_list_path=file_list, file_infos=file_infos,
    )