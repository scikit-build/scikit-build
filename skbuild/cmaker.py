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
import shlex
import subprocess
import sys
import sysconfig

from .constants import (
    CMAKE_BUILD_DIR,
    CMAKE_DEFAULT_EXECUTABLE,
    CMAKE_INSTALL_DIR,
    SETUPTOOLS_INSTALL_DIR,
)
from .exceptions import SKBuildError
from .platform_specifics import get_platform

if sys.version_info >= (3, 3):
    from shlex import quote
else:
    from pipes import quote

RE_FILE_INSTALL = re.compile(r"""[ \t]*file\(INSTALL DESTINATION "([^"]+)".*"([^"]+)"\).*""")


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
        if arg.startswith("-D{}:".format(arg_name)):
            if arg_value is None:
                return True
            if "=" in arg:
                return arg.split("=")[1] == arg_value
    return False


def get_cmake_version(cmake_executable=CMAKE_DEFAULT_EXECUTABLE):
    """
    Runs CMake and extracts associated version information.
    Raises :class:`skbuild.exceptions.SKBuildError` if it failed to execute CMake.

    Example:
        >>> # xdoc: IGNORE_WANT
        >>> from skbuild.cmaker import get_cmake_version
        >>> print(get_cmake_version())
        3.14.4
    """
    try:
        version_string = subprocess.check_output([cmake_executable, "--version"])
    except (OSError, subprocess.CalledProcessError):
        raise SKBuildError(
            "Problem with the CMake installation, aborting build. CMake executable is %s" % cmake_executable
        )

    if sys.version_info > (3, 0):
        version_string = version_string.decode()

    return version_string.splitlines()[0].split(" ")[-1]


