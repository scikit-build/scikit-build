"""This module provides functionality for wrapping key infrastructure components
from distutils and setuptools.
"""


import argparse
import contextlib
import copy
import glob
import io
import json
import os
import os.path
import platform
import shutil
import stat
import sys
import warnings
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    List,
    Mapping,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
)

import setuptools
from distutils.errors import DistutilsArgError, DistutilsError, DistutilsGetoptError
from packaging.requirements import Requirement
from packaging.version import parse as parse_version
from setuptools.dist import Distribution as upstream_Distribution

from . import cmaker
from .command import (
    bdist,
    bdist_wheel,
    build,
    build_ext,
    build_py,
    clean,
    egg_info,
    generate_source_manifest,
    install,
    install_lib,
    install_scripts,
    sdist,
    test,
)
from .constants import (
    CMAKE_DEFAULT_EXECUTABLE,
    CMAKE_INSTALL_DIR,
    CMAKE_SPEC_FILE,
    set_skbuild_plat_name,
    skbuild_plat_name,
)
from .exceptions import (
    SKBuildError,
    SKBuildGeneratorNotFoundError,
    SKBuildInvalidFileInstallationError,
)
from .utils import (
    PythonModuleFinder,
    mkdir_p,
    parse_manifestin,
    to_platform_path,
    to_unix_path,
)


def create_skbuild_argparser() -> argparse.ArgumentParser:
    """Create and return a scikit-build argument parser."""
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "--build-type", default="Release", metavar="", help="specify the CMake build type (e.g. Debug or Release)"
    )
    parser.add_argument("-G", "--generator", metavar="", help="specify the CMake build system generator")
    parser.add_argument("-j", metavar="N", type=int, dest="jobs", help="allow N build jobs at once")
    parser.add_argument("--cmake-executable", default=None, metavar="", help="specify the path to the cmake executable")
    parser.add_argument(
        "--install-target",
        default=None,
        metavar="",
        help="specify the CMake target performing the install. " "If not provided, uses the target ``install``",
    )
    parser.add_argument(
        "--skip-generator-test",
        action="store_true",
        help="skip generator test when a generator is explicitly selected using --generator",
    )
    return parser


def _is_cmake_configure_argument(arg: str) -> bool:
    """Return True if ``arg`` is a relevant argument to pass to cmake when configuring a project."""

    for cmake_arg in (
        "-C",  # initial-cache
        "-D",  # <var>[:<type>]=<value>
    ):
        if arg.startswith(cmake_arg):
            return True
    return False


def parse_skbuild_args(
    args: Sequence[str], cmake_args: List[str], build_tool_args: List[str]
) -> Tuple[List[str], Optional[str], bool]:
    """
    Parse arguments in the scikit-build argument set. Convert specified
    arguments to proper format and append to cmake_args and build_tool_args.
    Returns the tuple ``(remaining arguments, cmake executable, skip_generator_test)``.
    """
    parser = create_skbuild_argparser()

    # Consider CMake arguments passed as global setuptools options
    cmake_args.extend([arg for arg in args if _is_cmake_configure_argument(arg)])
    # ... and remove them from the list
    args = [arg for arg in args if not _is_cmake_configure_argument(arg)]

    namespace, remaining_args = parser.parse_known_args(args)

    # Construct CMake argument list
    cmake_args.append("-DCMAKE_BUILD_TYPE:STRING=" + namespace.build_type)
    if namespace.generator is not None:
        cmake_args.extend(["-G", namespace.generator])

    # Construct build tool argument list
    build_tool_args.extend(["--config", namespace.build_type])
    if namespace.jobs is not None:
        build_tool_args.extend(["-j", str(namespace.jobs)])
    if namespace.install_target is not None:
        build_tool_args.extend(["--install-target", namespace.install_target])

    if namespace.generator is None and namespace.skip_generator_test is True:
        sys.exit("ERROR: Specifying --skip-generator-test requires --generator to also be specified.")

    return remaining_args, namespace.cmake_executable, namespace.skip_generator_test


def parse_args() -> Tuple[List[str], Optional[str], bool, List[str], List[str]]:
    """This function parses the command-line arguments ``sys.argv`` and returns
    the tuple ``(setuptools_args, cmake_executable, skip_generator_test, cmake_args, build_tool_args)``
    where each ``*_args`` element corresponds to a set of arguments separated by ``--``."""
    dutils: List[str] = []
    cmake: List[str] = []
    make: List[str] = []
    argsets = [dutils, cmake, make]
    i = 0
    separator = "--"

    for arg in sys.argv:
        if arg == separator:
            i += 1
            if i >= len(argsets):
                sys.exit(f"ERROR: Too many {separator!r} separators provided (expected at most {len(argsets) - 1}).")
        else:
            argsets[i].append(arg)

    dutils, cmake_executable, skip_generator_test = parse_skbuild_args(dutils, cmake, make)

    return dutils, cmake_executable, skip_generator_test, cmake, make


