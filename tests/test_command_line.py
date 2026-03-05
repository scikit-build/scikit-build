"""test_command_line
----------------------------------

Tests for various command line functionality.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from skbuild.constants import CMAKE_BUILD_DIR
from skbuild.exceptions import SKBuildError
from skbuild.utils import push_dir, to_platform_path

from . import (
    execute_setup_py,
    get_cmakecache_variables,
    initialize_git_repo_and_commit,
    prepare_project,
)


def test_help(capsys, project_setup_py_test):
    with project_setup_py_test("hello-no-language", ["--help"], disable_languages_test=True):
        out, _ = capsys.readouterr()
        assert "scikit-build options" not in out
        assert "Global options:" in out
        assert "usage:" in out


def test_help_commands(capsys, project_setup_py_test):
    with project_setup_py_test("hello-no-language", ["--help-commands"], disable_languages_test=True):
        out, _ = capsys.readouterr()
        assert "scikit-build options" in out
        assert "--build-type" in out
        assert "Global options:" not in out
        assert "usage:" in out


def test_metadata_display(capsys, project_setup_py_test):
    with project_setup_py_test("hello-no-language", ["--author", "--name"], disable_languages_test=True):
        out, _ = capsys.readouterr()
        assert "scikit-build options" not in out
        assert "Global options:" not in out
        assert "usage:" not in out
        assert out.splitlines()[0] == "The scikit-build team"
        assert out.splitlines()[1] == "hello_no_language"


def test_no_command(project_setup_py_test):
    with push_dir():
        failed = False
        try:
            with project_setup_py_test("hello-no-language", [], disable_languages_test=True):
                pass
        except SystemExit as e:
            failed = "error: no commands supplied" in e.args[0]

        assert failed
        assert not Path("_skbuild").exists()


def test_invalid_command(project_setup_py_test):
    with push_dir():
        failed = False
        try:
            with project_setup_py_test("hello-no-language", ["unknown"], disable_languages_test=True):
                pass
        except SystemExit as e:
            failed = "error: invalid command" in e.args[0]

        assert failed
        assert not Path("_skbuild").exists()


def test_too_many_separators(project_setup_py_test):
    with push_dir():
        failed = False
        try:
            with project_setup_py_test("hello-no-language", ["--"] * 3, disable_languages_test=True):
                pass
        except SystemExit as e:
            failed = e.args[0].startswith("ERROR: Too many")

        assert failed


def test_cmake_initial_cache_as_global_option(tmp_path):
    project = "hello-no-language"
    prepare_project(project, tmp_path)
    initialize_git_repo_and_commit(tmp_path, verbose=True)

    initial_cache = tmp_path / "initial-cache.txt"
    initial_cache.write_text("""set(MY_CMAKE_VARIABLE "1" CACHE BOOL "My cache variable")""")

    try:
        with execute_setup_py(tmp_path, [f"-C{initial_cache}", "build"], disable_languages_test=True):
            pass
    except SystemExit as exc:
        assert exc.code == 0  # noqa: PT017

    cmakecache_txt = tmp_path / CMAKE_BUILD_DIR() / "CMakeCache.txt"
    assert cmakecache_txt.exists()
    assert get_cmakecache_variables(cmakecache_txt).get("MY_CMAKE_VARIABLE", (None, None)) == ("BOOL", "1")


def test_cmake_executable_arg(project_setup_py_test):
    cmake_executable = "/path/to/invalid/cmake"

    failed = False
    message = ""
    try:
        with project_setup_py_test(
            "hello-no-language", ["--cmake-executable", cmake_executable, "build"], disable_languages_test=True
        ):
            pass
    except SystemExit as e:
        failed = isinstance(e.code, SKBuildError)
        message = str(e)

    assert failed
    assert f"Problem with the CMake installation, aborting build. CMake executable is {cmake_executable}" in message


@pytest.mark.parametrize("action", ["sdist", "bdist_wheel"])
@pytest.mark.parametrize("hide_listing", [True, False])
def test_hide_listing(action, hide_listing, capfd, caplog, project_setup_py_test):
    cmd = [action]
    if hide_listing:
        cmd.insert(0, "--hide-listing")

    with project_setup_py_test("test-hide-listing", cmd, verbose_git=False, disable_languages_test=True):
        pass

    out, err = capfd.readouterr()
    out += err + caplog.text

    if hide_listing:
        assert to_platform_path("bonjour/__init__.py") not in out
    else:
        assert to_platform_path("bonjour/__init__.py") in out

    if action == "sdist":
        assert "copied 15 files" in out
    elif action == "bdist_wheel":
        assert "copied 6 files" in out  # build_py
        assert "copied 9 files" in out  # install_lib
        assert "copied 0 files" in out  # install_scripts


def test_run_cmake_arg(capfd, project_setup_py_test):
    with project_setup_py_test("hello-no-language", ["--force-cmake", "--help"], disable_languages_test=True):
        out, _ = capfd.readouterr()
        assert "Generating done" in out


def test_skip_cmake_arg(capfd, project_setup_py_test):
    with project_setup_py_test("hello-no-language", ["--skip-cmake", "build"], disable_languages_test=True):
        out, _ = capfd.readouterr()
        assert "Generating done" not in out
