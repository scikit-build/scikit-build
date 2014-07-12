__author__ = 'Michael'

import os
import shutil
import subprocess

class CMakePlatform(object):
    def __init__(self):
        self.default_generators = list()

    @staticmethod
    def write_test_cmakelist(languages):
        if not os.path.exists("cmake_test_compile"):
            os.makedirs("cmake_test_compile")
        with open("cmake_test_compile/CMakeLists.txt", "w") as f:
            f.write("cmake_minimum_required(VERSION 2.8)\n")
            f.write("PROJECT(compiler_test NONE)\n")
            for language in languages:
                f.write("ENABLE_LANGUAGE({:s})\n".format(language))

    @staticmethod
    def cleanup_test():
        shutil.rmtree('cmake_test_compile')

    def get_best_generator(self, generator=None, languages=["CXX", "C"]):
        """
        Loop over generators to find one that works

        Languages is a list of all the languages you'll need for your project.
        """
        if generator is not None:
            generators = [generator, ]
        else:
            generators = self.default_generators

        self.write_test_cmakelist(languages)

        # back up the current path
        backup_path = os.getcwd()
        # cd into the cmake_test_compile folder as working dir (rmtree this later for cleanliness)
        # TODO: make this more robust in terms of checking where we are, if the folder exists, etc.
        os.chdir("cmake_test_compile")

        # working generator is the first generator we find that works.
        working_generator = None
        for generator in generators:
            # clear the cache for each attempted generator type
            if os.path.exists("CMakeCache.txt"):
                os.remove("CMakeCache.txt")
            # call cmake to see if the compiler specified by this generator works for the specified languages
            status = subprocess.call('cmake ./ -G "{:s}"'.format(generator))
            # cmake succeeded, this generator should work
            if status == 0:
                # we have a working generator, don't bother looking for more
                working_generator = generator
                break

        os.chdir(backup_path)
        return working_generator