@contextlib.contextmanager
def _capture_output() -> Generator[List[Union[io.StringIO, str]], None, None]:
    out: List[Union[io.StringIO, str]]

    with contextlib.redirect_stdout(io.StringIO()) as stdout:
        with contextlib.redirect_stderr(io.StringIO()) as stderr:
            out = [stdout, stderr]
            yield out

    assert isinstance(out[0], io.StringIO)
    assert isinstance(out[1], io.StringIO)
    out[0] = out[0].getvalue()
    out[1] = out[1].getvalue()


def _parse_setuptools_arguments(
    setup_attrs: Mapping[str, Any]
) -> Tuple[bool, bool, List[str], bool, bool, bool, str, bool]:
    """This function instantiates a Distribution object and
    parses the command line arguments.

    It returns the tuple ``(display_only, help_commands, commands, hide_listing, force_cmake, skip_cmake, plat_name)``
    where

    - display_only is a boolean indicating if an argument like '--help',
      '--help-commands' or '--author' was passed.
    - help_commands is a boolean indicating if argument '--help-commands'
      was passed.
    - commands contains the list of commands that were passed.
    - hide_listing is a boolean indicating if the list of files being included
      in the distribution is displayed or not.
    - force_cmake a boolean indicating that CMake should always be executed.
    - skip_cmake is a boolean indicating if the execution of CMake should
      explicitly be skipped.
    - plat_name is a string identifying the platform name to embed in generated
      filenames. It defaults to :func:`skbuild.constants.skbuild_plat_name()`.
    - build_ext_inplace is a boolean indicating if ``build_ext`` command was
      specified along with the --inplace argument.

    Otherwise it raises DistutilsArgError exception if there are
    any error on the command-line, and it raises DistutilsGetoptError
    if there any error in the command 'options' attribute.

    The code has been adapted from the setup() function available
    in distutils/core.py.
    """
    setup_attrs = dict(setup_attrs)

    setup_attrs["script_name"] = os.path.basename(sys.argv[0])

    dist = upstream_Distribution(setup_attrs)

    # Update class attribute to also ensure the argument is processed
    # when ``setuptools.setup`` is called.
    upstream_Distribution.global_options.extend(  # type: ignore[attr-defined]
        [
            ("hide-listing", None, "do not display list of files being included in the distribution"),
            ("force-cmake", None, "always run CMake"),
            ("skip-cmake", None, "do not run CMake"),
        ]
    )

    # Find and parse the config file(s): they will override options from
    # the setup script, but be overridden by the command line.
    dist.parse_config_files()

    # Parse the command line and override config files; any
    # command-line errors are the end user's fault, so turn them into
    # SystemExit to suppress tracebacks.

    with _capture_output():
        result = dist.parse_command_line()  # type: ignore[attr-defined]
        display_only = not result
        if not hasattr(dist, "hide_listing"):
            dist.hide_listing = False  # type: ignore[attr-defined]
        if not hasattr(dist, "force_cmake"):
            dist.force_cmake = False  # type: ignore[attr-defined]
        if not hasattr(dist, "skip_cmake"):
            dist.skip_cmake = False  # type: ignore[attr-defined]

    plat_names = set()
    for cmd in [dist.get_command_obj(command) for command in dist.commands]:  # type: ignore[attr-defined]
        plat_name = getattr(cmd, "plat_name", None)
        if plat_name is not None:
            plat_names.add(plat_name)
    if not plat_names:
        plat_names.add(None)
    elif len(plat_names) > 1:
        names = ", ".join(plat_names)
        msg = f"--plat-name is ambiguous: {names}"
        raise SKBuildError(msg)
    plat_name = list(plat_names)[0]

    build_ext_cmd = dist.get_command_obj("build_ext")
    build_ext_inplace: bool = getattr(build_ext_cmd, "inplace", False)

    return (
        display_only,
        dist.help_commands,  # type: ignore[attr-defined]
        dist.commands,  # type: ignore[attr-defined]
        dist.hide_listing,  # type: ignore[attr-defined]
        dist.force_cmake,  # type: ignore[attr-defined]
        dist.skip_cmake,  # type: ignore[attr-defined]
        plat_name,
        build_ext_inplace,
    )


def _check_skbuild_parameters(cmake_install_dir: str, cmake_source_dir: str) -> None:
    if os.path.isabs(cmake_install_dir):
        msg = (
            "\n  setup parameter 'cmake_install_dir' is set to "
            "an absolute path. A relative path is expected.\n"
            f"    Project Root  : {os.getcwd()}\n"
            f"    CMake Install Directory: {cmake_install_dir}\n"
        )
        raise SKBuildError(msg)

    if not os.path.exists(os.path.abspath(cmake_source_dir)):
        msg = (
            "\n  setup parameter 'cmake_source_dir' set to "
            "a nonexistent directory.\n"
            f"    Project Root  : {os.getcwd()}\n"
            f"    CMake Source Directory: {cmake_source_dir}\n"
        )
        raise SKBuildError(msg)


