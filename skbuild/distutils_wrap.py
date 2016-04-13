"""This module provides functionality for wrapping key components of the
distutils infrastructure.
"""
import os
import sys
import argparse
import distutils.core

from . import cmaker


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
        if concatenate_value:
            newarg += "=" + str(f(value))
        b.append(newarg)
        if value is not None:
            b.append(f(value))
    return a, b


def parse_args():
    dutils = []
    cmake = []
    make = []
    argsets = [dutils, cmake, make]
    i = 0
    for arg in sys.argv:
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

    for path in cmkr.install():
        for prefix, package in package_prefixes:
            # peel off the 'skbuild' prefix
            path = os.path.relpath(path, cmaker.PACKAGE_BUILD_DIR)

            if path.startswith(prefix):
                # peel off the package prefix
                path = os.path.relpath(path, prefix)

                package_file_list = package_data.get(package, [])
                package_file_list.append(path)
                package_data[package] = package_file_list
                break

            # NOTE(opadron): If control reaches this point, then we have
            # installed files for which there are no specified packages.  Not
            # sure what to do about them.  For now, they are silently dropped,
            # just like with distutils.

    kw['package_data'] = package_data
    kw['package_dir'] = {
        package: os.path.join(cmaker.PACKAGE_BUILD_DIR, prefix)
        for prefix, package in package_prefixes
    }

    return distutils.core.setup(*args, **kw)
