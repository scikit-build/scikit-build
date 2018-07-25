import textwrap
import platform
import pytest

from skbuild.cmaker import has_cmake_cache_arg

from . import _tmpdir, execute_setup_py


@pytest.mark.skipif(platform.system().lower() != "darwin",
                    reason="This test is only needed for OSX.")
@pytest.mark.parametrize("cmake_args", [
    [],
    ['-DCMAKE_OSX_DEPLOYMENT_TARGET:STRING=10.7',
     '-DCMAKE_OSX_ARCHITECTURES:STRING=x86'],
    ['-DCMAKE_OSX_DEPLOYMENT_TARGET:STRING=10.5',
     '-DCMAKE_OSX_ARCHITECTURES:STRING=x86_64'],
    ['-DCMAKE_OSX_DEPLOYMENT_TARGET:STRING=Test'],
    ['-DCMAKE_OSX_DEPLOYMENT_TARGET:STRING=Test2']
])
@pytest.mark.parametrize("cli_cmake_args", [
    [],
    ['-DCMAKE_OSX_DEPLOYMENT_TARGET:STRING=10.5',
     '-DCMAKE_OSX_ARCHITECTURES:STRING=x86_64'],
    ['-DCMAKE_OSX_DEPLOYMENT_TARGET:STRING=Test'],
    ['-DCMAKE_OSX_DEPLOYMENT_TARGET:STRING=Test2']
])
@pytest.mark.parametrize("command", ['build', 'bdist_wheel'])
def test_cmake_args_keyword_osx_default(mocker, cmake_args, cli_cmake_args, command):

    mock_setup = mocker.patch('skbuild.setuptools_wrap.upstream_setup')
    # returns ``None`` so subprocess can actually run.
    mock_configure = mocker.patch('skbuild.cmaker.CMaker.configure', return_value=None)

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
        """.format(cmake_args=",".join(["'%s'" % arg for arg in cmake_args]))
    ))
    tmp_dir.join('CMakeLists.txt').write(textwrap.dedent(
        """
        cmake_minimum_required(VERSION 3.5.0)
        project(test NONE)
        message(STATUS "CMAKE_OSX_DEPLOYMENT_TARGET[${CMAKE_OSX_DEPLOYMENT_TARGET}]")
        message(STATUS "CMAKE_OSX_ARCHITECTURES[${CMAKE_OSX_ARCHITECTURES}]")
        install(CODE "execute_process(
          COMMAND \${CMAKE_COMMAND} -E sleep 0)")
        """
    ))

    with execute_setup_py(tmp_dir, [command, '--'] + cli_cmake_args, disable_languages_test=True):
        assert mock_setup.call_count == 1
        setup_kw = mock_setup.call_args[1]
        assert setup_kw['cmake_args'] == cmake_args

        assert mock_configure.call_count == 1
        clargs = mock_setup.call_args[1]['clargs']

        # figure out what args are set to what.
        expected = {}
        for arglist in [cmake_args, cli_cmake_args]:
            for arg in arglist:
                name, arg = arg[2:].split(":")
                _, value = arg.split("=")
                expected[name] = value

        # allows for defaults to exist only if not specified, and ignores them.
        for name, value in expected.items():
            assert has_cmake_cache_arg(clargs, name, value)