def strip_package(package_parts: Sequence[str], module_file: str) -> str:
    """Given ``package_parts`` (e.g. ``['foo', 'bar']``) and a
    ``module_file`` (e.g. ``foo/bar/jaz/rock/roll.py``), starting
    from the left, this function will strip the parts of the path
    matching the package parts and return a new string
    (e.g ``jaz/rock/roll.py``).

    The function will work as expected for either Windows or Unix-style
    ``module_file`` and this independently of the platform.
    """
    if not package_parts or os.path.isabs(module_file):
        return module_file

    package = "/".join(package_parts)
    module_dir = os.path.dirname(module_file.replace("\\", "/"))

    module_dir = module_dir[: len(package)]

    return module_file[len(package) + 1 :] if package != "" and module_dir.startswith(package) else module_file


def _package_data_contain_module(module: Tuple[str, str, str], package_data: Mapping[str, List[str]]) -> bool:
    """Return True if the ``module`` is contained
    in the ``package_data``.

    ``module`` is a tuple of the form
    ``(package, modulename, module_file)``.
    """
    (package, _, module_file) = module
    if package not in package_data:
        return False
    # We need to strip the package because a module entry
    # usually looks like this:
    #
    #   ('foo.bar', 'module', 'foo/bar/module.py')
    #
    # and the entry in package_data would look like this:
    #
    #   {'foo.bar' : ['module.py']}
    if strip_package(package.split("."), module_file) in package_data[package]:
        return True
    return False


def _should_run_cmake(commands: Sequence[str], cmake_with_sdist: bool) -> bool:
    """Return True if at least one command requiring ``cmake`` to run
    is found in ``commands``."""
    given_commands = set(commands)
    expected_commands = {
        "build",
        "build_ext",
        "develop",
        "install",
        "install_lib",
        "bdist",
        "bdist_dumb",
        "bdist_egg",
        "bdist_rpm",
        "bdist_wininst",
        "bdist_wheel",
        "test",
    }

    if expected_commands & given_commands:
        return True
    if "sdist" in given_commands and cmake_with_sdist:
        return True
    return False


def _save_cmake_spec(args: Mapping[str, Any]) -> None:
    """Save the CMake spec to disk"""
    # We use JSON here because readability is more important than performance
    with contextlib.suppress(OSError):
        os.makedirs(os.path.dirname(CMAKE_SPEC_FILE()))

    with open(CMAKE_SPEC_FILE(), "w+", encoding="utf-8") as fp:
        json.dump(args, fp)


def _load_cmake_spec() -> Any:
    """Load and return the CMake spec from disk"""
    with contextlib.suppress(OSError, ValueError), open(CMAKE_SPEC_FILE(), encoding="utf-8") as fp:
        return json.load(fp)
    return None


