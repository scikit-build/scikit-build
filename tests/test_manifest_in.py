"""test_manifest_in
----------------------------------

Tries to build and test the `manifest-in` sample project.
"""

from __future__ import annotations

import glob

import pytest

from . import project_setup_py_test
from .pytest_helpers import check_sdist_content, check_wheel_content


@pytest.mark.nosetuptoolsscm()
@project_setup_py_test("manifest-in", ["sdist"], disable_languages_test=True)
def test_manifest_in_sdist():
    sdists_tar = glob.glob("dist/*.tar.gz")
    sdists_zip = glob.glob("dist/*.zip")
    assert sdists_tar or sdists_zip

    dirname = "manifest-in-1.2.3"
    # setuptools 69.3.0 and above now canonicalize the filename as well.
    if any("manifest_in" in x for x in sdists_zip + sdists_tar):
        dirname = "manifest_in-1.2.3"

    expected_content = [
        f"{dirname}/hello/__init__.py",
        f"{dirname}/setup.py",
        f"{dirname}/MANIFEST.in",
    ]

    sdist_archive = f"dist/{dirname}.zip"
    if sdists_tar:
        sdist_archive = f"dist/{dirname}.tar.gz"

    check_sdist_content(sdist_archive, dirname, expected_content)


@project_setup_py_test("manifest-in", ["bdist_wheel"], disable_languages_test=True)
def test_manifest_in_wheel():
    whls = glob.glob("dist/*.whl")
    assert len(whls) == 1

    expected_content = ["hello/__init__.py"]

    expected_distribution_name = "manifest_in-1.2.3"

    check_wheel_content(whls[0], expected_distribution_name, expected_content, pure=True)
