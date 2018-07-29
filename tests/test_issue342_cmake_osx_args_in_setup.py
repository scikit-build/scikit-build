import pytest
import sys
import textwrap

from . import _tmpdir, execute_setup_py


@pytest.mark.parametrize("cli_setup_args,keyword_cmake_args,cli_cmake_args,expected_cmake_osx_deployment_target", [
    # default plat_name is 'macosx-10.6-x86_64'
    (
            # cli_setup_args
            [],
            # keyword_cmake_args
            [],
            # cli_cmake_args
            [],
            # expected_cmake_osx_deployment_target
            "10.6"
    ),
    (
            # cli_setup_args
            ['--plat-name', 'macosx-10.6-x86_64'],
            # keyword_cmake_args
            [],
            # cli_cmake_args
            [],
            # expected_cmake_osx_deployment_target
            "10.6"
    ),
    (
            # cli_setup_args
            ['--plat-name', 'macosx-10.7-x86_64'],
            # keyword_cmake_args
            [],
            # cli_cmake_args
            [],
            # expected_cmake_osx_deployment_target
            "10.7"
    ),
    (
            # cli_setup_args
            [],
            # keyword_cmake_args
            ['-DCMAKE_OSX_DEPLOYMENT_TARGET:STRING=10.7'],
            # cli_cmake_args
            [],
            # expected_cmake_osx_deployment_target
            "10.7"
    ),
    (
            # cli_setup_args
            ['--plat-name', 'macosx-10.12-x86_64'],
            # keyword_cmake_args
            ['-DCMAKE_OSX_DEPLOYMENT_TARGET:STRING=10.7'],
            # cli_cmake_args
            [],
            # expected_cmake_osx_deployment_target
            "10.7"
    ),
    (
            # cli_setup_args
            [],
            # keyword_cmake_args
            ['-DCMAKE_OSX_DEPLOYMENT_TARGET:STRING=10.7'],
            # cli_cmake_args
            ['-DCMAKE_OSX_DEPLOYMENT_TARGET:STRING=10.8'],
            # expected_cmake_osx_deployment_target
            "10.8"
    ),
    (
            # cli_setup_args
            ['--plat-name', 'macosx-10.12-x86_64'],
            # keyword_cmake_args
            ['-DCMAKE_OSX_DEPLOYMENT_TARGET:STRING=10.7'],
            # cli_cmake_args
            ['-DCMAKE_OSX_DEPLOYMENT_TARGET:STRING=10.8'],
            # expected_cmake_osx_deployment_target
            "10.8"
    ),
])
def test_cmake_args_keyword_osx_default(
        cli_setup_args, keyword_cmake_args, cli_cmake_args, expected_cmake_osx_deployment_target, mocker):

    tmp_dir = _tmpdir('cmake_args_keyword_osx_default')

    tmp_dir.join('setup.py').write(textwrap.dedent(
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
        """.format(cmake_args=",".join(["'%s'" % arg for arg in keyword_cmake_args]))
    ))
    tmp_dir.join('CMakeLists.txt').write(textwrap.dedent(
        """
        message(FATAL_ERROR "This error message should not be displayed")
        """
    ))

    mock_configure = mocker.patch('skbuild.cmaker.CMaker.configure', side_effect=RuntimeError("exit skbuild"))

    try:
        # allow to run the test on any platform
        saved_platform = sys.platform
        sys.platform = "darwin"

        with pytest.raises(RuntimeError, match="exit skbuild"):
            with execute_setup_py(tmp_dir, ['build'] + cli_setup_args + ['--'] + cli_cmake_args):
                pass
    finally:
        sys.platform = saved_platform

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

    assert found_cmake_osx_deployment_target, \
        textwrap.dedent("""
                    Argument -DCMAKE_OSX_DEPLOYMENT_TARGET:STRING=%s is NOT found near the end of
                    current list of arguments:
                      keyword_cmake_args  : %s
                      cli_cmake_args    : %s
                      current_cmake_args: %s
                    """ % (expected_cmake_osx_deployment_target,
                           keyword_cmake_args, cli_cmake_args, current_cmake_args))