# pylint:disable=too-many-locals, too-many-branches
def setup(  # noqa: C901
    *,
    cmake_args: Sequence[str] = (),
    cmake_install_dir: str = "",
    cmake_source_dir: str = "",
    cmake_with_sdist: bool = False,
    cmake_languages: Sequence[str] = ("C", "CXX"),
    cmake_minimum_required_version: Optional[str] = None,
    cmake_process_manifest_hook: Optional[Callable[[List[str]], List[str]]] = None,
    cmake_install_target: str = "install",
    **kw: Any,
) -> None:
    """This function wraps setup() so that we can run cmake, make,
    CMake build, then proceed as usual with setuptools, appending the
    CMake-generated output as necessary.

    The CMake project is re-configured only if needed. This is achieved by (1) retrieving the environment mapping
    associated with the generator set in the ``CMakeCache.txt`` file, (2) saving the CMake configure arguments and
    version in :func:`skbuild.constants.CMAKE_SPEC_FILE()`: and (3) re-configuring only if either the generator or
    the CMake specs change.
    """

    # If any, strip ending slash from each package directory
    # Regular setuptools does not support this
    # TODO: will become an error in the future
    if "package_dir" in kw:
        for package, prefix in kw["package_dir"].items():
            if prefix.endswith("/"):
                msg = f"package_dir={{{package!r}: {prefix!r}}} ends with a trailing slash, which is not supported by setuptools."
                warnings.warn(msg, FutureWarning, stacklevel=2)
                kw["package_dir"][package] = prefix[:-1]

    sys.argv, cmake_executable, skip_generator_test, cmake_args_from_args, make_args = parse_args()

    # work around https://bugs.python.org/issue1011113
    # (patches provided, but no updates since 2014)
    cmdclass = kw.get("cmdclass", {})
    cmdclass["build"] = cmdclass.get("build", build.build)
    cmdclass["build_py"] = cmdclass.get("build_py", build_py.build_py)
    cmdclass["build_ext"] = cmdclass.get("build_ext", build_ext.build_ext)
    cmdclass["install"] = cmdclass.get("install", install.install)
    cmdclass["install_lib"] = cmdclass.get("install_lib", install_lib.install_lib)
    cmdclass["install_scripts"] = cmdclass.get("install_scripts", install_scripts.install_scripts)
    cmdclass["clean"] = cmdclass.get("clean", clean.clean)
    cmdclass["sdist"] = cmdclass.get("sdist", sdist.sdist)
    cmdclass["bdist"] = cmdclass.get("bdist", bdist.bdist)
    cmdclass["bdist_wheel"] = cmdclass.get("bdist_wheel", bdist_wheel.bdist_wheel)
    cmdclass["egg_info"] = cmdclass.get("egg_info", egg_info.egg_info)
    cmdclass["generate_source_manifest"] = cmdclass.get(
        "generate_source_manifest", generate_source_manifest.generate_source_manifest
    )
    cmdclass["test"] = cmdclass.get("test", test.test)
    kw["cmdclass"] = cmdclass

    # Extract setup keywords specific to scikit-build and remove them from kw.
    # Removing the keyword from kw need to be done here otherwise, the
    # following call to _parse_setuptools_arguments would complain about
    # unknown setup options.

    # ... and validate them
    try:
        _check_skbuild_parameters(cmake_install_dir, cmake_source_dir)
    except SKBuildError as ex:
        import traceback  # pylint: disable=import-outside-toplevel

        print("Traceback (most recent call last):", file=sys.stderr)
        traceback.print_tb(sys.exc_info()[2])
        print(file=sys.stderr, flush=True)
        sys.exit(ex)  # type: ignore[arg-type]

    # Convert source dir to a path relative to the root
    # of the project
    if cmake_source_dir == ".":
        cmake_source_dir = ""
    if os.path.isabs(cmake_source_dir):
        cmake_source_dir = os.path.relpath(cmake_source_dir)

    # Skip running CMake in the following cases:
    # * flag "--skip-cmake" is provided
    # * "display only" argument is provided (e.g  '--help', '--author', ...)
    # * no command-line arguments or invalid ones are provided
    # * no command requiring cmake is provided
    # * no CMakeLists.txt if found
    display_only = has_invalid_arguments = help_commands = False
    force_cmake = skip_cmake = False
    commands: List[str] = []
    try:
        (
            display_only,
            help_commands,
            commands,
            hide_listing,
            force_cmake,
            skip_cmake,
            plat_name,
            build_ext_inplace,
        ) = _parse_setuptools_arguments(kw)
    except (DistutilsArgError, DistutilsGetoptError):
        has_invalid_arguments = True
        plat_name = None
        hide_listing = False

    has_cmakelists = os.path.exists(os.path.join(cmake_source_dir, "CMakeLists.txt"))
    if not has_cmakelists:
        print("skipping skbuild (no CMakeLists.txt found)", flush=True)

    skip_skbuild = (
        display_only or has_invalid_arguments or not _should_run_cmake(commands, cmake_with_sdist) or not has_cmakelists
    )
    if skip_skbuild and not force_cmake:
        if help_commands:
            # Prepend scikit-build help. Generate option descriptions using
            # argparse.
            skbuild_parser = create_skbuild_argparser()
            arg_descriptions = [line for line in skbuild_parser.format_help().split("\n") if line.startswith("  ")]
            print("scikit-build options:")
            print("\n".join(arg_descriptions))
            print()
            print('Arguments following a "--" are passed directly to CMake ' "(e.g. -DMY_VAR:BOOL=TRUE).")
            print('Arguments following a second "--" are passed directly to ' " the build tool.")
            print(flush=True)
        return setuptools.setup(**kw)

    developer_mode = "develop" in commands or "test" in commands or build_ext_inplace

    packages = kw.get("packages", [])
    package_dir = kw.get("package_dir", {})
    package_data = {k: copy.copy(v) for k, v in kw.get("package_data", {}).items()}

    py_modules = kw.get("py_modules", [])
    new_py_modules = {py_module: False for py_module in py_modules}

    scripts = kw.get("scripts", [])
    new_scripts = {script: False for script in scripts}

    data_files = {(parent_dir or "."): set(file_list) for parent_dir, file_list in kw.get("data_files", [])}

    # Since CMake arguments provided through the command line have more
    # weight and when CMake is given multiple times a argument, only the last
    # one is considered, let's prepend the one provided in the setup call.
    cmake_args = list(cmake_args) + cmake_args_from_args

    # Handle cmake_install_target
    # get the target (next item after '--install-target') or return '' if no --install-target
    cmake_install_target_from_command = next(
        (make_args[index + 1] for index, item in enumerate(make_args) if item == "--install-target"), ""
    )
    cmake_install_target_from_setup = cmake_install_target
    # Setting target from command takes precedence
    # cmake_install_target_from_setup has the default 'install',
    # so cmake_install_target would never be empty.
    if cmake_install_target_from_command:
        cmake_install_target = cmake_install_target_from_command
    else:
        cmake_install_target = cmake_install_target_from_setup

    # Parse CMAKE_ARGS
    env_cmake_args = os.environ["CMAKE_ARGS"].split() if "CMAKE_ARGS" in os.environ else []
    env_cmake_args = [s for s in env_cmake_args if "CMAKE_INSTALL_PREFIX" not in s]

    # Using the environment variable CMAKE_ARGS has lower precedence than manual options
    cmake_args = env_cmake_args + cmake_args

    if sys.platform == "darwin":

        # If no ``--plat-name`` argument was passed, set default value.
        if plat_name is None:
            plat_name = skbuild_plat_name()

        (_, version, machine) = plat_name.split("-")

        # The loop here allows for CMAKE_OSX_* command line arguments to overload
        # values passed with either the ``--plat-name`` command-line argument
        # or the ``cmake_args`` setup option.
        for cmake_arg in cmake_args:
            if "CMAKE_OSX_DEPLOYMENT_TARGET" in cmake_arg:
                version = cmake_arg.split("=")[1]
            if "CMAKE_OSX_ARCHITECTURES" in cmake_arg:
                machine = cmake_arg.split("=")[1]
                if set(machine.split(";")) == {"x86_64", "arm64"}:
                    machine = "universal2"
            elif "CMAKE_SYSTEM_PROCESSOR" in cmake_arg:
                machine = cmake_arg.split("=")[1]

        assert machine in {"x86_64", "arm64", "universal2"}, f"macOS arch {machine} not understood"

        set_skbuild_plat_name(f"macosx-{version}-{machine}")

        # Set platform env. variable so that commands (e.g. bdist_wheel)
        # uses this information. The _PYTHON_HOST_PLATFORM env. variable is
        # used in distutils.util.get_platform() function.
        os.environ.setdefault("_PYTHON_HOST_PLATFORM", skbuild_plat_name())

        # Set CMAKE_OSX_DEPLOYMENT_TARGET and CMAKE_OSX_ARCHITECTURES if not already
        # specified
        (_, version, machine) = skbuild_plat_name().split("-")
        if not cmaker.has_cmake_cache_arg(cmake_args, "CMAKE_OSX_DEPLOYMENT_TARGET"):
            cmake_args.append(f"-DCMAKE_OSX_DEPLOYMENT_TARGET:STRING={version}")
        if not cmaker.has_cmake_cache_arg(cmake_args, "CMAKE_OSX_ARCHITECTURES"):
            machine_archs = "x86_64;arm64" if machine == "universal2" else machine
            cmake_args.append(f"-DCMAKE_OSX_ARCHITECTURES:STRING={machine_archs}")

    # Install cmake if listed in `setup_requires`
    for package in kw.get("setup_requires", []):
        if Requirement(package).name == "cmake":
            setup_requires = [package]
            dist = upstream_Distribution({"setup_requires": setup_requires})
            dist.fetch_build_eggs(setup_requires)  # type: ignore[no-untyped-call]

            with contextlib.suppress(ImportError):
                # Considering packages associated with "setup_requires" keyword are
                # installed in .eggs subdirectory without honoring setuptools "console_scripts"
                # entry_points and without settings the expected executable permissions, we are
                # taking care of it below.

                # A local "cmake" folder can be imported by mistake, keep going if it is
                from cmake import (
                    CMAKE_BIN_DIR,  # pylint: disable=import-outside-toplevel
                )

                for executable in ("cmake", "cpack", "ctest"):
                    executable = os.path.join(CMAKE_BIN_DIR, executable)
                    if platform.system().lower() == "windows":
                        executable += ".exe"
                    st = os.stat(executable)
                    permissions = st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
                    os.chmod(executable, permissions)
                cmake_executable = os.path.join(CMAKE_BIN_DIR, "cmake")
                break

    # Languages are used to determine a working generator

    try:
        if cmake_executable is None:
            cmake_executable = CMAKE_DEFAULT_EXECUTABLE
        cmkr = cmaker.CMaker(cmake_executable)
        if not skip_cmake:
            if cmake_minimum_required_version is not None:
                if parse_version(cmkr.cmake_version) < parse_version(cmake_minimum_required_version):
                    msg = f"CMake version {cmake_minimum_required_version} or higher is required. CMake version {cmkr.cmake_version} is being used"
                    raise SKBuildError(msg)
            # Used to confirm that the cmake executable is the same, and that the environment
            # didn't change
            cmake_spec = {
                "args": [shutil.which(CMAKE_DEFAULT_EXECUTABLE)] + cmake_args,
                "version": cmkr.cmake_version,
                "environment": {
                    "PYTHONNOUSERSITE": os.environ.get("PYTHONNOUSERSITE"),
                    "PYTHONPATH": os.environ.get("PYTHONPATH"),
                },
            }

            # skip the configure step for a cached build
            env = cmkr.get_cached_generator_env()
            if env is None or cmake_spec != _load_cmake_spec():
                env = cmkr.configure(
                    cmake_args,
                    skip_generator_test=skip_generator_test,
                    cmake_source_dir=cmake_source_dir,
                    cmake_install_dir=cmake_install_dir,
                    languages=cmake_languages,
                )
                _save_cmake_spec(cmake_spec)
            cmkr.make(make_args, install_target=cmake_install_target, env=env)
    except SKBuildGeneratorNotFoundError as ex:
        sys.exit(ex)  # type: ignore[arg-type]
    except SKBuildError as ex:
        import traceback  # pylint: disable=import-outside-toplevel

        print("Traceback (most recent call last):", file=sys.stderr)
        traceback.print_tb(sys.exc_info()[2])
        print(file=sys.stderr, flush=True)
        sys.exit(ex)  # type: ignore[arg-type]

    # If needed, set reasonable defaults for package_dir
    for package in packages:
        if package not in package_dir:
            package_dir[package] = package.replace(".", "/")
            if "" in package_dir:
                package_dir[package] = to_unix_path(os.path.join(package_dir[""], package_dir[package]))

    kw["package_dir"] = package_dir

    package_prefixes = _collect_package_prefixes(package_dir, packages)

    # This hook enables custom processing of the cmake manifest
    cmake_manifest = cmkr.install()
    process_manifest = cmake_process_manifest_hook
    if process_manifest is not None:
        if callable(process_manifest):
            cmake_manifest = process_manifest(cmake_manifest)
        else:
            raise SKBuildError("The cmake_process_manifest_hook argument should be callable.")

    _classify_installed_files(
        cmake_manifest,
        package_data,
        package_prefixes,
        py_modules,
        new_py_modules,
        scripts,
        new_scripts,
        data_files,
        cmake_source_dir,
        cmake_install_dir,
    )

    original_manifestin_data_files = []
    if kw.get("include_package_data", False):
        original_manifestin_data_files = parse_manifestin(os.path.join(os.getcwd(), "MANIFEST.in"))
        for path in original_manifestin_data_files:
            _classify_file(
                path, package_data, package_prefixes, py_modules, new_py_modules, scripts, new_scripts, data_files
            )

    if developer_mode:
        # Copy packages
        for package, package_file_list in package_data.items():
            for package_file in package_file_list:
                package_file = os.path.join(package_dir[package], package_file)
                cmake_file = os.path.join(CMAKE_INSTALL_DIR(), package_file)
                if os.path.exists(cmake_file):
                    _copy_file(cmake_file, package_file, hide_listing)

        # Copy modules
        for py_module in py_modules:
            package_file = py_module + ".py"
            cmake_file = os.path.join(CMAKE_INSTALL_DIR(), package_file)
            if os.path.exists(cmake_file):
                _copy_file(cmake_file, package_file, hide_listing)
    else:
        _consolidate_package_modules(cmake_source_dir, packages, package_dir, py_modules, package_data, hide_listing)

        original_package_data = kw.get("package_data", {}).copy()
        _consolidate_package_data_files(original_package_data, package_prefixes, hide_listing)

        for data_file in original_manifestin_data_files:
            dest_data_file = os.path.join(CMAKE_INSTALL_DIR(), data_file)
            _copy_file(data_file, dest_data_file, hide_listing)

    kw["package_data"] = package_data
    kw["package_dir"] = {
        package: (
            os.path.join(CMAKE_INSTALL_DIR(), prefix)
            if os.path.exists(os.path.join(CMAKE_INSTALL_DIR(), prefix))
            else prefix
        )
        for prefix, package in package_prefixes
    }

    kw["scripts"] = [
        os.path.join(CMAKE_INSTALL_DIR(), script) if mask else script for script, mask in new_scripts.items()
    ]

    kw["data_files"] = [(parent_dir, list(file_set)) for parent_dir, file_set in data_files.items()]

    if "zip_safe" not in kw:
        kw["zip_safe"] = False

    # Adapted from espdev/ITKPythonInstaller/setup.py.in
    class BinaryDistribution(upstream_Distribution):  # pylint: disable=missing-class-docstring
        def has_ext_modules(self) -> bool:  # pylint: disable=no-self-use,missing-function-docstring
            return has_cmakelists

    kw["distclass"] = BinaryDistribution

    print(flush=True)

    return setuptools.setup(**kw)


