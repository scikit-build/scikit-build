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

from . import _tmpdir, execute_setup_py
from .pytest_helpers import check_sdist_content


def test_build(capsys, project_setup_py_test):
    with project_setup_py_test("cmakelists-not-in-top-level-dir", ["build"]):
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

    # The cmake keywords are now validated by scikit-build-core's setuptools
    # plugin, and skbuild.setup() only forwards them to setuptools when a
    # CMakeLists.txt exists in cmake_source_dir (otherwise it falls back to a
    # plain setuptools build, like classic scikit-build did). The keyword is
    # therefore passed directly to setuptools.setup() here so that the
    # validation classic scikit-build performed itself is still exercised.
    (tmp_dir / "setup.py").write_text(
        textwrap.dedent(
            f"""
        import setuptools
        setuptools.setup(
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

    # The valid cases need a working CMakeLists.txt: when the keyword is given
    # directly to setuptools, the scikit-build-core plugin always runs CMake.
    (tmp_dir / "CMakeLists.txt").write_text(
        textwrap.dedent(
            """
        cmake_minimum_required(VERSION 3.15...3.31)
        project(test_cmake_source_dir NONE)
        install(CODE "")
        """
        )
    )

    failed = False
    message = ""
    try:
        with execute_setup_py(tmp_dir, ["build"]):
            pass
    except SystemExit as e:
        failed = True
        message = str(e)

    assert failed == expected_failed
    if failed:
        assert "cmake_source_dir must be an existing directory" in message


def test_hello_sdist(project_setup_py_test):
    with project_setup_py_test("cmakelists-not-in-top-level-dir", ["sdist"]):
        sdists_tar = glob.glob("dist/*.tar.gz")
        sdists_zip = glob.glob("dist/*.zip")
        assert sdists_tar or sdists_zip

        expected_content = [
            "hello-1.2.3/MANIFEST.in",
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
