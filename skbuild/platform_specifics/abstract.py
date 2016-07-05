
import os
import shutil
import subprocess

test_folder = "cmake_test_compile"
list_file = "CMakeLists.txt"
cache_file = "CMakeCache.txt"


class CMakePlatform(object):

    def __init__(self):
        self.default_generators = list()

    @staticmethod
    def write_test_cmakelist(languages):
        if not os.path.exists(test_folder):
            os.makedirs(test_folder)
        with open("{:s}/{:s}".format(test_folder, list_file), "w") as f:
            f.write("cmake_minimum_required(VERSION 2.8)\n")
            f.write("PROJECT(compiler_test NONE)\n")
            for language in languages:
                f.write("ENABLE_LANGUAGE({:s})\n".format(language))

    @staticmethod
    def cleanup_test():
        if os.path.exists(test_folder):
            shutil.rmtree(test_folder)

    def get_cmake_exe_path(self):
        """Override this method with additional logic where necessary if CMake is not on PATH.
        """
        return "cmake"

    # TODO: this method name is not great.  Does anyone have a better idea for
    # renaming it?
    def get_best_generator(
            self, generator=None, languages=("CXX", "C"), cleanup=True):
        """Loop over generators to find one that works.

        Parameters:
        generator: string or None
            If provided, uses only provided generator, instead of trying system defaults.
        languages: tuple
            the languages you'll need for your project, in terms that CMake recognizes.
        cleanup: bool
            If True, cleans up temporary folder used to test generators.  Set to False
            for debugging to see CMake's output files.
        """

        candidate_generators = self.default_generators

        if generator is not None:
            candidate_generators = [generator]

        cmake_exe_path = self.get_cmake_exe_path()

        self.write_test_cmakelist(languages)

        # back up current folder so we go back to it when done testing
        backup_folder = os.getcwd()

        # cd into the cmake_test_compile folder as working dir (rmtree this later for cleanliness)
        # TODO: make this more robust in terms of checking where we are, if the
        # folder exists, etc.
        os.chdir(test_folder)

        # working generator is the first generator we find that works.
        working_generator = None

        # initial status is failure.  If subprocess call of cmake succeeds, it
        # gets set to 0.
        status = -1

        for generator in candidate_generators:
            # clear the cache for each attempted generator type
            if os.path.exists(cache_file):
                os.remove(cache_file)
            try:
                # call cmake to see if the compiler specified by this generator
                # works for the specified languages
                cmake_execution_string = '{:s} ./ -G "{:s}"'.format(
                    cmake_exe_path, generator)
                status = subprocess.call(cmake_execution_string, shell=True)
            except OSError as e:
                # ignore errors from the OS - just don't report success for
                # this generator.
                print(
                    "Error encountered when attempting to use generator {:s}:".format(generator))
                print(e)
            # cmake succeeded, this generator should work
            if status == 0:
                # we have a working generator, don't bother looking for more
                working_generator = generator
                break

        os.chdir(backup_folder)

        if cleanup:
            CMakePlatform.cleanup_test()

        return working_generator