def _collect_package_prefixes(
    package_dir: Dict[str, str], packages: List[Union[Any, str]]
) -> List[Union[Any, Tuple[str, str]]]:
    """
    Collect the list of prefixes for all packages

    The list is used to match paths in the install manifest to packages
    specified in the setup.py script.

    The list is sorted in decreasing order of prefix length so that paths are
    matched with their immediate parent package, instead of any of that
    package's ancestors.

    For example, consider the project structure below.  Assume that the
    setup call was made with a package list featuring "top" and "top.bar", but
    not "top.not_a_subpackage".

    ::

        top/                -> top/
          __init__.py       -> top/__init__.py                 (parent: top)
          foo.py            -> top/foo.py                      (parent: top)
          bar/              -> top/bar/                        (parent: top)
            __init__.py     -> top/bar/__init__.py             (parent: top.bar)

          not_a_subpackage/ -> top/not_a_subpackage/           (parent: top)
            data_0.txt      -> top/not_a_subpackage/data_0.txt (parent: top)
            data_1.txt      -> top/not_a_subpackage/data_1.txt (parent: top)

    The paths in the generated install manifest are matched to packages
    according to the parents indicated on the right.  Only packages that are
    specified in the setup() call are considered.  Because of the sort order,
    the data files on the bottom would have been mapped to
    "top.not_a_subpackage" instead of "top", proper -- had such a package been
    specified.
    """
    return sorted(
        ((package_dir[package].replace(".", "/"), package) for package in packages),
        key=lambda tup: len(tup[0]),
        reverse=True,
    )


