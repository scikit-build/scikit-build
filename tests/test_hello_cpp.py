#!/usr/bin/env python

"""test_hello_cpp
----------------------------------

Tries to build and test the `hello-cpp` sample project.
"""

import glob
import os

import pytest

from skbuild.constants import CMAKE_BUILD_DIR, SKBUILD_DIR
from skbuild.utils import push_dir

from . import SAMPLES_DIR, _copy_dir, _tmpdir, get_ext_suffix, project_setup_py_test
from .pytest_helpers import check_sdist_content, check_wheel_content


def test_hello_builds():
    with push_dir():

        @project_setup_py_test("hello-cpp", ["build"], ret=True)
        def run():
            pass

        # Check that a project can be build twice in a row
        # See issue scikit-build#120
        tmp_dir = run()[0]

        @project_setup_py_test("hello-cpp", ["build"], tmp_dir=tmp_dir)
        def another_run():
            pass

        another_run()


# @project_setup_py_test("hello-cpp", ["test"])
# def test_hello_works():
#     pass


@project_setup_py_test("hello-cpp", ["sdist"])
def test_hello_sdist():
    sdists_tar = glob.glob("dist/*.tar.gz")
    sdists_zip = glob.glob("dist/*.zip")
    assert sdists_tar or sdists_zip

    expected_content = [
        "hello-1.2.3/CMakeLists.txt",
        "hello-1.2.3/bonjour/__init__.py",
        "hello-1.2.3/bonjour/data/ciel.txt",
        "hello-1.2.3/bonjour/data/soleil.txt",
        "hello-1.2.3/bonjour/data/terre.txt",
        "hello-1.2.3/bonjourModule.py",
        "hello-1.2.3/hello/_hello.cxx",
        "hello-1.2.3/hello/CMakeLists.txt",
        "hello-1.2.3/hello/__init__.py",
        "hello-1.2.3/hello/__main__.py",
        "hello-1.2.3/setup.py",
    ]

    sdist_archive = "dist/hello-1.2.3.zip"
    if sdists_tar:
        sdist_archive = "dist/hello-1.2.3.tar.gz"

    check_sdist_content(sdist_archive, "hello-1.2.3", expected_content)


def test_hello_wheel():
    expected_content = [
        "hello/_hello%s" % get_ext_suffix(),
        "hello/__init__.py",
        "hello/__main__.py",
        "hello/world.py",
        "helloModule.py",
        "bonjour/__init__.py",
        "bonjour/data/ciel.txt",
        "bonjour/data/soleil.txt",
        "bonjour/data/terre.txt",
        "bonjourModule.py",
    ]

    expected_distribution_name = "hello-1.2.3"

    @project_setup_py_test("hello-cpp", ["bdist_wheel"], ret=True)
    def build_wheel():
        whls = glob.glob("dist/*.whl")
        assert len(whls) == 1
        check_wheel_content(whls[0], expected_distribution_name, expected_content)
        os.remove(whls[0])
        assert not os.path.exists(whls[0])

        assert os.path.exists(os.path.join(CMAKE_BUILD_DIR(), "CMakeCache.txt"))
        os.remove(os.path.join(CMAKE_BUILD_DIR(), "CMakeCache.txt"))

    tmp_dir = build_wheel()[0]

    @project_setup_py_test("hello-cpp", ["--skip-cmake", "bdist_wheel"], tmp_dir=tmp_dir)
    def build_wheel_skip_cmake():
        assert not os.path.exists(os.path.join(CMAKE_BUILD_DIR(), "CMakeCache.txt"))
        whls = glob.glob("dist/*.whl")
        assert len(whls) == 1
        check_wheel_content(whls[0], expected_distribution_name, expected_content)

    build_wheel_skip_cmake()


@pytest.mark.parametrize("dry_run", ["with-dry-run", "without-dry-run"])
def test_hello_clean(dry_run, capfd):
    with push_dir():

        dry_run = dry_run == "with-dry-run"

        @project_setup_py_test("hello-cpp", ["build"], ret=True)
        def run_build():
            pass

        tmp_dir = run_build()[0]

        assert tmp_dir.join(SKBUILD_DIR()).exists()

        # XXX Since using capfd.disabled() context manager prevents
        # the output from being captured atfer it exits, we display
        # a separator allowing to differentiate the build and clean output.
        print("<<-->>")

        clean_args = ["clean"]
        if dry_run:
            clean_args.append("--dry-run")

        @project_setup_py_test("hello-cpp", clean_args, tmp_dir=tmp_dir)
        def run_clean():
            pass

        run_clean()

        if not dry_run:
            assert not tmp_dir.join(SKBUILD_DIR()).exists()
        else:
            assert tmp_dir.join(SKBUILD_DIR()).exists()

        build_out, clean_out = capfd.readouterr()[0].split("<<-->>")
        assert "Build files have been written to" in build_out
        assert "Build files have been written to" not in clean_out


def test_hello_cleans(capfd, caplog):
    with push_dir():

        tmp_dir = _tmpdir("test_hello_cleans")

        _copy_dir(tmp_dir, os.path.join(SAMPLES_DIR, "hello-cpp"))

        @project_setup_py_test("hello-cpp", ["build"], tmp_dir=tmp_dir)
        def run_build():
            pass

        @project_setup_py_test("hello-cpp", ["clean"], tmp_dir=tmp_dir)
        def run_clean():
            pass

        # Check that a project can be cleaned twice in a row
        run_build()
        capfd.readouterr()
        caplog.clear()

        run_clean()
        txt1 = caplog.text
        msg = capfd.readouterr().out + txt1
        assert "running clean" in msg
        caplog.clear()

        run_clean()
        txt2 = caplog.text
        msg = capfd.readouterr().out + txt2
        assert "running clean" in msg


@pytest.mark.deprecated
@project_setup_py_test("hello-cpp", ["develop"])
def test_hello_develop():
    for expected_file in [
        # These files are the "regular" source files
        "setup.py",
        "CMakeLists.txt",
        "bonjour/__init__.py",
        "bonjourModule.py",
        "hello/__init__.py",
        "hello/__main__.py",
        "hello/_hello.cxx",
        "hello/CMakeLists.txt",
        # These files are "generated" by CMake and
        # are copied from CMAKE_INSTALL_DIR
        "hello/_hello%s" % get_ext_suffix(),
        "hello/world.py",
        "helloModule.py",
    ]:
        assert os.path.exists(expected_file)
