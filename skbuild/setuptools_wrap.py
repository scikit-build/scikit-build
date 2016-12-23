"""This module provides functionality for wrapping key infrastructure components
from distutils and setuptools.
"""

from __future__ import print_function

import os
import os.path
import sys
import argparse

from contextlib import contextmanager
from distutils.errors import (DistutilsArgError,
                              DistutilsError,
                              DistutilsGetoptError)
from shutil import copyfile, copymode

# XXX If 'six' becomes a dependency, use 'six.StringIO' instead.
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from setuptools import setup as upstream_setup
from setuptools.dist import Distribution as upstream_Distribution

from . import cmaker
from .command import (build, build_py, clean,
                      install, install_lib, install_scripts,
                      bdist, bdist_wheel, egg_info,
                      sdist, generate_source_manifest)
from .constants import CMAKE_INSTALL_DIR
from .exceptions import SKBuildError, SKBuildGeneratorNotFoundError
from .utils import (mkdir_p, PythonModuleFinder, to_platform_path, to_unix_path)


def create_skbuild_argparser():
    """Create and return a scikit-build argument parser.
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        '--build-type', default='Release', metavar='',
        help='specify the CMake build type (e.g. Debug or Release)')
    parser.add_argument(
        '-G', '--generator', metavar='',
        help='specify the CMake build system generator')
    parser.add_argument(
        '-j', metavar='N', type=int, dest='jobs',
        help='allow N build jobs at once')
    return parser


def parse_skbuild_args(args, cmake_args, build_tool_args):
    """
    Parse arguments in the scikit-build argument set. Convert specified
    arguments to proper format and append to cmake_args and build_tool_args.
    Returns remaining arguments.
    """
    parser = create_skbuild_argparser()
    namespace, remaining_args = parser.parse_known_args(args)

    # Construct CMake argument list
    cmake_args.append('-DCMAKE_BUILD_TYPE:STRING=' + namespace.build_type)
    if namespace.generator is not None:
        cmake_args.extend(['-G', namespace.generator])

    # Construct build tool argument list
    build_tool_args.extend(['--config', namespace.build_type])
    if namespace.jobs is not None:
        build_tool_args.extend(['-j', str(namespace.jobs)])

    return remaining_args


def parse_args():
    """This function parses the command-line arguments ``sys.argv`` and returns
    the tuple ``(setuptools_args, cmake_args, build_tool_args)`` where each
    element corresponds to a set of arguments separated by ``--``."""
    dutils = []
    cmake = []
    make = []
    argsets = [dutils, cmake, make]
    i = 0
    separator = '--'

    for arg in sys.argv:
        if arg == separator:
            i += 1
            if i >= len(argsets):
                sys.exit(
                    "ERROR: Too many \"{}\" separators provided "
                    "(expected at most {}).".format(separator,
                                                    len(argsets) - 1))
        else:
            argsets[i].append(arg)

    dutils = parse_skbuild_args(dutils, cmake, make)

    return dutils, cmake, make


@contextmanager
def _capture_output():
    oldout, olderr = sys.stdout, sys.stderr
    try:
        out = [StringIO(), StringIO()]
        sys.stdout, sys.stderr = out
        yield out
    finally:
        sys.stdout, sys.stderr = oldout, olderr
        out[0] = out[0].getvalue()
        out[1] = out[1].getvalue()


def _parse_setuptools_arguments(setup_attrs):
    """This function instantiates a Distribution object and
    parses the command line arguments.

    It returns the tuple
        ``(display_only, help_commands, commands,
        hide_listing, force_cmake, skip_cmake)``
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

    Otherwise it raises DistutilsArgError exception if there are
    any error on the command-line, and it raises DistutilsGetoptError
    if there any error in the command 'options' attribute.

    The code has been adapted from the setup() function available
    in distutils/core.py.
    """
    setup_attrs = dict(setup_attrs)

    setup_attrs['script_name'] = os.path.basename(sys.argv[0])

    dist = upstream_Distribution(setup_attrs)

    # Update class attribute to also ensure the argument is processed
    # when ``upstream_setup`` is called.
    # pylint:disable=no-member
    upstream_Distribution.global_options.append(
        ('hide-listing', None, "do not display list of files being "
                               "included in the distribution")
    )
    # pylint:disable=no-member
    upstream_Distribution.global_options.append(
        ('force-cmake', None, "always run CMake")
    )
    # pylint:disable=no-member
    upstream_Distribution.global_options.append(
        ('skip-cmake', None, "do not run CMake")
    )

    # Find and parse the config file(s): they will override options from
    # the setup script, but be overridden by the command line.
    dist.parse_config_files()

    # Parse the command line and override config files; any
    # command-line errors are the end user's fault, so turn them into
    # SystemExit to suppress tracebacks.

    with _capture_output():
        result = dist.parse_command_line()
        display_only = not result
        if not hasattr(dist, 'hide_listing'):
            dist.hide_listing = False
        if not hasattr(dist, 'force_cmake'):
            dist.force_cmake = False
        if not hasattr(dist, 'skip_cmake'):
            dist.skip_cmake = False

    return (display_only, dist.help_commands, dist.commands,
            dist.hide_listing, dist.force_cmake, dist.skip_cmake)


def _check_skbuild_parameters(skbuild_kw):
    cmake_install_dir = skbuild_kw['cmake_install_dir']
    if os.path.isabs(cmake_install_dir):
        raise SKBuildError((
            "\n  setup parameter 'cmake_install_dir' is set to "
            "an absolute path. A relative path is expected.\n"
            "    Project Root  : {}\n"
            "    CMake Install Directory: {}\n").format(
                os.getcwd(), cmake_install_dir
            ))

    cmake_source_dir = skbuild_kw['cmake_source_dir']
    if not os.path.exists(os.path.abspath(cmake_source_dir)):
        raise SKBuildError((
            "\n  setup parameter 'cmake_source_dir' set to "
            "a nonexistent directory.\n"
            "    Project Root  : {}\n"
            "    CMake Source Directory: {}\n").format(
                os.getcwd(), cmake_source_dir
            ))


def strip_package(package_parts, module_file):
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

    module_dir = module_dir[:len(package)]

    return module_file[len(package) + 1:] if module_dir.startswith(
        package) else module_file


def _package_data_contain_module(module, package_data):
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
    if (strip_package(package.split("."), module_file)
            in package_data[package]):
        return True
    return False


def _should_run_cmake(commands, cmake_with_sdist):
    """Return True if at least one command requiring ``cmake`` to run
    is found in ``commands``."""
    for expected_command in [
        "build",
        "develop",
        "install",
        "install_lib",
        "bdist",
        "bdist_dumb",
        "bdist_egg"
        "bdist_rpm",
        "bdist_wininst",
        "bdist_wheel",
    ]:
        if expected_command in commands:
            return True
    if "sdist" in commands and cmake_with_sdist:
        return True
    return False


# pylint:disable=too-many-locals, too-many-branches
def setup(*args, **kw):  # noqa: C901
    """This function wraps setup() so that we can run cmake, make,
    CMake build, then proceed as usual with setuptools, appending the
    CMake-generated output as necessary.
    """
    sys.argv, cmake_args, make_args = parse_args()

    # work around https://bugs.python.org/issue1011113
    # (patches provided, but no updates since 2014)
    cmdclass = kw.get('cmdclass', {})
    cmdclass['build'] = cmdclass.get('build', build.build)
    cmdclass['build_py'] = cmdclass.get('build_py', build_py.build_py)
    cmdclass['install'] = cmdclass.get('install', install.install)
    cmdclass['install_lib'] = cmdclass.get('install_lib',
                                           install_lib.install_lib)
    cmdclass['install_scripts'] = cmdclass.get('install_scripts',
                                               install_scripts.install_scripts)
    cmdclass['clean'] = cmdclass.get('clean', clean.clean)
    cmdclass['sdist'] = cmdclass.get('sdist', sdist.sdist)
    cmdclass['bdist'] = cmdclass.get('bdist', bdist.bdist)
    cmdclass['bdist_wheel'] = cmdclass.get(
        'bdist_wheel', bdist_wheel.bdist_wheel)
    cmdclass['egg_info'] = cmdclass.get('egg_info', egg_info.egg_info)
    cmdclass['generate_source_manifest'] = cmdclass.get(
        'generate_source_manifest',
        generate_source_manifest.generate_source_manifest)
    kw['cmdclass'] = cmdclass

    # Extract setup keywords specific to scikit-build and remove them from kw.
    # Removing the keyword from kw need to be done here otherwise, the
    # following call to _parse_setuptools_arguments would complain about
    # unknown setup options.
    parameters = {
        'cmake_args': [],
        'cmake_install_dir': '',
        'cmake_source_dir': '',
        'cmake_with_sdist': False
    }
    skbuild_kw = {param: kw.pop(param, parameters[param])
                  for param in parameters}

    # ... and validate them
    try:
        _check_skbuild_parameters(skbuild_kw)
    except SKBuildError as ex:
        import traceback
        print("Traceback (most recent call last):")
        traceback.print_tb(sys.exc_info()[2])
        print('')
        sys.exit(ex)

    # Convert source dir to a path relative to the root
    # of the project
    cmake_source_dir = skbuild_kw['cmake_source_dir']
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
    commands = []
    try:
        (display_only, help_commands, commands,
         hide_listing, force_cmake, skip_cmake) = \
            _parse_setuptools_arguments(kw)
    except (DistutilsArgError, DistutilsGetoptError):
        has_invalid_arguments = True

    has_cmakelists = os.path.exists(
        os.path.join(cmake_source_dir, "CMakeLists.txt"))
    if not has_cmakelists:
        print('skipping skbuild (no CMakeLists.txt found)')

    skip_cmake = (skip_cmake
                  or display_only
                  or has_invalid_arguments
                  or not _should_run_cmake(commands,
                                           skbuild_kw["cmake_with_sdist"])
                  or not has_cmakelists)
    if skip_cmake and not force_cmake:
        if help_commands:
            # Prepend scikit-build help. Generate option descriptions using
            # argparse.
            skbuild_parser = create_skbuild_argparser()
            arg_descriptions = [
                line for line in skbuild_parser.format_help().split('\n')
                if line.startswith('  ')
                ]
            print('scikit-build options:')
            print('\n'.join(arg_descriptions))
            print('')
            print('Arguments following a "--" are passed directly to CMake '
                  '(e.g. -DMY_VAR:BOOL=TRUE).')
            print('Arguments following a second "--" are passed directly to '
                  ' the build tool.')
            print('')
        return upstream_setup(*args, **kw)

    developer_mode = "develop" in commands

    packages = kw.get('packages', [])
    package_dir = kw.get('package_dir', {})
    package_data = kw.get('package_data', {}).copy()

    py_modules = kw.get('py_modules', [])
    new_py_modules = {py_module: False for py_module in py_modules}

    scripts = kw.get('scripts', [])
    new_scripts = {script: False for script in scripts}

    data_files = {
        (parent_dir or '.'): set(file_list)
        for parent_dir, file_list in kw.get('data_files', [])
    }

    # Since CMake arguments provided through the command line have more
    # weight and when CMake is given multiple times a argument, only the last
    # one is considered, let's prepend the one provided in the setup call.
    cmake_args = skbuild_kw['cmake_args'] + cmake_args

    try:
        cmkr = cmaker.CMaker()
        env = cmkr.configure(cmake_args,
                             cmake_source_dir=cmake_source_dir,
                             cmake_install_dir=skbuild_kw['cmake_install_dir'])
        cmkr.make(make_args, env=env)
    except SKBuildGeneratorNotFoundError as ex:
        sys.exit(ex)
    except SKBuildError as ex:
        import traceback
        print("Traceback (most recent call last):")
        traceback.print_tb(sys.exc_info()[2])
        print('')
        sys.exit(ex)

    # If needed, set reasonable defaults for package_dir
    for package in packages:
        if package not in package_dir:
            package_dir[package] = package.replace(".", os.path.sep)

    package_prefixes = _collect_package_prefixes(package_dir, packages)

    _classify_files(cmkr.install(), package_data, package_prefixes,
                    py_modules, new_py_modules,
                    scripts, new_scripts,
                    data_files,
                    cmake_source_dir, skbuild_kw['cmake_install_dir'])

    if developer_mode:
        for package, package_file_list in package_data.items():
            for package_file in package_file_list:
                package_file = os.path.join(package_dir[package], package_file)
                cmake_file = os.path.join(CMAKE_INSTALL_DIR, package_file)
                if os.path.exists(cmake_file):
                    _copy_file(cmake_file, package_file, hide_listing)
    else:
        _consolidate(cmake_source_dir,
                     packages, package_dir, py_modules, package_data,
                     hide_listing)

    kw['package_data'] = package_data
    kw['package_dir'] = {
        package: (
            os.path.join(CMAKE_INSTALL_DIR, prefix)
            if os.path.exists(os.path.join(CMAKE_INSTALL_DIR, prefix))
            else prefix)
        for prefix, package in package_prefixes
    }

    kw['py_modules'] = [
        os.path.join(CMAKE_INSTALL_DIR, py_module) if mask else py_module
        for py_module, mask in new_py_modules.items()
    ]

    kw['scripts'] = [
        os.path.join(CMAKE_INSTALL_DIR, script) if mask else script
        for script, mask in new_scripts.items()
    ]

    kw['data_files'] = [
        (parent_dir, list(file_set))
        for parent_dir, file_set in data_files.items()
    ]

    # Adapted from espdev/ITKPythonInstaller/setup.py.in
    # pylint: disable=missing-docstring
    class BinaryDistribution(upstream_Distribution):
        def has_ext_modules(self):  # pylint: disable=no-self-use
            return has_cmakelists
    kw['distclass'] = BinaryDistribution

    print("")

    return upstream_setup(*args, **kw)


def _collect_package_prefixes(package_dir, packages):
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
    return list(sorted(
        (
            (package_dir[package].replace('.', '/'), package)
            for package in packages
        ),
        key=lambda tup: len(tup[0]),
        reverse=True
    ))


# pylint:disable=too-many-arguments, too-many-branches
def _classify_files(install_paths, package_data, package_prefixes,
                    py_modules, new_py_modules,
                    scripts, new_scripts,
                    data_files,
                    cmake_source_dir, cmake_install_dir):
    assert not os.path.isabs(cmake_source_dir)
    assert cmake_source_dir != "."

    cmake_source_dir = to_unix_path(cmake_source_dir)

    install_root = os.path.join(os.getcwd(), CMAKE_INSTALL_DIR)
    for path in install_paths:
        found_package = False
        found_module = False
        found_script = False

        # if this installed file is not within the project root, complain and
        # exit
        if not to_platform_path(path).startswith(CMAKE_INSTALL_DIR):
            raise SKBuildError((
                "\n  CMake-installed files must be within the project root.\n"
                "    Project Root  : {}\n"
                "    Violating File: {}\n").format(
                    install_root, to_platform_path(path)))

        # peel off the 'skbuild' prefix
        path = to_unix_path(os.path.relpath(path, CMAKE_INSTALL_DIR))

        # If the CMake project lives in a sub-directory (e.g src), its
        # include rules are relative to it. If the project is not already
        # installed in a directory, we need to prepend
        # the source directory so that the remaining of the logic
        # can successfully check if the path belongs to a package or
        # if it is a module.
        # TODO(jc) Instead of blindly checking if cmake_install_dir is set
        #          or not, a more elaborated check should be done.
        if (not cmake_install_dir
                and cmake_source_dir
                and not path.startswith(cmake_source_dir)):
            path = to_unix_path(os.path.join(cmake_source_dir, path))

        # check to see if path is part of a package
        for prefix, package in package_prefixes:
            if path.startswith(prefix):
                # peel off the package prefix
                path = os.path.relpath(path, prefix)

                package_file_list = package_data.get(package, [])
                package_file_list.append(path)
                package_data[package] = package_file_list

                found_package = True
                break

        if found_package:
            continue
        # If control reaches this point, then this installed file is not part of
        # a package.

        # check if path is a module
        for module in py_modules:
            if path.replace("/", ".") == ".".join((module, "py")):
                new_py_modules[module] = True
                found_module = True
                break

        if found_module:
            continue
        # If control reaches this point, then this installed file is not a
        # module

        # if the file is a script, mark the corresponding script
        for script in scripts:
            if path == script:
                new_scripts[script] = True
                found_script = True
                break

        if found_script:
            continue
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
        file_set.add(os.path.join(CMAKE_INSTALL_DIR, path))
        del parent_dir, file_set


def _copy_file(src_file, dest_file, hide_listing=True):
    """Copy ``src_file`` to ``dest_file`` ensuring parent directory exists.

    By default, message like `creating directory /path/to/package` and
    `copying directory /src/path/to/package -> path/to/package` are displayed
    on standard output. Setting ``hide_listing`` to False avoids message from
    being displayed.
    """
    # Create directory if needed
    dest_dir = os.path.dirname(dest_file)
    if not os.path.exists(dest_dir):
        if not hide_listing:
            print("creating directory {}".format(dest_dir))
        mkdir_p(dest_dir)

    # Copy file
    if not hide_listing:
        print("copying {} -> {}".format(src_file, dest_file))
    copyfile(src_file, dest_file)
    copymode(src_file, dest_file)


def _consolidate(
        cmake_source_dir, packages, package_dir, py_modules, package_data,
        hide_listing
):
    """This function consolidates packages having modules located in
    both the source tree and the CMake install tree into one location.

    The one location is the CMake install tree
    (see data::`.constants.CMAKE_INSTALL_DIR`).

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
    into the data::`.constants.CMAKE_INSTALL_DIR` and added to the
    ``package_data`` dictionary so that it can be considered by
    the upstream setup function.
    """

    try:
        # Search for python modules in both the current directory
        # and cmake install tree.
        modules = PythonModuleFinder(
            packages, package_dir, py_modules,
            alternative_build_base=CMAKE_INSTALL_DIR
        ).find_all_modules()
    except DistutilsError as msg:
        raise SystemExit("error: {}".format(str(msg)))

    print("")

    for entry in modules:

        # Check if module file should be copied into the CMake install tree.
        if _package_data_contain_module(entry, package_data):
            continue

        (package, _, src_module_file) = entry

        # Copy missing module file
        dest_module_file = os.path.join(CMAKE_INSTALL_DIR, src_module_file)
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
