import argparse
import itertools
import os
import os.path
import platform
import subprocess
import sys
import sysconfig

from .platform_specifics import get_platform


def pop_arg(arg, a, default=None):
    """Pops an arg(ument) from an argument list a and returns the new list
    and the value of the argument if present and a default otherwise.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(arg)
    ns, a = parser.parse_known_args(a)
    ns = tuple(vars(ns).items())
    if len(ns) > 0 and ns[0][1] is not None:
        val = ns[0][1]
    else:
        val = default
    return a, val


def _remove_cwd_prefix(path):
    base_path = os.getcwd()
    if platform.system() == "Windows":
        base_path = base_path.replace("\\\\", "/")
    common_prefix = os.path.commonprefix([base_path, path])
    # strip off the base path - keep only the relative path
    relpath = path.replace(common_prefix, "")
    # get rid of a leading slash
    path = relpath[1:]
    # trim newline characters (sometimes at end of filename)
    path = path.replace("\n", "")
    return path


def _touch_init(folder):
    init = os.path.join(folder, "__init__.py")
    if not os.path.exists(init):
        with open(init, "w") as f:
            f.write("\n")
    return _remove_cwd_prefix(init)


class CMaker(object):

    def __init__(self, **defines):
        if platform.system() != 'Windows':
            rtn = subprocess.call(['which', 'cmake'])
            if rtn != 0:
                sys.exit('CMake is not installed, aborting build.')

    def configure(self, clargs=(), generator_id=None):
        """Calls cmake to generate the makefile (or VS solution, or XCode project).

        Input:
        ------
        generator_id: string
            The string representing the CMake generator to use.  If None, uses defaults for your platform.
        """

        clargs, generator_id = pop_arg('-G', clargs)
        generator_id = get_platform().get_best_generator(
            generator_id)
        if generator_id is None:
            sys.exit("Could not get working generator for your system."
                     "  Aborting build.")

        if not os.path.exists("cmake_build"):
            os.makedirs("cmake_build")

        # determine python include dir
        python_include_dir = (sysconfig.get_path('include') or
                              sysconfig.get_path('platinclude'))

        # determine direct path to libpython
        python_library = sysconfig.get_config_var('LIBRARY')

        # if static, try to find a suitable dynamic libpython
        if os.path.splitext(python_library)[1][-2:] == '.a':
            candidate_extensions = ('.so', '.a')
            if sysconfig.get_config_var('WITH_DYLD'):
                candidate_extensions = ('.dylib',) + candidate_extensions

            python_version = sysconfig.get_config_var('VERSION')
            candidate_versions = (python_version,)
            if python_version:
                candidate_versions += ('',)

            abiflags = getattr(sys, 'abiflags', '')
            candidate_abiflags = (abiflags,)
            if abiflags:
                candidate_abiflags += ('',)

            libdir = sysconfig.get_config_var('LIBDIR')
            candidates = (
                os.path.join(
                    libdir,
                    ''.join(('libpython', ver, abi, ext))
                )
                for (ext, ver, abi) in itertools.product(
                    candidate_extensions,
                    candidate_versions,
                    candidate_abiflags
                )
            )

            for candidate in candidates:
                if os.path.exists(candidate):
                    # we found a (likely alternate) libpython
                    python_library = candidate
                    break

        cmd = ['cmake', '..', '-G', generator_id,
               '-DCMAKE_INSTALL_PREFIX={0}'.format(os.getcwd()),
               '-DPYTHON_EXECUTABLE=' + sys.executable,
               '-DPYTHON_VERSION_STRING=' + sys.version.split(' ')[0],
               '-DPYTHON_INCLUDE_DIR=' + python_include_dir,
               '-DPYTHON_LIBRARY=' + python_library,
               ]

        cmd.extend(clargs)
        # changes dir to cmake_build and calls cmake's configure step
        # to generate makefile
        rtn = subprocess.check_call(cmd, cwd="cmake_build")
        if rtn != 0:
            raise RuntimeError("Could not successfully configure your project. "
                               "Please see CMake's output for more information.")

    def make(self, clargs=(), config="Release", source_dir="."):
        """Calls the system-specific make program to compile code.
        """
        clargs, config = pop_arg('--config', clargs, config)
        if not os.path.exists("cmake_build"):
            raise RuntimeError("CMake build folder (cmake_build) does not exist. "
                               "Did you forget to run configure before make?")
        cmd = ["cmake", "--build", source_dir,
               "--target", "install", "--config", config]
        cmd.extend(clargs)
        rtn = subprocess.check_call(cmd, cwd="cmake_build")
        return rtn

    def install(self):
        """Returns a list of tuples of (install location, file list) to install
        via distutils that is compatible with the data_files keyword argument.
        """
        return self._parse_manifest()

    def _parse_manifest(self):
        installed_files = {}
        with open("cmake_build/install_manifest.txt", "r") as manifest:
            for path in manifest.readlines():
                cleaned_relative_path = _remove_cwd_prefix(path)
                package, relative_path = cleaned_relative_path.split(os.sep, 1)
                path_set = installed_files.get(package, set())
                path_set.add(relative_path)
                installed_files[package] = path_set

        return { k: list(v) for k,v in installed_files.items() }
