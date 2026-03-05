"""test_cmakelists_not_in_top_level_dir
----------------------------------

Tries to build and test the `cmakelists_not_in_top_level_dir` sample
project. It basically checks that using the `cmake_source_dir` setup
keyword works.
"""

from __future__ import annotations

import glob
import textwrap

import pytest

from skbuild.exceptions import SKBuildError

from . import _tmpdir, execute_setup_py
from .pytest_helpers import check_sdist_content


def test_build(capsys, project_setup_py_test):
    with project_setup_py_test("cmakelists-not-in-top-level-dir", ["build"], disable_languages_test=True):
        out, err = capsys.readouterr()
        dist_warning = "Unknown distribution option: 'cmake_source_dir'"
        assert dist_warning not in err
        assert dist_warning not in out


@pytest.mark.parametrize(
    ("cmake_source_dir", "expected_failed"),
    [
        ("invalid", True),
        ("", False),
        (".", False),
    ],
)
def test_cmake_source_dir(cmake_source_dir, expected_failed):
    tmp_dir = _tmpdir("test_cmake_source_dir")

    (tmp_dir / "setup.py").write_text(
        textwrap.dedent(
            f"""
        from skbuild import setup
        setup(
            name="test_cmake_source_dir",
            version="1.2.3",
            description="a minimal example package",
            author='The scikit-build team',
            license="MIT",
            cmake_source_dir="{cmake_source_dir}"
        )
        """
        )
    )

    failed = False
    message = ""
    try:
        with execute_setup_py(tmp_dir, ["build"], disable_languages_test=True):
            pass
    except SystemExit as e:
        failed = isinstance(e.code, SKBuildError)
        message = str(e)

    assert failed == expected_failed
    if failed:
        assert "'cmake_source_dir' set to a nonexistent directory." in message


def test_hello_sdist(project_setup_py_test):
    with project_setup_py_test("cmakelists-not-in-top-level-dir", ["sdist"], disable_languages_test=True):
        sdists_tar = glob.glob("dist/*.tar.gz")
        sdists_zip = glob.glob("dist/*.zip")
        assert sdists_tar or sdists_zip

        expected_content = [
            "hello-1.2.3/hello/_hello.cxx",
            "hello-1.2.3/hello/CMakeLists.txt",
            "hello-1.2.3/hello/__init__.py",
            "hello-1.2.3/hello/__main__.py",
            "hello-1.2.3/setup.py",
        ]

        sdist_archive = None
        if sdists_tar:
            sdist_archive = "dist/hello-1.2.3.tar.gz"
        elif sdists_zip:
            sdist_archive = "dist/hello-1.2.3.zip"

        check_sdist_content(sdist_archive, "hello-1.2.3", expected_content)
