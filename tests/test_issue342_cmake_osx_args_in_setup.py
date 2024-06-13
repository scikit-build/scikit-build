from __future__ import annotations

import platform
import sys
import textwrap

import pytest

import skbuild.constants

from . import _tmpdir, execute_setup_py, push_env

params = (
    "osx_deployment_target_env_var,cli_setup_args,"
    "keyword_cmake_args,cli_cmake_args,expected_cmake_osx_deployment_target"
)


@pytest.mark.parametrize(
    params,
    [
        # default plat_name is 'macosx-10.9-x86_64'
        (
            # osx_deployment_target_env_var
            None,
            # cli_setup_args
            [],
            # keyword_cmake_args
            [],
            # cli_cmake_args
            [],
            # expected_cmake_osx_deployment_target
            "10.9",
        ),
        (
            # osx_deployment_target_env_var
            "10.7",
            # cli_setup_args
            [],
            # keyword_cmake_args
            [],
            # cli_cmake_args
            [],
            # expected_cmake_osx_deployment_target
            "10.7",
        ),
        (
            # osx_deployment_target_env_var
            "10.7",
            # cli_setup_args
            ["--plat-name", "macosx-10.9-x86_64"],
            # keyword_cmake_args
            [],
            # cli_cmake_args
            [],
            # expected_cmake_osx_deployment_target
            "10.9",
        ),
        (
            # osx_deployment_target_env_var
            None,
            # cli_setup_args
            ["--plat-name", "macosx-10.6-x86_64"],
            # keyword_cmake_args
            [],
            # cli_cmake_args
            [],
            # expected_cmake_osx_deployment_target
            "10.6",
        ),
        (
            # osx_deployment_target_env_var
            None,
            # cli_setup_args
            ["--plat-name", "macosx-10.7-x86_64"],
            # keyword_cmake_args
            [],
            # cli_cmake_args
            [],
            # expected_cmake_osx_deployment_target
            "10.7",
        ),
        (
            # osx_deployment_target_env_var
            None,
            # cli_setup_args
            [],
            # keyword_cmake_args
            ["-DCMAKE_OSX_DEPLOYMENT_TARGET:STRING=10.7"],
            # cli_cmake_args
            [],
            # expected_cmake_osx_deployment_target
            "10.7",
        ),
        (
            # osx_deployment_target_env_var
            None,
            # cli_setup_args
            ["--plat-name", "macosx-10.12-x86_64"],
            # keyword_cmake_args
            ["-DCMAKE_OSX_DEPLOYMENT_TARGET:STRING=10.7"],
            # cli_cmake_args
            [],
            # expected_cmake_osx_deployment_target
            "10.7",
        ),
        (
            # osx_deployment_target_env_var
            None,
            # cli_setup_args
            [],
            # keyword_cmake_args
            ["-DCMAKE_OSX_DEPLOYMENT_TARGET:STRING=10.7"],
            # cli_cmake_args
            ["-DCMAKE_OSX_DEPLOYMENT_TARGET:STRING=10.8"],
            # expected_cmake_osx_deployment_target
            "10.8",
        ),
        (
            # osx_deployment_target_env_var
            None,
            # cli_setup_args
            ["--plat-name", "macosx-10.12-x86_64"],
            # keyword_cmake_args
            ["-DCMAKE_OSX_DEPLOYMENT_TARGET:STRING=10.7"],
            # cli_cmake_args
            ["-DCMAKE_OSX_DEPLOYMENT_TARGET:STRING=10.8"],
            # expected_cmake_osx_deployment_target
            "10.8",
        ),
    ],
)
def test_cmake_args_keyword_osx_default(
    osx_deployment_target_env_var,
    cli_setup_args,
    keyword_cmake_args,
    cli_cmake_args,
    expected_cmake_osx_deployment_target,
    mocker,
    monkeypatch,
):
    tmp_dir = _tmpdir("cmake_args_keyword_osx_default")

    tmp_dir.join("setup.py").write(
        textwrap.dedent(
            """
        from skbuild import setup
        setup(
            name="test_cmake_args_keyword_osx_default",
            version="1.2.3",
            description="A minimal example package",
            author="The scikit-build team",
            license="MIT",
            cmake_args=[{cmake_args}]
        )
        """.format(cmake_args=",".join([f"'{arg}'" for arg in keyword_cmake_args]))
        )
    )
    tmp_dir.join("CMakeLists.txt").write(
        textwrap.dedent(
            """
        message(FATAL_ERROR "This error message should not be displayed")
        """
        )
    )

    mock_configure = mocker.patch("skbuild.cmaker.CMaker.configure", side_effect=RuntimeError("exit skbuild"))

    monkeypatch.setattr(platform, "mac_ver", lambda: ("10.9", None, "x84_64"))
    monkeypatch.setattr(platform, "machine", lambda: "x86_64")
    monkeypatch.setattr(sys, "platform", "darwin")

    with push_env(MACOSX_DEPLOYMENT_TARGET=osx_deployment_target_env_var):
        monkeypatch.setattr(skbuild.constants, "_SKBUILD_PLAT_NAME", skbuild.constants._default_skbuild_plat_name())
        with pytest.raises(RuntimeError, match="exit skbuild"):
            with execute_setup_py(tmp_dir, ["build", *cli_setup_args, "--", *cli_cmake_args]):
                pass

    assert mock_configure.call_count == 1

    current_cmake_args = mock_configure.call_args[0][0]

    # Since additional cmake argument are appended, it is not possible to simply
    # compare lists.
    found_cmake_osx_deployment_target = False
    for cmake_arg in reversed(current_cmake_args):
        if cmake_arg.startswith("-DCMAKE_OSX_DEPLOYMENT_TARGET:STRING="):
            if cmake_arg.endswith(expected_cmake_osx_deployment_target):
                found_cmake_osx_deployment_target = True
            break

    assert found_cmake_osx_deployment_target, textwrap.dedent(
        f"""
                    Argument -DCMAKE_OSX_DEPLOYMENT_TARGET:STRING={expected_cmake_osx_deployment_target} is NOT found near the end of
                    current list of arguments:
                      keyword_cmake_args  : {keyword_cmake_args}
                      cli_cmake_args    : {cli_cmake_args}
                      current_cmake_args: {current_cmake_args}
                    """
    )
