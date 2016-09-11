"""This module provides functionality for wrapping key infrastructure components
from distutils and setuptools.
"""

import os
import os.path
import sys
import argparse

from contextlib import contextmanager
from distutils.errors import DistutilsGetoptError, DistutilsArgError

from . import cmaker
from .command import build, install, clean, bdist, bdist_wheel, egg_info, sdist
from .exceptions import SKBuildError

# XXX If 'six' becomes a dependency, use 'six.StringIO' instead.
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from setuptools import setup as upstream_setup
from setuptools.dist import Distribution as upstream_Distribution


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
    ns, remaining_args = parser.parse_known_args(args)

    # Construct CMake argument list
    cmake_args.append('-DCMAKE_BUILD_TYPE:STRING=' + ns.build_type)
    if ns.generator is not None:
        cmake_args.extend(['-G', ns.generator])

    # Construct build tool argument list
    build_tool_args.extend(['--config', ns.build_type])
    if ns.jobs is not None:
        build_tool_args.extend(['-j', str(ns.jobs)])

    return remaining_args


def parse_args():
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

    It returns a tuple (display_only, help_commands, commands) where
     - display_only is a boolean indicating if an argument like '--help',
     '--help-commands' or '--author' was passed.
     - help_commands is a boolean indicating if argument '--help-commands'
     was passed.
     - commands contains the list of commands that were passed.

    Otherwise it raises DistutilsArgError exception if there are
    any error on the command-line, and it raises DistutilsGetoptError
    if there any error in the command 'options' attribute.

    The code has been adapted from the setup() function available
    in distutils/core.py.
    """
    setup_attrs = dict(setup_attrs)

    setup_attrs['script_name'] = os.path.basename(sys.argv[0])

    dist = upstream_Distribution(setup_attrs)

    # Find and parse the config file(s): they will override options from
    # the setup script, but be overridden by the command line.
    dist.parse_config_files()

    # Parse the command line and override config files; any
    # command-line errors are the end user's fault, so turn them into
    # SystemExit to suppress tracebacks.

    with _capture_output():
        result = dist.parse_command_line()
        display_only = not result

    return display_only, dist.help_commands, dist.commands


def setup(*args, **kw):
    """This function wraps setup() so that we can run cmake, make,
    CMake build, then proceed as usual with setuptools, appending the
    CMake-generated output as necessary.
    """
    sys.argv, cmake_args, make_args = parse_args()

    # work around https://bugs.python.org/issue1011113
    # (patches provided, but no updates since 2014)
    cmdclass = kw.get('cmdclass', {})
    cmdclass['build'] = cmdclass.get('build', build.build)
    cmdclass['install'] = cmdclass.get('install', install.install)
    cmdclass['clean'] = cmdclass.get('clean', clean.clean)
    cmdclass['sdist'] = cmdclass.get('sdist', sdist.sdist)
    cmdclass['bdist'] = cmdclass.get('bdist', bdist.bdist)
    cmdclass['bdist_wheel'] = cmdclass.get(
        'bdist_wheel', bdist_wheel.bdist_wheel)
    cmdclass['egg_info'] = cmdclass.get('egg_info', egg_info.egg_info)
    kw['cmdclass'] = cmdclass

    # Skip running CMake in the following cases:
    # * no command-line arguments or invalid ones are provided
    # * "display only" argument like '--help', '--help-commands'
    #   or '--author' are provided
    display_only = has_invalid_arguments = help_commands = False
    commands = []
    try:
        (display_only, help_commands, commands) = \
            _parse_setuptools_arguments(kw)
    except (DistutilsArgError, DistutilsGetoptError):
        has_invalid_arguments = True

    has_cmakelists = os.path.exists("CMakeLists.txt")
    if not has_cmakelists:
        print('skipping skbuild (no CMakeLists.txt found)')

    skip_cmake = (display_only
                  or has_invalid_arguments
                  or 'clean' in commands
                  or 'egg_info' in commands
                  or 'sdist' in commands
                  or not has_cmakelists)
    if skip_cmake:
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

    packages = kw.get('packages', [])
    package_dir = kw.get('package_dir', {})
    package_data = kw.get('package_data', {}).copy()

    py_modules = kw.get('py_modules', [])

    scripts = kw.get('scripts', [])
    new_scripts = {script: False for script in scripts}

    data_files = {
        (parent_dir or '.'): set(file_list)
        for parent_dir, file_list in kw.get('data_files', [])
    }

    try:
        cmkr = cmaker.CMaker()
        cmkr.configure(cmake_args)
        cmkr.make(make_args)
    except SKBuildError as e:
        import traceback
        print("Traceback (most recent call last):")
        traceback.print_tb(sys.exc_info()[2])
        print('')
        sys.exit(e)

    package_prefixes = _collect_package_prefixes(package_dir, packages)

    _classify_files(cmkr.install(), package_data, package_prefixes, py_modules,
                    scripts, new_scripts, data_files)

    kw['package_data'] = package_data
    kw['package_dir'] = {
        package: os.path.join(cmaker.CMAKE_INSTALL_DIR, prefix)
        for prefix, package in package_prefixes
    }

    kw['py_modules'] = py_modules

    kw['scripts'] = [
        os.path.join(cmaker.CMAKE_INSTALL_DIR, script) if mask else script
        for script, mask in new_scripts.items()
    ]

    kw['data_files'] = [
        (parent_dir, list(file_set))
        for parent_dir, file_set in data_files.items()
    ]

    # Adapted from espdev/ITKPythonInstaller/setup.py.in
    class BinaryDistribution(upstream_Distribution):
        def has_ext_modules(self):
            return True
    kw['distclass'] = BinaryDistribution

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


def _classify_files(install_paths, package_data, package_prefixes, py_modules,
                    scripts, new_scripts, data_files):
    install_root = os.path.join(os.getcwd(), cmaker.CMAKE_INSTALL_DIR)
    for path in install_paths:
        found_package = False
        found_module = False
        found_script = False

        # if this installed file is not within the project root, complain and
        # exit
        test_path = path.replace("/", os.sep)
        if not test_path.startswith(cmaker.CMAKE_INSTALL_DIR):
            raise SKBuildError((
                "\n  CMake-installed files must be within the project root.\n"
                "    Project Root  : {}\n"
                "    Violating File: {}\n").format(install_root, test_path))

        # peel off the 'skbuild' prefix
        path = os.path.relpath(path, cmaker.CMAKE_INSTALL_DIR)

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
        file_set.add(os.path.join(cmaker.CMAKE_INSTALL_DIR, path))
        del parent_dir, file_set