def _classify_installed_files(
    install_paths: Sequence[str],
    package_data: Dict[str, List[str]],
    package_prefixes: Sequence[Tuple[str, str]],
    py_modules: Sequence[str],
    new_py_modules: Dict[str, bool],
    scripts: Sequence[str],
    new_scripts: Dict[str, bool],
    data_files: Dict[Any, Any],
    cmake_source_dir: str,
    _cmake_install_dir: str,
) -> None:
    assert not os.path.isabs(cmake_source_dir)
    assert cmake_source_dir != "."

    install_root = os.path.join(os.getcwd(), CMAKE_INSTALL_DIR())
    for path in install_paths:
        # if this installed file is not within the project root, complain and
        # exit
        if not to_platform_path(path).startswith(CMAKE_INSTALL_DIR()):
            msg = (
                "\n  CMake-installed files must be within the project root.\n"
                f"    Project Root  : {install_root}\n"
                f"    Violating File: {to_platform_path(path)}\n"
            )
            raise SKBuildInvalidFileInstallationError(msg)

        # peel off the 'skbuild' prefix
        path = to_unix_path(os.path.relpath(path, CMAKE_INSTALL_DIR()))

        _classify_file(
            path, package_data, package_prefixes, py_modules, new_py_modules, scripts, new_scripts, data_files
        )


