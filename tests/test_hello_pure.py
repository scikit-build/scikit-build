"""test_hello_pure
----------------------------------

Tries to build and test the `hello-pure` sample project.
"""

from __future__ import annotations

import glob

from skbuild.constants import SKBUILD_DIR
from skbuild.utils import push_dir

from . import project_setup_py_test
from .pytest_helpers import check_sdist_content, check_wheel_content


@project_setup_py_test("hello-pure", ["build"], disable_languages_test=True)
def test_hello_pure_builds(capsys):
    out, _ = capsys.readouterr()
    assert "skipping skbuild (no CMakeLists.txt found)" in out


@project_setup_py_test("hello-pure", ["sdist"], disable_languages_test=True)
def test_hello_pure_sdist():
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


@project_setup_py_test("hello-pure", ["bdist_wheel"], disable_languages_test=True)
def test_hello_pure_wheel():
    expected_content = ["hello/__init__.py"]

    expected_distribution_name = "hello_pure-1.2.3"

    whls = glob.glob("dist/*.whl")
    assert len(whls) == 1
    check_wheel_content(whls[0], expected_distribution_name, expected_content, pure=True)


def test_hello_clean(capfd):
    with push_dir():

        @project_setup_py_test("hello-pure", ["build"], disable_languages_test=True, ret=True)
        def run_build():
            pass

        tmp_dir = run_build()[0]

        assert tmp_dir.join(SKBUILD_DIR()).exists()

        @project_setup_py_test("hello-pure", ["clean"], tmp_dir=tmp_dir, disable_languages_test=True)
        def run_clean():
            pass

        run_clean()

        assert not tmp_dir.join(SKBUILD_DIR()).exists()

        out = capfd.readouterr()[0]
        assert "Build files have been written to" not in out
