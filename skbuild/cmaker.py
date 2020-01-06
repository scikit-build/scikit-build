"""
This module provides an interface for invoking CMake executable.
"""

from __future__ import print_function
import argparse
import distutils.sysconfig as du_sysconfig
import glob
import io
import itertools
import os
import os.path
import platform
import re
import subprocess
import shlex
import sys
import sysconfig

from .constants import (CMAKE_BUILD_DIR,
                        CMAKE_DEFAULT_EXECUTABLE,
                        CMAKE_INSTALL_DIR,
                        SETUPTOOLS_INSTALL_DIR)
from .platform_specifics import get_platform
from .exceptions import SKBuildError

RE_FILE_INSTALL = re.compile(
    r"""[ \t]*file\(INSTALL DESTINATION "([^"]+)".*"([^"]+)"\).*""")


def pop_arg(arg, args, default=None):
    """Pops an argument ``arg`` from an argument list ``args`` and returns the
    new list and the value of the argument if present and a default otherwise.
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(arg)
    namespace, args = parser.parse_known_args(args)
    namespace = tuple(vars(namespace).items())
    if namespace and namespace[0][1] is not None:
        val = namespace[0][1]
    else:
        val = default
    return args, val


def _remove_cwd_prefix(path):
    cwd = os.getcwd()

    result = path.replace("/", os.sep)
    if result.startswith(cwd):
        result = os.path.relpath(result, cwd)

    if platform.system() == "Windows":
        result = result.replace("\\\\", os.sep)

    result = result.replace("\n", "")

    return result


def has_cmake_cache_arg(cmake_args, arg_name, arg_value=None):
    """Return True if ``-D<arg_name>:TYPE=<arg_value>`` is found
    in ``cmake_args``. If ``arg_value`` is None, return True only if
    ``-D<arg_name>:`` is found in the list."""
    for arg in reversed(cmake_args):
        if arg.startswith("-D%s:" % arg_name):
            if arg_value is None:
                return True
            elif "=" in arg:
                return arg.split("=")[1] == arg_value
    return False


def get_cmake_version(cmake_executable=CMAKE_DEFAULT_EXECUTABLE):
    """Runs CMake and extracts associated version information.
    Raises :class:`skbuild.exceptions.SKBuildError` if it failed to execute CMake.
    """
    try:
        version_string = subprocess.check_output([cmake_executable, '--version'])
    except (OSError, subprocess.CalledProcessError):
        raise SKBuildError(
            "Problem with the CMake installation, aborting build. CMake executable is %s" % cmake_executable)

    if sys.version_info > (3, 0):
        version_string = version_string.decode()

    return version_string.splitlines()[0].split(' ')[-1]


class CMaker(object):
    """Interface to CMake executable."""

    def __init__(self, cmake_executable=CMAKE_DEFAULT_EXECUTABLE):
        self.cmake_executable = cmake_executable
        self.cmake_version = get_cmake_version(self.cmake_executable)
        self.platform = get_platform()

    def get_cached_generator_name(self):
        """Reads and returns the cached generator from the :func:`skbuild.constants.CMAKE_BUILD_DIR()`:.
        Returns None if not found.
        """
        try:
            cmake_generator = 'CMAKE_GENERATOR:INTERNAL='
            with open(os.path.join(CMAKE_BUILD_DIR(), 'CMakeCache.txt')) as fp:
                for line in fp:
                    if line.startswith(cmake_generator):
                        return line[len(cmake_generator):].strip()
        except (OSError, IOError):
            pass

        return None

    def get_cached_generator_env(self):
        """If any, return a mapping of environment associated with the cached generator.
        """
        generator_name = self.get_cached_generator_name()
        if generator_name is not None:
            return self.platform.get_generator(generator_name).env

        return None

    def configure(self, clargs=(), generator_name=None, skip_generator_test=False,
                  cmake_source_dir='.', cmake_install_dir='',
                  languages=('C', 'CXX'), cleanup=True):
        """Calls cmake to generate the Makefile/VS Solution/XCode project.

        clargs: tuple
            List of command line arguments to pass to cmake executable.

        generator_name: string
            The string representing the CMake generator to use.
            If None, uses defaults for your platform.

        skip_generator_test: bool
            If set to True and if a generator name is specified (either as a keyword
            argument or as `clargs` using `-G <generator_name>`), the generator test
            is skipped.

        cmake_source_dir: string
            Path to source tree containing a ``CMakeLists.txt``

        cmake_install_dir: string
            Relative directory to append
            to :func:`skbuild.constants.CMAKE_INSTALL_DIR()`.

        languages: tuple
            List of languages required to configure the project and expected to
            be supported by the compiler. The language identifier that can be specified
            in the list corresponds to the one recognized by CMake.

        cleanup: bool
            If True, cleans up temporary folder used to test
            generators. Set to False for debugging to see CMake's
            output files.

        Return a mapping of the environment associated with the
        selected :class:`skbuild.platform_specifics.abstract.CMakeGenerator`.

        Mapping of the environment can also be later retrieved using :meth:`.get_cached_generator_env`.
        """

        # if no provided default generator_name, check environment
        if generator_name is None:
            generator_name = os.environ.get("CMAKE_GENERATOR")

        # if generator_name is provided on command line, use it
        clargs, cli_generator_name = pop_arg('-G', clargs)
        if cli_generator_name is not None:
            generator_name = cli_generator_name

        generator = self.platform.get_best_generator(
            generator_name, skip_generator_test=skip_generator_test,
            cmake_executable=self.cmake_executable, cmake_args=clargs,
            languages=languages, cleanup=cleanup)

        if not os.path.exists(CMAKE_BUILD_DIR()):
            os.makedirs(CMAKE_BUILD_DIR())

        if not os.path.exists(CMAKE_INSTALL_DIR()):
            os.makedirs(CMAKE_INSTALL_DIR())

        if not os.path.exists(SETUPTOOLS_INSTALL_DIR()):
            os.makedirs(SETUPTOOLS_INSTALL_DIR())

        python_version = CMaker.get_python_version()
        python_include_dir = CMaker.get_python_include_dir(python_version)
        python_library = CMaker.get_python_library(python_version)

        cmake_source_dir = os.path.abspath(cmake_source_dir)
        cmd = [
            self.cmake_executable, cmake_source_dir, '-G', generator.name,
            ("-DCMAKE_INSTALL_PREFIX:PATH=" +
                os.path.abspath(
                    os.path.join(CMAKE_INSTALL_DIR(), cmake_install_dir))),
            ("-DPYTHON_EXECUTABLE:FILEPATH=" +
                sys.executable),
            ("-DPYTHON_VERSION_STRING:STRING=" +
                sys.version.split(' ')[0]),
            ("-DPYTHON_INCLUDE_DIR:PATH=" +
                python_include_dir),
            ("-DPYTHON_LIBRARY:FILEPATH=" +
                python_library),
            ("-DSKBUILD:BOOL=" +
                "TRUE"),
            ("-DCMAKE_MODULE_PATH:PATH=" +
                os.path.join(os.path.dirname(__file__), "resources", "cmake"))
        ]

        cmd.extend(clargs)

        cmd.extend(
            filter(bool,
                   shlex.split(os.environ.get("SKBUILD_CONFIGURE_OPTIONS", "")))
        )

        # changes dir to cmake_build and calls cmake's configure step
        # to generate makefile
        print(
            "Configuring Project\n"
            "  Working directory:\n"
            "    {}\n"
            "  Command:\n"
            "    {}\n".format(
                os.path.abspath(CMAKE_BUILD_DIR()),
                self._formatArgsForDisplay(cmd)
            ))
        rtn = subprocess.call(cmd, cwd=CMAKE_BUILD_DIR(), env=generator.env)
        if rtn != 0:
            raise SKBuildError(
                "An error occurred while configuring with CMake.\n"
                "  Command:\n"
                "    {}\n"
                "  Source directory:\n"
                "    {}\n"
                "  Working directory:\n"
                "    {}\n"
                "Please see CMake's output for more information.".format(
                    self._formatArgsForDisplay(cmd),
                    os.path.abspath(cmake_source_dir),
                    os.path.abspath(CMAKE_BUILD_DIR())))

        CMaker.check_for_bad_installs()

        return generator.env

    @staticmethod
    def get_python_version():
        """Get version associated with the current python interpreter."""
        python_version = sysconfig.get_config_var('VERSION')

        if not python_version:
            python_version = sysconfig.get_config_var('py_version_short')

        if not python_version:
            python_version = ".".join(map(str, sys.version_info[:2]))

        return python_version

    # NOTE(opadron): The try-excepts raise the cyclomatic complexity, but we
    # need them for this function.
    @staticmethod  # noqa: C901
    def get_python_include_dir(python_version):
        """Get include directory associated with the current python
        interpreter."""
        # determine python include dir
        python_include_dir = sysconfig.get_config_var('INCLUDEPY')

        # if Python.h not found (or python_include_dir is None), try to find a
        # suitable include dir
        found_python_h = (
            python_include_dir is not None and
            os.path.exists(os.path.join(python_include_dir, 'Python.h'))
        )

        if not found_python_h:

            # NOTE(opadron): these possible prefixes must be guarded against
            # AttributeErrors and KeyErrors because they each can throw on
            # different platforms or even different builds on the same platform.
            include_py = sysconfig.get_config_var('INCLUDEPY')
            include_dir = sysconfig.get_config_var('INCLUDEDIR')
            include = None
            plat_include = None
            python_inc = None
            python_inc2 = None

            try:
                include = sysconfig.get_path('include')
            except (AttributeError, KeyError):
                pass

            try:
                plat_include = sysconfig.get_path('platinclude')
            except (AttributeError, KeyError):
                pass

            try:
                python_inc = sysconfig.get_python_inc()
            except AttributeError:
                pass

            if include_py is not None:
                include_py = os.path.dirname(include_py)
            if include is not None:
                include = os.path.dirname(include)
            if plat_include is not None:
                plat_include = os.path.dirname(plat_include)
            if python_inc is not None:
                python_inc2 = os.path.join(
                    python_inc, ".".join(map(str, sys.version_info[:2])))

            candidate_prefixes = list(filter(bool, (
                include_py,
                include_dir,
                include,
                plat_include,
                python_inc,
                python_inc2,
            )))

            candidate_versions = (python_version,)
            if python_version:
                candidate_versions += ('',)

                pymalloc = None
                try:
                    pymalloc = bool(sysconfig.get_config_var('WITH_PYMALLOC'))
                except AttributeError:
                    pass

                if pymalloc:
                    candidate_versions += (python_version + 'm',)

            candidates = (
                os.path.join(prefix, ''.join(('python', ver)))
                for (prefix, ver) in itertools.product(
                    candidate_prefixes,
                    candidate_versions
                )
            )

            for candidate in candidates:
                if os.path.exists(os.path.join(candidate, 'Python.h')):
                    # we found an include directory
                    python_include_dir = candidate
                    break

        # TODO(opadron): what happens if we don't find an include directory?
        #                Throw SKBuildError?

        return python_include_dir

    @staticmethod
    def get_python_library(python_version):
        """Get path to the python library associated with the current python
        interpreter."""
        # determine direct path to libpython
        python_library = sysconfig.get_config_var('LIBRARY')

        # if static (or nonexistent), try to find a suitable dynamic libpython
        if (not python_library or
                os.path.splitext(python_library)[1][-2:] == '.a'):

            candidate_lib_prefixes = ['', 'lib']

            candidate_implementations = ['python']
            if hasattr(sys, "pypy_version_info"):
                candidate_implementations = ['pypy-c', 'pypy3-c']

            candidate_extensions = ['.lib', '.so', '.a']
            if sysconfig.get_config_var('WITH_DYLD'):
                candidate_extensions.insert(0, '.dylib')

            candidate_versions = [python_version]
            if python_version:
                candidate_versions.append('')
                candidate_versions.insert(
                    0, "".join(python_version.split(".")[:2]))

            abiflags = getattr(sys, 'abiflags', '')
            candidate_abiflags = [abiflags]
            if abiflags:
                candidate_abiflags.append('')

            # Ensure the value injected by virtualenv is
            # returned on windows.
            # Because calling `sysconfig.get_config_var('multiarchsubdir')`
            # returns an empty string on Linux, `du_sysconfig` is only used to
            # get the value of `LIBDIR`.
            libdir = du_sysconfig.get_config_var('LIBDIR')
            if sysconfig.get_config_var('MULTIARCH'):
                masd = sysconfig.get_config_var('multiarchsubdir')
                if masd:
                    if masd.startswith(os.sep):
                        masd = masd[len(os.sep):]
                    libdir = os.path.join(libdir, masd)

            if libdir is None:
                libdir = os.path.abspath(os.path.join(
                    sysconfig.get_config_var('LIBDEST'), "..", "libs"))

            candidates = (
                os.path.join(
                    libdir,
                    ''.join((pre, impl, ver, abi, ext))
                )
                for (pre, impl, ext, ver, abi) in itertools.product(
                    candidate_lib_prefixes,
                    candidate_implementations,
                    candidate_extensions,
                    candidate_versions,
                    candidate_abiflags
                )
            )

            for candidate in candidates:
                if os.path.exists(candidate):
                    # we found a (likely alternate) libpython
                    python_library = candidate
                    break

        # TODO(opadron): what happens if we don't find a libpython?

        return python_library

    @staticmethod
    def check_for_bad_installs():
        """This function tries to catch files that are meant to be installed
        outside the project root before they are actually installed.

        Indeed, we can not wait for the manifest, so we try to extract the
        information (install destination) from the CMake build files
        ``*.cmake`` found in :func:`skbuild.constants.CMAKE_BUILD_DIR()`.

        It raises :class:`skbuild.exceptions.SKBuildError` if it found install destination outside of
        :func:`skbuild.constants.CMAKE_INSTALL_DIR()`.
        """

        bad_installs = []
        install_dir = os.path.join(os.getcwd(), CMAKE_INSTALL_DIR())

        for root, _, file_list in os.walk(CMAKE_BUILD_DIR()):
            for filename in file_list:
                if os.path.splitext(filename)[1] != ".cmake":
                    continue

                with io.open(os.path.join(root, filename), encoding="utf-8") as fp:
                    lines = fp.readlines()

                for line in lines:
                    match = RE_FILE_INSTALL.match(line)
                    if match is None:
                        continue

                    destination = os.path.normpath(
                        match.group(1).replace("${CMAKE_INSTALL_PREFIX}",
                                               install_dir))

                    if not destination.startswith(install_dir):
                        bad_installs.append(
                            os.path.join(
                                destination,
                                os.path.basename(match.group(2))
                            )
                        )

        if bad_installs:
            raise SKBuildError("\n".join((
                "  CMake-installed files must be within the project root.",
                "    Project Root:",
                "      " + install_dir,
                "    Violating Files:",
                "\n".join(
                    ("      " + _install) for _install in bad_installs)
            )))

    def make(self, clargs=(), config="Release", source_dir=".", env=None):
        """Calls the system-specific make program to compile code.
        """
        clargs, config = pop_arg('--config', clargs, config)
        if not os.path.exists(CMAKE_BUILD_DIR()):
            raise SKBuildError(("CMake build folder ({}) does not exist. "
                                "Did you forget to run configure before "
                                "make?").format(CMAKE_BUILD_DIR()))

        cmd = [self.cmake_executable, "--build", source_dir,
               "--target", "install", "--config", config, "--"]
        cmd.extend(clargs)
        cmd.extend(
            filter(bool,
                   shlex.split(os.environ.get("SKBUILD_BUILD_OPTIONS", "")))
        )

        rtn = subprocess.call(cmd, cwd=CMAKE_BUILD_DIR(), env=env)
        if rtn != 0:
            raise SKBuildError(
                "An error occurred while building with CMake.\n"
                "  Command:\n"
                "    {}\n"
                "  Source directory:\n"
                "    {}\n"
                "  Working directory:\n"
                "    {}\n"
                "Please see CMake's output for more information.".format(
                    self._formatArgsForDisplay(cmd),
                    os.path.abspath(source_dir),
                    os.path.abspath(CMAKE_BUILD_DIR())))

    def install(self):
        """Returns a list of file paths to install via setuptools that is
        compatible with the data_files keyword argument.
        """
        return self._parse_manifests()

    def _parse_manifests(self):
        paths = \
            glob.glob(os.path.join(CMAKE_BUILD_DIR(), "install_manifest*.txt"))
        try:
            return [self._parse_manifest(path) for path in paths][0]
        except IndexError:
            return []

    @staticmethod
    def _parse_manifest(install_manifest_path):
        with open(install_manifest_path, "r") as manifest:
            return [_remove_cwd_prefix(path) for path in manifest]

        return []

    @staticmethod
    def _formatArgsForDisplay(args):
        """Format a list of arguments appropriately for display. When formatting
        a command and its arguments, the user should be able to execute the
        command by copying and pasting the output directly into a shell.

        Currently, the only formatting is naively surrounding each argument with
        quotation marks.
        """
        try:
            from shlex import quote
        except ImportError:
            from pipes import quote

        return ' '.join(quote(arg) for arg in args)
