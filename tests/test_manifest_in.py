#!/usr/bin/env python

"""test_manifest_in
----------------------------------

Tries to build and test the `manifest-in` sample project.
"""

import glob

import pytest

from . import project_setup_py_test
from .pytest_helpers import check_sdist_content, check_wheel_content


@pytest.mark.nosetuptoolsscm
@project_setup_py_test("manifest-in", ["sdist"], disable_languages_test=True)
def test_manifest_in_sdist():
    sdists_tar = glob.glob("dist/*.tar.gz")
    sdists_zip = glob.glob("dist/*.zip")
    assert sdists_tar or sdists_zip

    expected_content = [
        "manifest-in-1.2.3/hello/__init__.py",
        "manifest-in-1.2.3/setup.py",
        "manifest-in-1.2.3/MANIFEST.in",
    ]

    sdist_archive = "dist/manifest-in-1.2.3.zip"
    if sdists_tar:
        sdist_archive = "dist/manifest-in-1.2.3.tar.gz"

    check_sdist_content(sdist_archive, "manifest-in-1.2.3", expected_content)


@project_setup_py_test("manifest-in", ["bdist_wheel"], disable_languages_test=True)
def test_manifest_in_wheel():
    whls = glob.glob("dist/*.whl")
    assert len(whls) == 1

    expected_content = ["hello/__init__.py"]

    expected_distribution_name = "manifest_in-1.2.3"

    check_wheel_content(whls[0], expected_distribution_name, expected_content, pure=True)