def _classify_file(
    path: str,
    package_data: Dict[str, List[str]],
    package_prefixes: Sequence[Tuple[str, str]],
    py_modules: Sequence[str],
    new_py_modules: Dict[str, bool],
    scripts: Sequence[str],
    new_scripts: Dict[str, bool],
    data_files: Dict[str, Set[str]],
) -> None:
    found_package = False
    found_module = False
    found_script = False

    path = to_unix_path(path)

    # check to see if path is part of a package
    for prefix, package in package_prefixes:
        if path.startswith(prefix + "/"):
            # peel off the package prefix
            path = to_unix_path(os.path.relpath(path, prefix))

            package_file_list = list(package_data.get(package, []))
            package_file_list.append(path)
            package_data[package] = package_file_list

            found_package = True
            break

    if found_package:
        return
    # If control reaches this point, then this installed file is not part of
    # a package.

    # check if path is a module
    for module in py_modules:
        if path.replace("/", ".") == ".".join((module, "py")):
            new_py_modules[module] = True
            found_module = True
            break

    if found_module:
        return
    # If control reaches this point, then this installed file is not a
    # module

    # if the file is a script, mark the corresponding script
    for script in scripts:
        if path == script:
            new_scripts[script] = True
            found_script = True
            break

    if found_script:
        return
    # If control reaches this point, then this installed file is not a
    # script

    # If control reaches this point, then we have installed files that are
    # not part of a package, not a module, nor a script.  Without any other
    # information, we can only treat it as a generic data file.
    parent_dir = os.path.dirname(path)
    file_set = data_files.get(parent_dir)
    if file_set is None:
        file_set = set()
        data_files[parent_dir] = file_set
    file_set.add(os.path.join(CMAKE_INSTALL_DIR(), path))


