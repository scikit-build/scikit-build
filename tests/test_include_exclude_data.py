from __future__ import annotations

import glob
import os

import pytest

from skbuild.utils import to_unix_path

from . import project_setup_py_test
from .pytest_helpers import check_sdist_content, check_wheel_content


def check_whls(project_name):
    whls = glob.glob("dist/*.whl")
    assert len(whls) == 1
    assert not whls[0].endswith("-none-any.whl")

    expected_content = [
        "hello/__init__.py",
        "hello/cmake_generated_module.py",
        "hello/data/subdata/hello_data1_include_from_manifest.txt",
        "hello/data/subdata/hello_data2_include_from_manifest.txt",
        "hello/data/subdata/hello_data3_cmake_generated.txt",
        "hello/hello_data1_cmake_generated.txt",
        "hello/hello_data2_cmake_generated.txt",
        "hello/hello_include_from_manifest.txt",
        "hello2/__init__.py",
        "hello2/hello2_data1_cmake_generated.txt",
        "hello2/hello2_data2_cmake_generated.txt",
        "hello2/data2/subdata2/hello2_data3_cmake_generated.txt",
        "hello2/data2/subdata2/hello2_data1_include_from_manifest.txt",
        "hello2/data2/subdata2/hello2_data2_include_from_manifest.txt",
        "hello2/hello2_include_from_manifest.txt",
    ]

    expected_distribution_name = project_name

    check_wheel_content(whls[0], expected_distribution_name, expected_content)


def check_sdist(proj, base=""):
    sdists_tar = glob.glob("dist/*.tar.gz")
    sdists_zip = glob.glob("dist/*.zip")
    assert sdists_tar or sdists_zip

    expected_content = [
        to_unix_path(os.path.join(proj, "setup.py")),
        to_unix_path(os.path.join(proj, base, "hello/__init__.py")),
        to_unix_path(os.path.join(proj, base, "hello/data/subdata/hello_data1_include_from_manifest.txt")),
        to_unix_path(os.path.join(proj, base, "hello/data/subdata/hello_data2_include_from_manifest.txt")),
        to_unix_path(
            os.path.join(proj, base, "hello/data/subdata/hello_data4_include_from_manifest_and_exclude_from_setup.txt")
        ),
        to_unix_path(os.path.join(proj, base, "hello/hello_include_from_manifest.txt")),
        to_unix_path(os.path.join(proj, base, "hello2/__init__.py")),
        to_unix_path(os.path.join(proj, base, "hello2/data2/subdata2/hello2_data1_include_from_manifest.txt")),
        to_unix_path(os.path.join(proj, base, "hello2/data2/subdata2/hello2_data2_include_from_manifest.txt")),
        to_unix_path(
            os.path.join(
                proj, base, "hello2/data2/subdata2/hello2_data4_include_from_manifest_and_exclude_from_setup.txt"
            )
        ),
        to_unix_path(os.path.join(proj, base, "hello2/hello2_include_from_manifest.txt")),
    ]

    sdist_archive = f"dist/{proj}.zip"
    if sdists_tar:
        sdist_archive = f"dist/{proj}.tar.gz"

    check_sdist_content(sdist_archive, proj, expected_content, package_dir=base)


@project_setup_py_test("test-include-exclude-data", ["bdist_wheel"])
def test_include_exclude_data():
    check_whls("test_include_exclude_data-0.1.0")


@pytest.mark.nosetuptoolsscm()
@project_setup_py_test("test-include-exclude-data", ["sdist"])
def test_hello_sdist():
    check_sdist("test_include_exclude_data-0.1.0")


@project_setup_py_test("test-include-exclude-data-with-base", ["bdist_wheel"])
def test_include_exclude_data_with_base():
    check_whls("test_include_exclude_data_with_base-0.1.0")


@pytest.mark.nosetuptoolsscm()
@project_setup_py_test("test-include-exclude-data-with-base", ["sdist"])
def test_hello_sdist_with_base():
    check_sdist("test_include_exclude_data_with_base-0.1.0", base="src")
