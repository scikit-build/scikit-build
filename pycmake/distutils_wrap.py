"""This module provides functionality for wrapping key components of the
distutils infrastructure.
"""
import os
import sys
import argparse
import distutils.core

from pycmake import cmaker


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
    cmkr = cmaker.CMaker()
    cmkr.configure(cmake_args)
    cmkr.make(make_args)
    extra_data_files = cmkr.install()
    data_files = kw.get('package_data', {})
    base_path_files = data_files.get("", [])
    base_path_files.extend(extra_data_files)
    data_files[""] = base_path_files
    kw['package_data'] = data_files
    return distutils.core.setup(*args, **kw)
