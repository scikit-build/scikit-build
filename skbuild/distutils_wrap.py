"""This module provides functionality for wrapping key components of the
distutils infrastructure.
"""
import os
import sys
import site
import argparse
import distutils.core

import itertools as it

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

    py_modules = kw.get('py_modules', [])
    new_py_modules = { module: False for module in py_modules }

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

    # try to deduce the path for installed python packages relative to the
    # search prefix.  NOTE(opadron): My google-fu has failed to find any better
    # ways of doing this:
    relative_site_packages_dir = None
    candidate_dirs = it.chain(site.getsitepackages(),
                              (site.getusersitepackages,))
    for candidate_dir in candidate_dirs:
        candidate = os.path.relpath(candidate_dir, sys.prefix)
        if not candidate.startswith('..'):
            relative_site_packages_dir = candidate
            break

    for path in cmkr.install():
        found_package = False
        found_module = False
        found_script = False

        # peel off the 'skbuild' prefix
        path = os.path.relpath(path, cmaker.CMAKE_INSTALL_DIR)

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

        # if the file is a module, mark the corresponding module
        for module in py_modules:
            if path.replace("/", ".")  == ".".join((module, "py")):
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
        parent_dir = os.path.join(relative_site_packages_dir,
                                  os.path.dirname(path))
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

    kw['py_modules'] = [
        module if mask else module for module, mask in new_py_modules.items()
    ]

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
    from distutils.command import build, install, clean
    class new_build(build.build):
        def finalize_options(self):
            if not self.build_base or self.build_base == 'build':
                self.build_base = cmaker.DISTUTILS_INSTALL_DIR
            build.build.finalize_options(self)

    class new_install(install.install):
        def finalize_options(self):
            if not self.build_base or self.build_base == 'build':
                self.build_base = cmaker.DISTUTILS_INSTALL_DIR
            install.install.finalize_options(self)

    class new_clean(clean.clean):
        def finalize_options(self):
            if not self.build_base or self.build_base == 'build':
                self.build_base = cmaker.DISTUTILS_INSTALL_DIR
            clean.clean.finalize_options(self)

        # NOTE(opadron): Even if we didn't have a bug that we needed to work
        # around, we still want to add extra logic to this "clean" command that
        # will remove the _skbuild directory.
        def run(self):
            clean.clean.run(self)
            from distutils import log
            if not self.dry_run:
                from shutil import rmtree
                for dir_ in (cmaker.CMAKE_INSTALL_DIR,
                            cmaker.CMAKE_BUILD_DIR,
                            cmaker.SKBUILD_DIR):
                    log.info("removing '%s'", dir_)
                    rmtree(dir_)

    cmdclass = kw.get('cmdclass', {})
    cmdclass['build'] = cmdclass.get('build', new_build)
    cmdclass['install'] = cmdclass.get('install', new_install)
    cmdclass['clean'] = cmdclass.get('clean', new_clean)
    kw['cmdclass'] = cmdclass

    return distutils.core.setup(*args, **kw)
