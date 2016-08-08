"""This module provides functionality for wrapping key infrastructure components
from distutils and setuptools.
"""

import os
import os.path
import sys
import argparse

from . import cmaker
from .command import build, install, clean, bdist, bdist_wheel, egg_info
from .exceptions import SKBuildError

try:
    from setuptools import setup as upstream_setup
except ImportError:
    from distutils.core import setup as upstream_setup


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


def setup(*args, **kw):
    """This function wraps setup() so that we can run cmake, make,
    CMake build, then proceed as usual with setuptools, appending the
    CMake-generated output as necessary.
    """
    sys.argv, cmake_args, make_args = parse_args()

    # Skip running CMake when user requests help
    help_parser = argparse.ArgumentParser(add_help=False)
    help_parser.add_argument('-h', '--help', action='store_true')
    help_parser.add_argument('--help-commands', action='store_true')
    ns = help_parser.parse_known_args()[0]
    if ns.help_commands:
        return upstream_setup(*args, **kw)
    if ns.help:
        # Prepend scikit-build help. Generate option descriptions using
        # argparse.
        skbuild_parser = create_skbuild_argparser()
        arg_descriptions = [line
                            for line in skbuild_parser.format_help().split('\n')
                            if line.startswith('  ')]
        print('scikit-build options:')
        print('\n'.join(arg_descriptions))
        print()
        print('Arguments following a "--" are passed directly to CMake '
              '(e.g. -DMY_VAR:BOOL=TRUE).')
        print('Arguments following a second "--" are passed directly to the '
              'build tool.')
        print()
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

    # collect the list of prefixes for all packages
    #
    # The list is used to match paths in the install manifest to packages
    # specified in the setup.py script.
    #
    # The list is sorted in decreasing order of prefix length so that paths are
    # matched with their immediate parent package, instead of any of that
    # package's ancestors.
    #
    # For example, consider the project structure below.  Assume that the
    # setup call was made with a package list featuring "top" and "top.bar", but
    # not "top.not_a_subpackage".
    #
    # top/                -> top/
    #   __init__.py       -> top/__init__.py                 (parent: top)
    #   foo.py            -> top/foo.py                      (parent: top)
    #   bar/              -> top/bar/                        (parent: top)
    #     __init__.py     -> top/bar/__init__.py             (parent: top.bar)
    #
    #   not_a_subpackage/ -> top/not_a_subpackage/           (parent: top)
    #     data_0.txt      -> top/not_a_subpackage/data_0.txt (parent: top)
    #     data_1.txt      -> top/not_a_subpackage/data_1.txt (parent: top)
    #
    # The paths in the generated install manifest are matched to packages
    # according to the parents indicated on the right.  Only packages that are
    # specified in the setup() call are considered.  Because of the sort order,
    # the data files on the bottom would have been mapped to
    # "top.not_a_subpackage" instead of "top", proper -- had such a package been
    # specified.
    package_prefixes = list(sorted(
        (
            (package_dir[package].replace('.', '/'), package)
            for package in packages
        ),
        key=lambda tup: len(tup[0]),
        reverse=True
    ))

    try:
        cmkr = cmaker.CMaker()
        cmkr.configure(cmake_args)
        cmkr.make(make_args)
    except SKBuildError as e:
        import traceback
        print("Traceback (most recent call last):")
        traceback.print_tb(sys.exc_info()[2])
        print()
        sys.exit(e)

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

    # work around https://bugs.python.org/issue1011113
    # (patches provided, but no updates since 2014)
    cmdclass = kw.get('cmdclass', {})
    cmdclass['build'] = cmdclass.get('build', build.build)
    cmdclass['install'] = cmdclass.get('install', install.install)
    cmdclass['clean'] = cmdclass.get('clean', clean.clean)
    cmdclass['bdist'] = cmdclass.get('bdist', bdist.bdist)
    cmdclass['bdist_wheel'] = cmdclass.get(
        'bdist_wheel', bdist_wheel.bdist_wheel)
    cmdclass['egg_info'] = cmdclass.get('egg_info', egg_info.egg_info)
    kw['cmdclass'] = cmdclass

    return upstream_setup(*args, **kw)


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
