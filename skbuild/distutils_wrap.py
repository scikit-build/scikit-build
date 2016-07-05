"""This module provides functionality for wrapping key components of the
distutils infrastructure.
"""
import os
import os.path
import sys
import argparse
import distutils.core

from . import cmaker
from .command import build, install, clean
from .exceptions import SKBuildError

def move_arg(arg, a, b, newarg=None, f=lambda x: x, concatenate_value=False):
    """Moves an argument from a list to b list, possibly giving it a new name
    and/or performing a transformation on the value. Returns a and b. The arg need
    not be present in a.
    """
    newarg = newarg or arg
    parser = argparse.ArgumentParser()
    parser.add_argument(arg)
    ns, a = parser.parse_known_args(a)
    ns = tuple(vars(ns).items())
    if len(ns) > 0 and ns[0][1] is not None:
        key, value = ns[0]
        newargs = [newarg, value]
        if concatenate_value:
            b.append("=".join(newargs))
        elif value is not None:
            b.extend(newargs)
    return a, b


def parse_args():
    dutils = []
    cmake = []
    make = []
    argsets = [dutils, cmake, make]
    i = 0

    argv = list(sys.argv)
    try:
        argv.index("--build-type")
    except ValueError:
        argv.append("--build-type")
        argv.append("Release")

    for arg in argv:
        if arg == '--':
            i += 1
        else:
            argsets[i].append(arg)

    # handle argument transformations
    dutils, cmake = move_arg('--build-type', dutils, cmake,
                             newarg='-DCMAKE_BUILD_TYPE',
                             concatenate_value=True)
    dutils, cmake = move_arg('-G', dutils, cmake)
    dutils, make = move_arg('-j', dutils, make)
    op = os.path
    absappend = lambda x: op.join(op.dirname(op.abspath(sys.argv[0])), x)
    dutils, dutils = move_arg('--egg-base', dutils, dutils, f=absappend)

    return dutils, cmake, make


def setup(*args, **kw):
    """This function wraps distutils.core.setup() so that we can run cmake, make,
    CMake build, then proceed as usual with a distutils, appending the
    CMake-generated output as necessary.
    """
    sys.argv, cmake_args, make_args = parse_args()

    packages = kw.get('packages', [])
    package_dir = kw.get('package_dir', {})
    package_data = kw.get('package_data', {}).copy()

    py_modules = kw.get('py_modules', [])

    scripts = kw.get('scripts', [])
    new_scripts = { script: False for script in scripts }

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

    cmkr = cmaker.CMaker()
    cmkr.configure(cmake_args)
    cmkr.make(make_args)

    install_root = os.path.join(os.getcwd(), cmaker.CMAKE_INSTALL_DIR)
    for path in cmkr.install():
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
    kw['cmdclass'] = cmdclass

    return distutils.core.setup(*args, **kw)

