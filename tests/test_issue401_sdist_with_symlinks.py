from __future__ import annotations

import glob
import pathlib
import sys
import tarfile

import pytest

from .pytest_helpers import check_sdist_content


@pytest.mark.nosetuptoolsscm
@pytest.mark.skipif(sys.platform == "win32", reason="Symlinks not supported on Windows")
def test_sdist_with_symlinks(project_setup_py_test):
    with project_setup_py_test("issue-401-sdist-with-symlinks", ["sdist"]):
        assert pathlib.Path("VERSION").is_symlink()

        sdists_tar = glob.glob("dist/*.tar.gz")
        sdists_zip = glob.glob("dist/*.zip")
        assert sdists_tar or sdists_zip

        expected_content = [
            "hello-1.2.3/MANIFEST.in",
            "hello-1.2.3/README",
            "hello-1.2.3/setup.py",
            "hello-1.2.3/VERSION",
        ]

        if sdists_tar:
            check_sdist_content(sdists_tar[0], "hello-1.2.3", expected_content)

            with tarfile.open(sdists_tar[0], "r:gz") as tf:
                member_list = tf.getnames()
                assert "hello-1.2.3/VERSION" in member_list
                mbr = tf.getmember("hello-1.2.3/VERSION")
                assert not mbr.issym()
        elif sdists_zip:
            check_sdist_content(sdists_zip[0], "hello-1.2.3", expected_content)