class CMaker(object):
    r"""Interface to CMake executable.

    Example:
        >>> # Setup dummy repo
        >>> from skbuild.cmaker import CMaker
        >>> import ubelt as ub
        >>> from os.path import join
        >>> repo_dpath = ub.ensure_app_cache_dir('skbuild', 'test_cmaker')
        >>> ub.delete(repo_dpath)
        >>> src_dpath = ub.ensuredir(join(repo_dpath, 'SRC'))
        >>> cmake_fpath = join(src_dpath, 'CMakeLists.txt')
        >>> open(cmake_fpath, 'w').write(ub.codeblock(
                '''
                cmake_minimum_required(VERSION 3.5.0)
                project(foobar NONE)
                file(WRITE "${CMAKE_BINARY_DIR}/foo.txt" "# foo")
                install(FILES "${CMAKE_BINARY_DIR}/foo.txt" DESTINATION ".")
                install(CODE "message(STATUS \\"Project has been installed\\")")
                message(STATUS "CMAKE_SOURCE_DIR:${CMAKE_SOURCE_DIR}")
                message(STATUS "CMAKE_BINARY_DIR:${CMAKE_BINARY_DIR}")
                '''
        >>> ))
        >>> # create a cmaker instance in the dummy repo, configure, and make.
        >>> from skbuild.utils import push_dir
        >>> with push_dir(repo_dpath):
        >>>     cmkr = CMaker()
        >>>     config_kwargs = {'cmake_source_dir': str(src_dpath)}
        >>>     print('--- test cmaker configure ---')
        >>>     env = cmkr.configure(**config_kwargs)
        >>>     print('--- test cmaker make ---')
        >>>     cmkr.make(env=env)
    """

    def __init__(self, cmake_executable=CMAKE_DEFAULT_EXECUTABLE):
        self.cmake_executable = cmake_executable
        self.cmake_version = get_cmake_version(self.cmake_executable)
        self.platform = get_platform()

    @staticmethod
    def get_cached(variable_name):
        """If set, returns the variable cached value from the :func:`skbuild.constants.CMAKE_BUILD_DIR()`, otherwise returns None"""
        variable_name = "{}:".format(variable_name)
        try:
            with open(os.path.join(CMAKE_BUILD_DIR(), "CMakeCache.txt")) as fp:
                for line in fp:
                    if line.startswith(variable_name):
                        return line.split("=", 1)[-1].strip()
        except (OSError, IOError):
            pass

        return None

    @classmethod
    def get_cached_generator_name(cls):
        """Reads and returns the cached generator from the :func:`skbuild.constants.CMAKE_BUILD_DIR()`:.
        Returns None if not found.
        """
        return cls.get_cached("CMAKE_GENERATOR")

    def get_cached_generator_env(self):
        """If any, return a mapping of environment associated with the cached generator."""
        generator_name = self.get_cached_generator_name()
        if generator_name is not None:
            return self.platform.get_generator(generator_name).env

        return None

    def configure(
        self,
        clargs=(),
        generator_name=None,
        skip_generator_test=False,
        cmake_source_dir=".",
        cmake_install_dir="",
        languages=("C", "CXX"),
        cleanup=True,
    ):
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
        clargs, cli_generator_name = pop_arg("-G", clargs)
        if cli_generator_name is not None:
            generator_name = cli_generator_name

        # if arch is provided on command line, use it
        clargs, cli_arch = pop_arg("-A", clargs)

        generator = self.platform.get_best_generator(
            generator_name,
            skip_generator_test=skip_generator_test,
            cmake_executable=self.cmake_executable,
            cmake_args=clargs,
            languages=languages,
            cleanup=cleanup,
            architecture=cli_arch,
        )

        ninja_executable_path = None
        if generator.name == "Ninja":
            try:
                import ninja  # pylint: disable=import-outside-toplevel

                ninja_executable_path = os.path.join(ninja.BIN_DIR, "ninja")
            except ImportError:
                pass

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
            self.cmake_executable,
            cmake_source_dir,
            "-G",
            generator.name,
            ("-DCMAKE_INSTALL_PREFIX:PATH=" + os.path.abspath(os.path.join(CMAKE_INSTALL_DIR(), cmake_install_dir))),
            ("-DPYTHON_VERSION_STRING:STRING=" + sys.version.split(" ")[0]),
            ("-DSKBUILD:INTERNAL=" + "TRUE"),
            ("-DCMAKE_MODULE_PATH:PATH=" + os.path.join(os.path.dirname(__file__), "resources", "cmake")),
        ]

        find_python_prefixes = [
            "-DPython{}".format(python_version[0]),
            "-DPython",
            "-DPYTHON",
        ]

        for prefix in find_python_prefixes:
            cmd.extend(
                [
                    (prefix + "_EXECUTABLE:FILEPATH=" + sys.executable),
                    (prefix + "_INCLUDE_DIR:PATH=" + python_include_dir),
                    (prefix + "_LIBRARY:PATH=" + python_library),
                ]
            )

            try:
                import numpy as np

                cmd.append(prefix + "_NumPy_INCLUDE_DIRS:PATH=" + np.get_include())
            except ImportError:
                pass

        if generator.toolset:
            cmd.extend(["-T", generator.toolset])
        if generator.architecture:
            cmd.extend(["-A", generator.architecture])
        if ninja_executable_path is not None:
            cmd.append("-DCMAKE_MAKE_PROGRAM:FILEPATH=" + ninja_executable_path)

        cmd.extend(clargs)

        # Parse CMAKE_ARGS only if SKBUILD_CONFIGURE_OPTIONS is not present
        if "SKBUILD_CONFIGURE_OPTIONS" in os.environ:
            env_cmake_args = filter(None, shlex.split(os.environ["SKBUILD_CONFIGURE_OPTIONS"]))
        else:
            env_cmake_args = filter(None, shlex.split(os.environ.get("CMAKE_ARGS", "")))
            env_cmake_args = [s for s in env_cmake_args if "CMAKE_INSTALL_PREFIX" not in s]

        cmd.extend(env_cmake_args)

        # changes dir to cmake_build and calls cmake's configure step
        # to generate makefile
        print(
            "Configuring Project\n"
            "  Working directory:\n"
            "    {}\n"
            "  Command:\n"
            "    {}\n".format(os.path.abspath(CMAKE_BUILD_DIR()), self._formatArgsForDisplay(cmd))
        )
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
                    os.path.abspath(CMAKE_BUILD_DIR()),
                )
            )

        CMaker.check_for_bad_installs()

        return generator.env

    @staticmethod
    def get_python_version():
        """Get version associated with the current python interpreter.

        Returns:
            str: python version string

        Example:
            >>> # xdoc: +IGNORE_WANT
            >>> from skbuild.cmaker import CMaker
            >>> python_version = CMaker.get_python_version()
            >>> print('python_version = {!r}'.format(python_version))
            python_version = '3.7'
        """
        python_version = sysconfig.get_config_var("VERSION")

        if not python_version:
            python_version = sysconfig.get_config_var("py_version_short")

        if not python_version:
            python_version = ".".join(map(str, sys.version_info[:2]))

        return python_version

    # NOTE(opadron): The try-excepts raise the cyclomatic complexity, but we
    # need them for this function.
    @staticmethod  # noqa: C901
    def get_python_include_dir(python_version):
        """Get include directory associated with the current python
        interpreter.

        Args:
            python_version (str): python version, may be partial.

        Returns:
            PathLike: python include dir

        Example:
            >>> # xdoc: +IGNORE_WANT
            >>> from skbuild.cmaker import CMaker
            >>> python_version = CMaker.get_python_version()
            >>> python_include_dir = CMaker.get_python_include_dir(python_version)
            >>> print('python_include_dir = {!r}'.format(python_include_dir))
            python_include_dir = '.../conda/envs/py37/include/python3.7m'
        """
        # determine python include dir
        python_include_dir = sysconfig.get_config_var("INCLUDEPY")

        # if Python.h not found (or python_include_dir is None), try to find a
        # suitable include dir
        found_python_h = python_include_dir is not None and os.path.exists(os.path.join(python_include_dir, "Python.h"))

        if not found_python_h:

            # NOTE(opadron): these possible prefixes must be guarded against
            # AttributeErrors and KeyErrors because they each can throw on
            # different platforms or even different builds on the same platform.
            include_py = sysconfig.get_config_var("INCLUDEPY")
            include_dir = sysconfig.get_config_var("INCLUDEDIR")
            include = None
            plat_include = None
            python_inc = None
            python_inc2 = None

            try:
                include = sysconfig.get_path("include")
            except (AttributeError, KeyError):
                pass

            try:
                plat_include = sysconfig.get_path("platinclude")
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
                python_inc2 = os.path.join(python_inc, ".".join(map(str, sys.version_info[:2])))

            candidate_prefixes = list(
                filter(
                    bool,
                    (
                        include_py,
                        include_dir,
                        include,
                        plat_include,
                        python_inc,
                        python_inc2,
                    ),
                )
            )

            candidate_versions = (python_version,)
            if python_version:
                candidate_versions += ("",)

                pymalloc = None
                try:
                    pymalloc = bool(sysconfig.get_config_var("WITH_PYMALLOC"))
                except AttributeError:
                    pass

                if pymalloc:
                    candidate_versions += (python_version + "m",)

            candidates = (
                os.path.join(prefix, "".join(("python", ver)))
                for (prefix, ver) in itertools.product(candidate_prefixes, candidate_versions)
            )

            for candidate in candidates:
                if os.path.exists(os.path.join(candidate, "Python.h")):
                    # we found an include directory
                    python_include_dir = candidate
                    break

        # TODO(opadron): what happens if we don't find an include directory?
        #                Throw SKBuildError?

        return python_include_dir

    @staticmethod
    def get_python_library(python_version):
        """Get path to the python library associated with the current python
        interpreter.

        Args:
            python_version (str): python version, may be partial.

        Returns:
            PathLike: python_library : python shared library

        Example:
            >>> # xdoc: +IGNORE_WANT
            >>> from skbuild.cmaker import CMaker
            >>> python_version = CMaker.get_python_version()
            >>> python_library = CMaker.get_python_include_dir(python_version)
            >>> print('python_library = {!r}'.format(python_library))
            python_library = '.../conda/envs/py37/include/python3.7m'
        """
        # This seems to be the simplest way to detect the library path with
        # modern python versions that avoids the complicated construct below.
        # It avoids guessing the library name. Tested with cpython 3.8 and
        # pypy 3.8 on Ubuntu.
        libdir = sysconfig.get_config_var("LIBDIR")
        ldlibrary = sysconfig.get_config_var("LDLIBRARY")
        if libdir and ldlibrary and os.path.exists(libdir):
            if sysconfig.get_config_var("MULTIARCH"):
                masd = sysconfig.get_config_var("multiarchsubdir")
                if masd:
                    if masd.startswith(os.sep):
                        masd = masd[len(os.sep) :]
                    libdir_masd = os.path.join(libdir, masd)
                    if os.path.exists(libdir_masd):
                        libdir = libdir_masd
            libpath = os.path.join(libdir, ldlibrary)
            if os.path.exists(libpath):
                return libpath

        return CMaker._guess_python_library(python_version)

    @staticmethod
    def _guess_python_library(python_version):
        # determine direct path to libpython
        python_library = sysconfig.get_config_var("LIBRARY")

        # if static (or nonexistent), try to find a suitable dynamic libpython
        if not python_library or os.path.splitext(python_library)[1][-2:] == ".a":

            candidate_lib_prefixes = ["", "lib"]

            candidate_suffixes = [""]
            candidate_implementations = ["python"]
            if hasattr(sys, "pypy_version_info"):
                candidate_implementations = ["pypy-c", "pypy3-c", "pypy"]
                candidate_suffixes.append("-c")

            candidate_extensions = [".lib", ".so", ".a"]
            # On pypy + MacOS, the variable WITH_DYLD is not set. It would
            # actually be possible to determine the python library there using
            # LDLIBRARY + LIBDIR. As a simple fix, we check if the LDLIBRARY
            # ends with .dylib and add it to the candidate matrix in this case.
            with_ld = sysconfig.get_config_var("WITH_DYLD")
            ld_lib = sysconfig.get_config_var("LDLIBRARY")
            if with_ld or (ld_lib and ld_lib.endswith(".dylib")):
                candidate_extensions.insert(0, ".dylib")

            candidate_versions = [python_version]
            if python_version:
                candidate_versions.append("")
                candidate_versions.insert(0, "".join(python_version.split(".")[:2]))

            abiflags = getattr(sys, "abiflags", "")
            candidate_abiflags = [abiflags]
            if abiflags:
                candidate_abiflags.append("")

            # Ensure the value injected by virtualenv is
            # returned on windows.
            # Because calling `sysconfig.get_config_var('multiarchsubdir')`
            # returns an empty string on Linux, `du_sysconfig` is only used to
            # get the value of `LIBDIR`.
            candidate_libdirs = []
            libdir_a = du_sysconfig.get_config_var("LIBDIR")
            if libdir_a is None:
                candidate_libdirs.append(
                    os.path.abspath(os.path.join(sysconfig.get_config_var("LIBDEST"), "..", "libs"))
                )
            libdir_b = sysconfig.get_config_var("LIBDIR")
            for libdir in (libdir_a, libdir_b):
                if libdir is None:
                    continue
                if sysconfig.get_config_var("MULTIARCH"):
                    masd = sysconfig.get_config_var("multiarchsubdir")
                    if masd:
                        if masd.startswith(os.sep):
                            masd = masd[len(os.sep) :]
                        candidate_libdirs.append(os.path.join(libdir, masd))
                candidate_libdirs.append(libdir)

            candidates = (
                os.path.join(libdir, "".join((pre, impl, ver, abi, suf, ext)))
                for (libdir, pre, impl, ext, ver, abi, suf) in itertools.product(
                    candidate_libdirs,
                    candidate_lib_prefixes,
                    candidate_implementations,
                    candidate_extensions,
                    candidate_versions,
                    candidate_abiflags,
                    candidate_suffixes,
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

                    destination = os.path.normpath(match.group(1).replace("${CMAKE_INSTALL_PREFIX}", install_dir))

                    if not destination.startswith(install_dir):
                        bad_installs.append(os.path.join(destination, os.path.basename(match.group(2))))

        if bad_installs:
            raise SKBuildError(
                "\n".join(
                    (
                        "  CMake-installed files must be within the project root.",
                        "    Project Root:",
                        "      " + install_dir,
                        "    Violating Files:",
                        "\n".join(("      " + _install) for _install in bad_installs),
                    )
                )
            )

    def make(self, clargs=(), config="Release", source_dir=".", install_target="install", env=None):
        """Calls the system-specific make program to compile code.

        install_target: string
             Name of the target responsible to install the project.
             Default is "install".

             .. note::

                To workaround CMake issue #8438.
                See https://gitlab.kitware.com/cmake/cmake/-/issues/8438
                Due to a limitation of CMake preventing from adding a dependency
                on the "build-all" built-in target, we explicitly build the project first when
                the install target is different from the default on.
        """
        clargs, config = pop_arg("--config", clargs, config)
        clargs, install_target = pop_arg("--install-target", clargs, install_target)
        if not os.path.exists(CMAKE_BUILD_DIR()):
            raise SKBuildError(
                ("CMake build folder ({}) does not exist. " "Did you forget to run configure before " "make?").format(
                    CMAKE_BUILD_DIR()
                )
            )

        # Workaround CMake issue #8438
        # See https://gitlab.kitware.com/cmake/cmake/-/issues/8438
        # Due to a limitation of CMake preventing from adding a dependency
        # on the "build-all" built-in target, we explicitly build
        # the project first when
        # the install target is different from the default on.
        if install_target != "install":
            self.make_impl(clargs=clargs, config=config, source_dir=source_dir, install_target=None, env=env)

        self.make_impl(clargs=clargs, config=config, source_dir=source_dir, install_target=install_target, env=env)

    def make_impl(self, clargs, config, source_dir, install_target, env=None):
        """
        Precondition: clargs does not have --config nor --install-target options.
        These command line arguments are extracted in the caller function
        `make` with `clargs, config = pop_arg('--config', clargs, config)`

        This is a refactor effort for calling the function `make` twice in
        case the install_target is different than the default `install`.
        """
        if not install_target:
            cmd = [self.cmake_executable, "--build", source_dir, "--config", config, "--"]
        else:
            cmd = [self.cmake_executable, "--build", source_dir, "--target", install_target, "--config", config, "--"]
        cmd.extend(clargs)
        cmd.extend(filter(bool, shlex.split(os.environ.get("SKBUILD_BUILD_OPTIONS", ""))))

        rtn = subprocess.call(cmd, cwd=CMAKE_BUILD_DIR(), env=env)
        # For reporting errors (if any)
        if not install_target:
            install_target = "internal build step [valid]"

        if rtn != 0:
            raise SKBuildError(
                "An error occurred while building with CMake.\n"
                "  Command:\n"
                "    {}\n"
                "  Install target:\n"
                "    {}\n"
                "  Source directory:\n"
                "    {}\n"
                "  Working directory:\n"
                "    {}\n"
                "Please check the install target is valid and see CMake's output for more "
                "information.".format(
                    self._formatArgsForDisplay(cmd),
                    install_target,
                    os.path.abspath(source_dir),
                    os.path.abspath(CMAKE_BUILD_DIR()),
                )
            )

    def install(self):
        """Returns a list of file paths to install via setuptools that is
        compatible with the data_files keyword argument.
        """
        return self._parse_manifests()

    def _parse_manifests(self):
        paths = glob.glob(os.path.join(CMAKE_BUILD_DIR(), "install_manifest*.txt"))
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

        return " ".join(quote(arg) for arg in args)
