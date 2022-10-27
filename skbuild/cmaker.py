"""
This module provides an interface for invoking CMake executable.
"""


import argparse
import configparser
import contextlib
import glob
import itertools
import os
import os.path
import platform
import re
import shlex
import subprocess
import sys
import sysconfig
from pathlib import Path
from shlex import quote
from typing import Dict, List, Mapping, Optional, Sequence, Tuple, overload

import distutils.sysconfig as du_sysconfig

from .constants import (
    CMAKE_BUILD_DIR,
    CMAKE_DEFAULT_EXECUTABLE,
    CMAKE_INSTALL_DIR,
    SETUPTOOLS_INSTALL_DIR,
)
from .exceptions import SKBuildError
from .platform_specifics import get_platform

RE_FILE_INSTALL = re.compile(r"""[ \t]*file\(INSTALL DESTINATION "([^"]+)".*"([^"]+)"\).*""")


@overload
def pop_arg(arg: str, args: Sequence[str], default: None = None) -> Tuple[List[str], Optional[str]]:
    ...


@overload
def pop_arg(arg: str, args: Sequence[str], default: str) -> Tuple[List[str], str]:
    ...


def pop_arg(arg: str, args: Sequence[str], default: Optional[str] = None) -> Tuple[List[str], Optional[str]]:
    """Pops an argument ``arg`` from an argument list ``args`` and returns the
    new list and the value of the argument if present and a default otherwise.
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(arg)
    namespace_names, args = parser.parse_known_args(args)
    namespace = tuple(vars(namespace_names).items())
    if namespace and namespace[0][1] is not None:
        val = namespace[0][1]
    else:
        val = default
    return args, val


def _remove_cwd_prefix(path: str) -> str:
    cwd = os.getcwd()

    result = path.replace("/", os.sep)
    if result.startswith(cwd):
        result = os.path.relpath(result, cwd)

    if platform.system() == "Windows":
        result = result.replace("\\\\", os.sep)

    result = result.replace("\n", "")

    return result


def has_cmake_cache_arg(cmake_args: List[str], arg_name: str, arg_value: Optional[str] = None) -> bool:
    """Return True if ``-D<arg_name>:TYPE=<arg_value>`` is found
    in ``cmake_args``. If ``arg_value`` is None, return True only if
    ``-D<arg_name>:`` is found in the list."""
    for arg in reversed(cmake_args):
        if arg.startswith(f"-D{arg_name}:"):
            if arg_value is None:
                return True
            if "=" in arg:
                return arg.split("=")[1] == arg_value
    return False


def get_cmake_version(cmake_executable: str = CMAKE_DEFAULT_EXECUTABLE) -> str:
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
        version_string_bytes = subprocess.run(
            [cmake_executable, "--version"], check=True, stdout=subprocess.PIPE
        ).stdout
    except (OSError, subprocess.CalledProcessError) as err:
        raise SKBuildError(
            f"Problem with the CMake installation, aborting build. CMake executable is {cmake_executable}"
        ) from err

    version_string = version_string_bytes.decode()

    return version_string.splitlines()[0].split(" ")[-1]


class CMaker:
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

    def __init__(self, cmake_executable: str = CMAKE_DEFAULT_EXECUTABLE) -> None:
        self.cmake_executable = cmake_executable
        self.cmake_version = get_cmake_version(self.cmake_executable)
        self.platform = get_platform()

    @staticmethod
    def get_cached(variable_name: str) -> Optional[str]:
        """If set, returns the variable cached value from the :func:`skbuild.constants.CMAKE_BUILD_DIR()`, otherwise returns None"""
        variable_name = f"{variable_name}:"
        cmake_cache = Path(CMAKE_BUILD_DIR()) / "CMakeCache.txt"

        with contextlib.suppress(OSError):
            for line in cmake_cache.read_text("utf8").splitlines():
                if line.startswith(variable_name):
                    return line.split("=", 1)[-1].strip()

        return None

    @classmethod
    def get_cached_generator_name(cls) -> Optional[str]:
        """Reads and returns the cached generator from the :func:`skbuild.constants.CMAKE_BUILD_DIR()`:.
        Returns None if not found.
        """
        return cls.get_cached("CMAKE_GENERATOR")

    def get_cached_generator_env(self) -> Optional[Dict[str, str]]:
        """If any, return a mapping of environment associated with the cached generator."""
        generator_name = self.get_cached_generator_name()
        if generator_name is not None:
            return self.platform.get_generator(generator_name).env

        return None

    def configure(
        self,
        clargs: Sequence[str] = (),
        generator_name: Optional[str] = None,
        skip_generator_test: bool = False,
        cmake_source_dir: str = ".",
        cmake_install_dir: str = "",
        languages: Sequence[str] = ("C", "CXX"),
        cleanup: bool = True,
    ) -> Dict[str, str]:
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
            with contextlib.suppress(ImportError):
                import ninja  # pylint: disable=import-outside-toplevel

                ninja_executable_path = os.path.join(ninja.BIN_DIR, "ninja")

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
        cmake_resource_dir = os.path.join(os.path.dirname(__file__), "resources", "cmake")
        cmake_install_prefix = os.path.abspath(os.path.join(CMAKE_INSTALL_DIR(), cmake_install_dir))
        python_version_string = sys.version.split(" ", maxsplit=1)[0]

        cmd = [
            self.cmake_executable,
            cmake_source_dir,
            "-G",
            generator.name,
            f"-DCMAKE_INSTALL_PREFIX:PATH={cmake_install_prefix}",
            f"-DPYTHON_VERSION_STRING:STRING={python_version_string}",
            "-DSKBUILD:INTERNAL=TRUE",
            f"-DCMAKE_MODULE_PATH:PATH={cmake_resource_dir}",
            f"-DPYTHON_EXECUTABLE:PATH={sys.executable}",
            f"-DPYTHON_INCLUDE_DIR:PATH={python_include_dir}",
            f"-DPYTHON_LIBRARY:PATH={python_library}",
        ]

        for prefix in ["-DPython", "-DPython3"]:
            cmd.extend(
                [
                    f"{prefix}_EXECUTABLE:PATH={sys.executable}",
                    f"{prefix}_ROOT_DIR:PATH={sys.prefix}",
                    f"{prefix}_INCLUDE_DIR:PATH={python_include_dir}",
                    f"{prefix}_FIND_REGISTRY:STRING=NEVER",
                ]
            )
            if sys.implementation.name == "pypy":
                cmd.append(f"{prefix}_FIND_IMPLEMENTATIONS:STRING=PyPy")

            with contextlib.suppress(ImportError):
                import numpy as np

                cmd.append(f"{prefix}_NumPy_INCLUDE_DIRS:PATH=" + np.get_include())

        if generator.toolset:
            cmd.extend(["-T", generator.toolset])
        if generator.architecture and "Visual Studio" in generator.name:
            cmd.extend(["-A", generator.architecture])
        if ninja_executable_path is not None:
            cmd.append(f"-DCMAKE_MAKE_PROGRAM:FILEPATH={ninja_executable_path}")

        cmd.extend(clargs)

        # Parse CMAKE_ARGS only if SKBUILD_CONFIGURE_OPTIONS is not present
        if "SKBUILD_CONFIGURE_OPTIONS" in os.environ:
            env_cmake_args = list(filter(None, shlex.split(os.environ["SKBUILD_CONFIGURE_OPTIONS"])))
        else:
            env_cmake_args_filtered = filter(None, shlex.split(os.environ.get("CMAKE_ARGS", "")))
            env_cmake_args = [s for s in env_cmake_args_filtered if "CMAKE_INSTALL_PREFIX" not in s]

        cmd.extend(env_cmake_args)

        # changes dir to cmake_build and calls cmake's configure step
        # to generate makefile
        print(
            "Configuring Project\n"
            "  Working directory:\n"
            f"    {os.path.abspath(CMAKE_BUILD_DIR())}\n"
            "  Command:\n"
            f"    {self._formatArgsForDisplay(cmd)}\n",
            flush=True,
        )
        rtn = subprocess.run(cmd, cwd=CMAKE_BUILD_DIR(), env=generator.env, check=False).returncode
        if rtn != 0:
            raise SKBuildError(
                "An error occurred while configuring with CMake.\n"
                "  Command:\n"
                f"    {self._formatArgsForDisplay(cmd)}\n"
                "  Source directory:\n"
                f"    {os.path.abspath(cmake_source_dir)}\n"
                "  Working directory:\n"
                f"    {os.path.abspath(CMAKE_BUILD_DIR())}\n"
                "Please see CMake's output for more information."
            )

        CMaker.check_for_bad_installs()

        return generator.env

    @staticmethod
    def get_python_version() -> str:
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

        assert isinstance(python_version, str)

        return python_version

    # NOTE(opadron): The try-excepts raise the cyclomatic complexity, but we
    # need them for this function.
    @staticmethod  # noqa: C901
    def get_python_include_dir(python_version: str) -> Optional[str]:
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
        python_include_dir: Optional[str] = sysconfig.get_config_var("INCLUDEPY")

        # if Python.h not found (or python_include_dir is None), try to find a
        # suitable include dir
        found_python_h = python_include_dir is not None and os.path.exists(os.path.join(python_include_dir, "Python.h"))

        if not found_python_h:

            # NOTE(opadron): these possible prefixes must be guarded against
            # AttributeErrors and KeyErrors because they each can throw on
            # different platforms or even different builds on the same platform.
            include_py: Optional[str] = sysconfig.get_config_var("INCLUDEPY")
            include_dir: Optional[str] = sysconfig.get_config_var("INCLUDEDIR")
            include: Optional[str] = None
            plat_include: Optional[str] = None
            python_inc: Optional[str] = None
            python_inc2: Optional[str] = None

            with contextlib.suppress(AttributeError, KeyError):
                include = sysconfig.get_path("include")

            with contextlib.suppress(AttributeError, KeyError):
                plat_include = sysconfig.get_path("platinclude")

            with contextlib.suppress(AttributeError):
                python_inc = sysconfig.get_python_inc()  # type: ignore[attr-defined]

            if include_py is not None:
                include_py = os.path.dirname(include_py)
            if include is not None:
                include = os.path.dirname(include)
            if plat_include is not None:
                plat_include = os.path.dirname(plat_include)
            if python_inc is not None:
                python_inc2 = os.path.join(python_inc, ".".join(map(str, sys.version_info[:2])))

            all_candidate_prefixes = [include_py, include_dir, include, plat_include, python_inc, python_inc2]
            candidate_prefixes: List[str] = [pre for pre in all_candidate_prefixes if pre]

            candidate_versions: Tuple[str, ...] = (python_version,)
            if python_version:
                candidate_versions += ("",)

                pymalloc = None
                with contextlib.suppress(AttributeError):
                    pymalloc = bool(sysconfig.get_config_var("WITH_PYMALLOC"))

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
    def get_python_library(python_version: str) -> Optional[str]:
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
        # On Windows, support cross-compiling in the same way as setuptools
        # When cross-compiling, check DIST_EXTRA_CONFIG first
        config_file = os.environ.get("DIST_EXTRA_CONFIG", None)
        if config_file and Path(config_file).is_file():
            cp = configparser.ConfigParser()
            cp.read(config_file)
            result = cp.get("build_ext", "library_dirs", fallback="")
            if result:
                minor = sys.version_info[1]
                return str(Path(result) / f"python3{minor}.lib")

        # This seems to be the simplest way to detect the library path with
        # modern python versions that avoids the complicated construct below.
        # It avoids guessing the library name. Tested with cpython 3.8 and
        # pypy 3.8 on Ubuntu.
        libdir: Optional[str] = sysconfig.get_config_var("LIBDIR")
        ldlibrary: Optional[str] = sysconfig.get_config_var("LDLIBRARY")
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
            if libpath and os.path.exists(libpath):
                return libpath

        return CMaker._guess_python_library(python_version)

    @staticmethod
    def _guess_python_library(python_version: str) -> Optional[str]:
        # determine direct path to libpython
        python_library: Optional[str] = sysconfig.get_config_var("LIBRARY")

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
            assert not isinstance(libdir_a, int)
            if libdir_a is None:
                libdest = sysconfig.get_config_var("LIBDEST")
                candidate_libdirs.append(os.path.abspath(os.path.join(libdest, "..", "libs") if libdest else "libs"))
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
    def check_for_bad_installs() -> None:
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

                with open(os.path.join(root, filename), encoding="utf-8") as fp:
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

    def make(
        self,
        clargs: Sequence[str] = (),
        config: str = "Release",
        source_dir: str = ".",
        install_target: str = "install",
        env: Optional[Mapping[str, str]] = None,
    ) -> None:
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
                f"CMake build folder ({CMAKE_BUILD_DIR()}) does not exist. "
                "Did you forget to run configure before "
                "make?"
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

    def make_impl(
        self,
        clargs: List[str],
        config: str,
        source_dir: str,
        install_target: Optional[str],
        env: Optional[Mapping[str, str]] = None,
    ) -> None:
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

        rtn = subprocess.run(cmd, cwd=CMAKE_BUILD_DIR(), env=env, check=False).returncode
        # For reporting errors (if any)
        if not install_target:
            install_target = "internal build step [valid]"

        if rtn != 0:
            raise SKBuildError(
                "An error occurred while building with CMake.\n"
                "  Command:\n"
                f"    {self._formatArgsForDisplay(cmd)}\n"
                "  Install target:\n"
                f"    {install_target}\n"
                "  Source directory:\n"
                f"    {os.path.abspath(source_dir)}\n"
                "  Working directory:\n"
                f"    {os.path.abspath(CMAKE_BUILD_DIR())}\n"
                "Please check the install target is valid and see CMake's output for more "
                "information."
            )

    def install(self) -> List[str]:
        """Returns a list of file paths to install via setuptools that is
        compatible with the data_files keyword argument.
        """
        return self._parse_manifests()

    def _parse_manifests(self) -> List[str]:
        paths = glob.glob(os.path.join(CMAKE_BUILD_DIR(), "install_manifest*.txt"))
        try:
            return [self._parse_manifest(path) for path in paths][0]
        except IndexError:
            return []

    @staticmethod
    def _parse_manifest(install_manifest_path: str) -> List[str]:
        with open(install_manifest_path, encoding="utf-8") as manifest:
            return [_remove_cwd_prefix(path) for path in manifest]

    @staticmethod
    def _formatArgsForDisplay(args: Sequence[str]) -> str:
        """Format a list of arguments appropriately for display. When formatting
        a command and its arguments, the user should be able to execute the
        command by copying and pasting the output directly into a shell.

        Currently, the only formatting is naively surrounding each argument with
        quotation marks.
        """

        return " ".join(quote(arg) for arg in args)
