import os
import sys
import platform
import subprocess
import argparse

from pycmake import platform_specifics


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
        """
        # TODO: needs to parse languages somehow? or does it matter? it would
        #    be an additional arg to the get_best_generator function.
        clargs, generator_id = pop_arg('-G', clargs)
        generator_id = platform_specifics.get_platform().get_best_generator(
            generator_id)
        if generator_id is None:
            sys.exit("Could not get working generator for your system."
                     "  Aborting build.")
        if not os.path.exists("cmake_build"):
            os.makedirs("cmake_build")
        cmd = ['cmake', '..',  '-G', generator_id,
               '-DCMAKE_INSTALL_PREFIX={0}'.format(os.getcwd())]
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
        installed_files = list()
        with open("cmake_build/install_manifest.txt", "r") as manifest:
            for path in manifest.readlines():
                # do we have an __init__.py file in the folder?
                # if not, we should create one so that distutils can find files
                # there.
                init_path = _touch_init(os.path.split(path)[0])
                cleaned_relative_path = _remove_cwd_prefix(path)
                # distutils likes only the filename - gets confused by relative
                # path???
                installed_files.append(os.path.split(cleaned_relative_path)[1])
        return installed_files
