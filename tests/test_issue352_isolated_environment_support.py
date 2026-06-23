from __future__ import annotations

import textwrap

import pytest

from . import _tmpdir, cmake_build_dir, execute_setup_py, push_env


def test_isolated_env_trigger_reconfigure(mocker):
    tmp_dir = _tmpdir("isolated_env_trigger_reconfigure")

    (tmp_dir / "setup.py").write_text(
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
    (tmp_dir / "CMakeLists.txt").write_text(
        textwrap.dedent(
            """
        message(FATAL_ERROR "This error message should not be displayed")
        """
        )
    )

    #
    # mock configure
    #
    configure_calls = []

    def fake_configure(self, *args, **kwargs):
        # Simulate a successful configuration creating a CMakeCache.txt
        cmakecache = self.config.build_dir / "CMakeCache.txt"
        cmakecache.parent.mkdir(parents=True, exist_ok=True)
        cmakecache.write_text(
            textwrap.dedent(
                """
            //Name of generator.
            CMAKE_GENERATOR:INTERNAL=Ninja
            """
            )
        )
        configure_calls.append((args, kwargs))

    mocker.patch("scikit_build_core.setuptools.build_cmake.Builder.configure", new=fake_configure)

    #
    # mock build
    #
    exit_before_running_make = "exit skbuild before running make"
    mocker.patch(
        "scikit_build_core.setuptools.build_cmake.Builder.build",
        side_effect=RuntimeError(exit_before_running_make),
    )

    # first build: "configure" is expected to be called
    with pytest.raises(RuntimeError, match=exit_before_running_make), execute_setup_py(tmp_dir, ["build"]):
        pass
    assert len(configure_calls) == 1

    build_dir = cmake_build_dir(tmp_dir)
    assert build_dir is not None
    assert (build_dir / "CMakeCache.txt").exists()

    # pip updates PYTHONPATH with the temporary path where the project
    # dependencies are installed when doing an isolated build. We simulate
    # this by updating the corresponding environment variable and check that
    # the following build (re)configures the project so that the tools
    # (e.g cmake, ninja) from the isolated environment are picked up.
    #
    # Note: the scikit-build-core backend always reconfigures (it does not
    # cache a "cmake spec" like classic scikit-build did), so a changed
    # isolated environment can never result in a stale configuration.
    with push_env(PYTHONPATH="/path/to/anything"):
        with pytest.raises(RuntimeError, match=exit_before_running_make), execute_setup_py(tmp_dir, ["build"]):
            pass
    assert len(configure_calls) == 2

    # this is the other variable set by pip when doing isolated build
    with push_env(PYTHONPATH="/path/to/anything", PYTHONNOUSERSITE="1"):
        with pytest.raises(RuntimeError, match=exit_before_running_make), execute_setup_py(tmp_dir, ["build"]):
            pass
    assert len(configure_calls) == 3
