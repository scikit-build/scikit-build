"""test_hello_pure
----------------------------------

Tries to build and test the `hello-pure` sample project.
"""

from __future__ import annotations

import glob

from skbuild.constants import SKBUILD_DIR
from skbuild.utils import push_dir

from .pytest_helpers import check_sdist_content, check_wheel_content


def test_hello_pure_builds(capsys, project_setup_py_test):
    with project_setup_py_test("hello-pure", ["build"], disable_languages_test=True):
        out, _ = capsys.readouterr()
        assert "skipping skbuild (no CMakeLists.txt found)" in out


def test_hello_pure_sdist(project_setup_py_test):
    with project_setup_py_test("hello-pure", ["sdist"], disable_languages_test=True):
        sdists_tar = glob.glob("dist/*.tar.gz")
        sdists_zip = glob.glob("dist/*.zip")
        assert sdists_tar or sdists_zip

        dirname = "hello-pure-1.2.3"
        # setuptools 69.3.0 and above now canonicalize the filename as well.
        if any("hello_pure" in x for x in sdists_zip + sdists_tar):
            dirname = "hello_pure-1.2.3"

        expected_content = [
            f"{dirname}/hello/__init__.py",
            f"{dirname}/setup.py",
        ]

        sdist_archive = f"dist/{dirname}.zip"
        if sdists_tar:
            sdist_archive = f"dist/{dirname}.tar.gz"

        check_sdist_content(sdist_archive, dirname, expected_content)


def test_hello_pure_wheel(project_setup_py_test):
    with project_setup_py_test("hello-pure", ["bdist_wheel"], disable_languages_test=True):
        expected_content = ["hello/__init__.py"]

        expected_distribution_name = "hello_pure-1.2.3"

        whls = glob.glob("dist/*.whl")
        assert len(whls) == 1
        check_wheel_content(whls[0], expected_distribution_name, expected_content, pure=True)


def test_hello_clean(capfd, project_setup_py_test):
    with push_dir():
        with project_setup_py_test("hello-pure", ["build"], disable_languages_test=True) as tmp_dir:
            pass

        assert (tmp_dir / SKBUILD_DIR()).exists()

        with project_setup_py_test("hello-pure", ["clean"], tmp_dir=tmp_dir, disable_languages_test=True):
            pass

        assert not (tmp_dir / SKBUILD_DIR()).exists()

        out = capfd.readouterr()[0]
        assert "Build files have been written to" not in out
