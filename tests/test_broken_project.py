"""test_broken_cmakelists
----------------------------------

Tries to build the `fail-with-*-cmakelists` sample projects.  Ensures that the
attempt fails with a SystemExit exception that has an SKBuildError exception as
its value.
"""

from __future__ import annotations

from subprocess import CalledProcessError, run

import pytest

from skbuild.constants import CMAKE_DEFAULT_EXECUTABLE
from skbuild.exceptions import SKBuildError
from skbuild.platform_specifics import CMakeGenerator, get_platform
from skbuild.utils import push_dir

from . import push_env


def test_cmakelists_with_fatalerror_fails(capfd, project_setup_py_test):
    with push_dir():
        with pytest.raises(SystemExit) as excinfo:
            with project_setup_py_test("fail-with-fatal-error-cmakelists", ["build"], disable_languages_test=True):
                pass

        e = excinfo.value
        assert isinstance(e.code, SKBuildError)

    _, err = capfd.readouterr()
    assert "Invalid CMakeLists.txt" in err
    assert "An error occurred while configuring with CMake." in str(e)


def test_cmakelists_with_syntaxerror_fails(capfd, project_setup_py_test):
    with push_dir():
        with pytest.raises(SystemExit) as excinfo:
            with project_setup_py_test("fail-with-syntax-error-cmakelists", ["build"], disable_languages_test=True):
                pass

        e = excinfo.value
        assert isinstance(e.code, SKBuildError)

    _, err = capfd.readouterr()
    assert 'Parse error.  Function missing ending ")"' in err
    assert "An error occurred while configuring with CMake." in str(e)


def test_hello_with_compileerror_fails(capfd, project_setup_py_test):
    with push_dir():
        with pytest.raises(SystemExit) as excinfo:
            with project_setup_py_test("fail-hello-with-compile-error", ["build"]):
                pass

        e = excinfo.value
        assert isinstance(e.code, SKBuildError)

    out, err = capfd.readouterr()
    assert "_hello.cxx" in out or "_hello.cxx" in err
    assert "An error occurred while building with CMake." in str(e)


@pytest.mark.parametrize("exception", [CalledProcessError, OSError])
def test_invalid_cmake(exception, mocker, project_setup_py_test):
    exceptions = {
        OSError: OSError("Unknown error"),
        CalledProcessError: CalledProcessError(1, [CMAKE_DEFAULT_EXECUTABLE, "--version"]),
    }

    run_original = run

    def run_mock(*args, **kwargs):
        if args[0] == [CMAKE_DEFAULT_EXECUTABLE, "--version"]:
            raise exceptions[exception]
        return run_original(*args, **kwargs)

    mocker.patch("skbuild.cmaker.subprocess.run", new=run_mock)

    with push_dir():
        with pytest.raises(SystemExit) as excinfo:
            with project_setup_py_test("hello-no-language", ["build"], disable_languages_test=True):
                pass

        e = excinfo.value
        assert isinstance(e.code, SKBuildError)

    assert "Problem with the CMake installation, aborting build." in str(e)


def test_first_invalid_generator(mocker, capfd, project_setup_py_test):
    platform = get_platform()
    default_generators = [CMakeGenerator("Invalid")]
    default_generators.extend(platform.default_generators)
    mocker.patch.object(
        type(platform), "default_generators", new_callable=mocker.PropertyMock, return_value=default_generators
    )

    mocker.patch("skbuild.cmaker.get_platform", return_value=platform)

    with push_dir(), push_env(CMAKE_GENERATOR=None):
        with project_setup_py_test("hello-no-language", ["build"]):
            pass

    _, err = capfd.readouterr()
    assert "CMake Error: Could not create named generator Invalid" in err


def test_invalid_generator(mocker, capfd, project_setup_py_test):
    platform = get_platform()
    mocker.patch.object(
        type(platform), "default_generators", new_callable=mocker.PropertyMock, return_value=[CMakeGenerator("Invalid")]
    )
    mocker.patch("skbuild.cmaker.get_platform", return_value=platform)

    with push_dir(), push_env(CMAKE_GENERATOR=None):
        with pytest.raises(SystemExit) as excinfo:
            with project_setup_py_test("hello-no-language", ["build"]):
                pass

        e = excinfo.value
        assert isinstance(e.code, SKBuildError)

    _, err = capfd.readouterr()

    assert "CMake Error: Could not create named generator Invalid" in err
    assert "scikit-build could not get a working generator for your system. Aborting build." in str(e)
