import os
import textwrap

import pytest

import skbuild
from skbuild.constants import CMAKE_BUILD_DIR

from . import _tmpdir, execute_setup_py


def test_isolated_env_trigger_reconfigure(mocker):

    tmp_dir = _tmpdir("isolated_env_trigger_reconfigure")

    tmp_dir.join("setup.py").write(
        textwrap.dedent(
            """
        from skbuild import setup
        setup(
            name="test_isolated_env_trigger_reconfigure",
            version="1.2.3",
            description="A minimal example package",
            author="The scikit-build team",
            license="MIT",
        )
        """
        )
    )
    tmp_dir.join("CMakeLists.txt").write(
        textwrap.dedent(
            """
        message(FATAL_ERROR "This error message should not be displayed")
        """
        )
    )

    #
    # mock configure
    #
    def fake_configure(*args, **kwargs):
        # Simulate a successful configuration creating a CMakeCache.txt
        tmp_dir.ensure(CMAKE_BUILD_DIR(), dir=1).join("CMakeCache.txt").write(
            textwrap.dedent(
                """
            //Name of generator.
            CMAKE_GENERATOR:INTERNAL=Ninja
            """
            )
        )

    # Skip real configuration creating the CMakeCache.txt expected by
    # "skbuild.setuptools_wrap._load_cmake_spec()" function
    mocker.patch("skbuild.cmaker.CMaker.configure", new=fake_configure)

    #
    # mock _save_cmake_spec
    #
    _save_cmake_spec_original = skbuild.setuptools_wrap._save_cmake_spec

    exit_after_saving_cmake_spec = "exit skbuild saving cmake spec"

    def _save_cmake_spec_mock(args):
        _save_cmake_spec_original(args)
        raise RuntimeError(exit_after_saving_cmake_spec)

    mocker.patch("skbuild.setuptools_wrap._save_cmake_spec", new=_save_cmake_spec_mock)

    #
    # mock make
    #
    exit_before_running_cmake = "exit skbuild running make"
    mocker.patch("skbuild.cmaker.CMaker.make", side_effect=RuntimeError(exit_before_running_cmake))

    # first build: "configure" and "_save_cmake_spec" are expected to be called
    with pytest.raises(RuntimeError, match=exit_after_saving_cmake_spec):
        with execute_setup_py(tmp_dir, ["build"], disable_languages_test=True):
            pass

    # second build: no reconfiguration should happen, only "make" is expected to be called
    with pytest.raises(RuntimeError, match=exit_before_running_cmake):
        with execute_setup_py(tmp_dir, ["build"], disable_languages_test=True):
            pass

    # since pip updates PYTHONPATH with the temporary path
    # where the project dependencies are installed, we simulate
    # this by updating the corresponding environment variable.
    os.environ["PYTHONPATH"] = "/path/to/anything"

    # after updating the env, reconfiguration is expected
    with pytest.raises(RuntimeError, match=exit_after_saving_cmake_spec):
        with execute_setup_py(tmp_dir, ["build"], disable_languages_test=True):
            pass

    # no reconfiguration should happen
    with pytest.raises(RuntimeError, match=exit_before_running_cmake):
        with execute_setup_py(tmp_dir, ["build"], disable_languages_test=True):
            pass

    # this is the other variable set by pip when doing isolated build
    os.environ["PYTHONNOUSERSITE"] = "1"

    # after updating the env, reconfiguration is expected
    with pytest.raises(RuntimeError, match=exit_after_saving_cmake_spec):
        with execute_setup_py(tmp_dir, ["build"], disable_languages_test=True):
            pass

    # no reconfiguration should happen
    with pytest.raises(RuntimeError, match=exit_before_running_cmake):
        with execute_setup_py(tmp_dir, ["build"], disable_languages_test=True):
            pass
