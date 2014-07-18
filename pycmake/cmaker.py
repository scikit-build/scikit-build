import os
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
    val = ns[0][1] if len(ns) > 0 else None
    return a, val

class CMaker(object):

    def __init__(self, generator=None, **defines):
        self.generator = generator or platform_specifics.get_platform()
        if platform.system() != 'Windows':
            rtn = subprocess.call(['which', 'cmake'])
            if rtn != 0:
                sys.exit('CMake is not installed, aborting build.')

    def configure(self, clargs=()):
        """Calls cmake to generate the makefile (or VS solution, or XCode project).
        """
        clargs, generator_id = pop_arg('-G', clargs, 
                                       self.generator.get_best_generator(generator))
        if not os.path.exists("cmake_build"):
            os.makedirs("cmake_build")
        cmd = 'cmake ../ -G "{0:s}" -DCMAKE_PREFIX_INSTALL=. {1}'
        cmd = cmd.format(generator_id, " ".join(clargs))
        rtn = subprocess.call(cmd, shell=True, cwd="cmake_build")
        if rtn != 0:
            raise RuntimeError("Could not successfully configure your project. "
                               "Please see CMake's output for more information.")

    def make(self, clargs=()):
        """Calls the system-specific make program to compile code
        """
        clargs, config = pop_arg('-G', clargs, "Release")
        if not os.path.exists("cmake_build"):
            raise RuntimeError("CMake build folder (cmake_build) does not exist. "
                               "Did you forget to run configure before make?")
        cmd = "cmake --build ./ --target install --config {0:s} {1}"
        cmd = cmd.format(config, " ".join(clargs))
        rtn = subprocess.call(cmd, shell=True, cwd="cmake_build")
        return rtn 

    def install(self):
        """Returns a list of tuples of (install location, file list) to install
        via distutils that is compatible with the data_files keyword argument.
        """
        return []


if __name__ == "__main__":
    maker = CMaker()
    os.chdir("tests")
    maker.configure("Visual Studio 11")
