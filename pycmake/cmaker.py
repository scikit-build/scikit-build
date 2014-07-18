import os
import platform
import subprocess

from pycmake import platform_specifics


class CMaker(object):

    def __init__(self, generator=None, **defines):
        self.generator = generator or platform_specifics.get_platform()
        if platform.system() != 'Windows':
            rtn = subprocess.call(['which', 'cmake'])
            if rtn != 0:
                sys.exit('CMake is not installed, aborting build.')

    def configure(self, clargs=(), generator=None):
        """
        Calls cmake to generate the makefile (or VS solution, or XCode project)

        Input:
        ------
        generator: string
            The string representing the CMake generator to use.  If None, uses defaults for your platform.
        """
        generator_id = self.generator.get_best_generator(generator)
        if not os.path.exists("cmake_build"):
            os.makedirs("cmake_build")
        os.chdir("cmake_build")
        return_status = subprocess.check_call(['cmake', '../', '-G', generator_id, "-DCMAKE_PREFIX_INSTALL=."])
        os.chdir("..")
        if return_status != 0:
            raise RuntimeError(
                "Could not successfully configure your project.  Please see CMake's output for more information.")

    def make(self, clargs=(), config="Release", source_dir="./"):
        """
        Calls the system-specific make program to compile code
        """
        if not os.path.exists("cmake_build"):
            raise RuntimeError(
                "CMake build folder (cmake_build) does not exist.  Did you forget to run configure before make?")
        os.chdir("cmake_build")
        return_status = subprocess.check_call(["cmake", "--build", source_dir, "--target", "install", "--config", config])
        os.chdir("..")
        return return_status

    def install(self):
        """Returns a list of tuples of (install location, file list) to install
        via distutils that is compatible with the data_files keyword argument.
        """
        return []


if __name__ == "__main__":
    maker = CMaker()
    #os.chdir("tests")
    maker.configure("Visual Studio 11")
