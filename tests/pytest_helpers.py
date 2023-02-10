import sys
import tarfile
from zipfile import ZipFile

import wheel
from pkg_resources import parse_version

from skbuild import __version__ as skbuild_version

from . import list_ancestors


def check_sdist_content(sdist_archive, expected_distribution_name, expected_content, package_dir=""):
    """This function raises an AssertionError if the given sdist_archive
    does not have the expected content.
    """
    sdist_zip = sdist_archive.endswith(".zip")
    sdist_tar = sdist_archive.endswith(".tar.gz")
    assert sdist_zip or sdist_tar

    expected_content = list(expected_content)

    expected_name = "_".join(expected_distribution_name.split("-")[:-1])

    if not package_dir:
        egg_info_dir = f"{expected_distribution_name}/{expected_name}.egg-info"
    else:
        egg_info_dir = f"{expected_distribution_name}/{package_dir}/{expected_name}.egg-info"

    expected_content += [
        f"{expected_distribution_name}/PKG-INFO",
        f"{expected_distribution_name}/setup.cfg",
        f"{egg_info_dir}/dependency_links.txt",
        f"{egg_info_dir}/top_level.txt",
        f"{egg_info_dir}/PKG-INFO",
        f"{egg_info_dir}/SOURCES.txt",
    ]

    if sdist_zip and ((3, 6, 7) < sys.version_info[:3] < (3, 7, 0) or sys.version_info[:3] > (3, 7, 1)):
        # Add directory entries in ZIP files created by distutils.
        # See https://github.com/python/cpython/pull/9419
        directories = set()
        for entry in expected_content:
            directories = directories.union([entry + "/" for entry in list_ancestors(entry)])
        expected_content += directories

    member_list = []
    if sdist_zip:
        member_list = ZipFile(sdist_archive).namelist()
    elif sdist_tar:
        with tarfile.open(sdist_archive) as tf:
            member_list = [member.name for member in tf.getmembers() if not member.isdir()]

    assert sorted(expected_content) == sorted(member_list)


def check_wheel_content(wheel_archive, expected_distribution_name, expected_content, pure=False):
    """This function raises an AssertionError if the given wheel_archive
    does not have the expected content.

    Note that this function already takes care of appending the
    ``<expected_distribution_name>.dist-info`` files to the ``expected_content``
    list.
    """

    expected_content = list(expected_content)
    expected_content += [
        f"{expected_distribution_name}.dist-info/top_level.txt",
        f"{expected_distribution_name}.dist-info/WHEEL",
        f"{expected_distribution_name}.dist-info/RECORD",
        f"{expected_distribution_name}.dist-info/METADATA",
    ]

    if parse_version(wheel.__version__) < parse_version("0.31.0"):
        # These files were specified in the now-withdrawn PEP 426
        # See https://github.com/pypa/wheel/issues/195
        expected_content += [
            f"{expected_distribution_name}.dist-info/DESCRIPTION.rst",
            f"{expected_distribution_name}.dist-info/metadata.json",
        ]

    if parse_version("0.33.1") < parse_version(wheel.__version__) < parse_version("0.33.4"):
        # Include directory entries when building wheel
        # See https://github.com/pypa/wheel/issues/287 and https://github.com/pypa/wheel/issues/294
        directories = set()
        for entry in expected_content:
            directories = directories.union([entry + "/" for entry in list_ancestors(entry)])
        expected_content += directories

    if pure:
        assert wheel_archive.endswith("-none-any.whl")
    else:
        assert not wheel_archive.endswith("-none-any.whl")

    archive = ZipFile(wheel_archive)
    member_list = archive.namelist()

    assert sorted(expected_content) == sorted(member_list)

    # PEP-0427: Generator is the name and optionally the version of the
    # software that produced the archive.
    # See https://www.python.org/dev/peps/pep-0427/#file-contents
    current_generator = None
    with archive.open(f"{expected_distribution_name}.dist-info/WHEEL") as wheel_file:
        for line in wheel_file:
            if line.startswith(b"Generator"):
                current_generator = line.split(b":")[1].strip()
                break
    assert current_generator == f"skbuild {skbuild_version}".encode()