def _copy_file(src_file: str, dest_file: str, hide_listing: Union[bool, int] = True) -> None:
    """Copy ``src_file`` to ``dest_file`` ensuring parent directory exists.

    By default, message like `creating directory /path/to/package` and
    `copying directory /src/path/to/package -> path/to/package` are displayed
    on standard output. Setting ``hide_listing`` to False avoids message from
    being displayed.
    """
    # Create directory if needed
    dest_dir = os.path.dirname(dest_file)
    if dest_dir != "" and not os.path.exists(dest_dir):
        if not hide_listing:
            print(f"creating directory {dest_dir}", flush=True)
        mkdir_p(dest_dir)

    # Copy file
    if not hide_listing:
        print(f"copying {src_file} -> {dest_file}", flush=True)
    shutil.copyfile(src_file, dest_file)
    shutil.copymode(src_file, dest_file)


def _consolidate_package_modules(
    cmake_source_dir: str,
    packages: List[Union[Any, str]],
    package_dir: Dict[str, str],
    py_modules: List[Union[Any, str]],
    package_data: Dict[str, List[str]],
    hide_listing: Union[bool, int],
) -> None:
    """This function consolidates packages having modules located in
    both the source tree and the CMake install tree into one location.

    The one location is the CMake install tree
    (see :func:`.constants.CMAKE_INSTALL_DIR()`).

    Why ? This is a necessary evil because ``Setuptools`` keeps track of
    packages and modules files to install using a dictionary of lists where
    the key are package names (e.g ``foo.bar``) and the values are lists of
    module files (e.g ``['__init__.py', 'baz.py']``. Since this doesn't allow
    to "split" files associated with a given module in multiple location, one
    location is selected, and files are copied over.

    How? It currently searches for modules across both locations using
    the :class:`.utils.PythonModuleFinder`. then with the help
    of :func:`_package_data_contain_module`, it identifies which
    one are either already included or missing from the distribution.

    Once a module has been identified as ``missing``, it is both copied
    into the :func:`.constants.CMAKE_INSTALL_DIR()` and added to the
    ``package_data`` dictionary so that it can be considered by
    the upstream setup function.
    """

    try:
        # Search for python modules in both the current directory
        # and cmake install tree.
        modules = PythonModuleFinder(
            packages, package_dir, py_modules, alternative_build_base=CMAKE_INSTALL_DIR()
        ).find_all_modules()
    except DistutilsError as msg:
        raise SystemExit(f"error: {msg}") from None

    print(flush=True)

    for entry in modules:

        # Check if module file should be copied into the CMake install tree.
        if _package_data_contain_module(entry, package_data):
            continue

        (package, _, src_module_file) = entry

        # Copy missing module file
        if os.path.exists(src_module_file):
            dest_module_file = os.path.join(CMAKE_INSTALL_DIR(), src_module_file)
            _copy_file(src_module_file, dest_module_file, hide_listing)

        # Since the mapping in package_data expects the package to be associated
        # with a list of files relative to the directory containing the package,
        # the following section makes sure to strip the redundant part of the
        # module file path.
        # The redundant part should be stripped for both cmake_source_dir and
        # the package.
        package_parts = []
        if cmake_source_dir:
            package_parts = cmake_source_dir.split(os.path.sep)
        package_parts += package.split(".")

        stripped_module_file = strip_package(package_parts, src_module_file)

        # Update list of files associated with the corresponding package
        try:
            package_data[package].append(stripped_module_file)
        except KeyError:
            package_data[package] = [stripped_module_file]


def _consolidate_package_data_files(
    original_package_data: Dict[str, List[str]],
    package_prefixes: List[Union[Any, Tuple[str, str]]],
    hide_listing: Union[bool, int],
) -> None:
    """This function copies package data files specified using the ``package_data`` keyword
    into :func:`.constants.CMAKE_INSTALL_DIR()`.

    ::

        setup(...,
            packages=['mypkg'],
            package_dir={'mypkg': 'src/mypkg'},
            package_data={'mypkg': ['data/*.dat']},
            )

    Considering that (1) the packages associated with modules located in both the source tree and
    the CMake install tree are consolidated into the CMake install tree, and (2) the consolidated
    package path set in the ``package_dir`` dictionary and later used by setuptools to package
    (or install) modules and data files is :func:`.constants.CMAKE_INSTALL_DIR()`, copying the data files
    is required to ensure setuptools can find them when it uses the package directory.
    """
    project_root = os.getcwd()
    for prefix, package in package_prefixes:
        if package not in original_package_data:
            continue
        raw_patterns = original_package_data[package]
        for pattern in raw_patterns:
            expanded_package_dir = os.path.join(project_root, prefix, pattern)
            for src_data_file in glob.glob(expanded_package_dir):
                full_prefix_length = len(os.path.join(project_root, prefix)) + 1
                data_file = src_data_file[full_prefix_length:]
                dest_data_file = os.path.join(CMAKE_INSTALL_DIR(), prefix, data_file)
                _copy_file(src_data_file, dest_data_file, hide_listing)
