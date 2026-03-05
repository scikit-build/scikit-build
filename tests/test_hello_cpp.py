"""test_hello_cpp
----------------------------------

Tries to build and test the `hello-cpp` sample project.
"""

from __future__ import annotations

import glob
import os
from pathlib import Path

from skbuild.constants import CMAKE_BUILD_DIR, SKBUILD_DIR
from skbuild.utils import push_dir

from . import SAMPLES_DIR, _copy_dir, _tmpdir, get_ext_suffix
from .pytest_helpers import check_sdist_content, check_wheel_content


def test_hello_builds(project_setup_py_test):
    with push_dir():
        # Check that a project can be build twice in a row
        # See issue scikit-build#120
        with project_setup_py_test("hello-cpp", ["build"]) as tmp_dir:
            pass

        with project_setup_py_test("hello-cpp", ["build"], tmp_dir=tmp_dir):
            pass


def test_hello_sdist(project_setup_py_test):
    with project_setup_py_test("hello-cpp", ["sdist"]):
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


def test_hello_wheel(project_setup_py_test):
    expected_content = [
        f"hello/_hello{get_ext_suffix()}",
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

    with project_setup_py_test("hello-cpp", ["bdist_wheel"]) as tmp_dir:
        whls = glob.glob("dist/*.whl")
        assert len(whls) == 1
        check_wheel_content(whls[0], expected_distribution_name, expected_content)
        os.remove(whls[0])
        assert not Path(whls[0]).exists()

        cmake_cache = Path(CMAKE_BUILD_DIR()) / "CMakeCache.txt"
        assert cmake_cache.exists()
        cmake_cache.unlink()

    with project_setup_py_test("hello-cpp", ["--skip-cmake", "bdist_wheel"], tmp_dir=tmp_dir):
        assert not (Path(CMAKE_BUILD_DIR()) / "CMakeCache.txt").exists()
        whls = glob.glob("dist/*.whl")
        assert len(whls) == 1
        check_wheel_content(whls[0], expected_distribution_name, expected_content)


def test_hello_clean(capfd, project_setup_py_test):
    with push_dir():
        with project_setup_py_test("hello-cpp", ["build"]) as tmp_dir:
            pass

        assert (tmp_dir / SKBUILD_DIR()).exists()

        # XXX Since using capfd.disabled() context manager prevents
        # the output from being captured after it exits, we display
        # a separator allowing to differentiate the build and clean output.
        print("<<-->>")

        clean_args = ["clean"]

        with project_setup_py_test("hello-cpp", clean_args, tmp_dir=tmp_dir):
            pass

        assert not (tmp_dir / SKBUILD_DIR()).exists()

        build_out, clean_out = capfd.readouterr()[0].split("<<-->>")
        assert "Build files have been written to" in build_out
        assert "Build files have been written to" not in clean_out


def test_hello_cleans(capfd, caplog, project_setup_py_test):
    with push_dir():
        tmp_dir = _tmpdir("test_hello_cleans")

        _copy_dir(tmp_dir, SAMPLES_DIR / "hello-cpp")

        # Check that a project can be cleaned twice in a row
        with project_setup_py_test("hello-cpp", ["build"], tmp_dir=tmp_dir):
            pass
        capfd.readouterr()
        caplog.clear()

        with project_setup_py_test("hello-cpp", ["clean"], tmp_dir=tmp_dir):
            pass
        txt1 = caplog.text
        msg = capfd.readouterr().out + txt1
        assert "running clean" in msg
        caplog.clear()

        with project_setup_py_test("hello-cpp", ["clean"], tmp_dir=tmp_dir):
            pass
        txt2 = caplog.text
        msg = capfd.readouterr().out + txt2
        assert "running clean" in msg
