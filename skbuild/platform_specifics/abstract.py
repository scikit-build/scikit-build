"""This module defines objects useful to discover which CMake generator is
supported on the current platform."""

import os
import shutil
import subprocess

from ..exceptions import SKBuildGeneratorNotFoundError
from ..utils import push_dir

test_folder = "_cmake_test_compile"


class CMakePlatform(object):
    """This class encapsulates the logic allowing to get the identifier of a
    working CMake generator.

    Derived class should at least set :attr:`default_generators`.
    """
    def __init__(self):
        self._default_generators = list()

    @property
    def default_generators(self):
        """List of generators considered by :func:`get_best_generator()`."""
        return self._default_generators

    @default_generators.setter
    def default_generators(self, generators):
        self._default_generators = generators

    @property
    def generator_installation_help(self):
        """Return message guiding the user for installing a valid toolchain."""
        return ""

    @staticmethod
    def write_test_cmakelist(languages):
        """Write a minimal ``CMakeLists.txt`` useful to check if the
        requested ``languages`` are supported."""
        if not os.path.exists(test_folder):
            os.makedirs(test_folder)
        with open("{:s}/{:s}".format(test_folder, "CMakeLists.txt"), "w") as f:
            f.write("cmake_minimum_required(VERSION 2.8)\n")
            f.write("PROJECT(compiler_test NONE)\n")
            for language in languages:
                f.write("ENABLE_LANGUAGE({:s})\n".format(language))

    @staticmethod
    def cleanup_test():
        """Delete test project directory."""
        if os.path.exists(test_folder):
            shutil.rmtree(test_folder)

    def get_cmake_exe_path(self):
        """Override this method with additional logic where necessary
        if CMake is not on PATH.
        """
        return "cmake"

    # TODO: this method name is not great.  Does anyone have a better idea for
    # renaming it?
    def get_best_generator(
            self, generator_name=None, languages=("CXX", "C"), cleanup=True):
        """Loop over generators to find one that works.

        :param generator_name: If provided, uses only provided generator, \
        instead of trying :attr:`default_generators`.
        :type generator_name: string or None

        :param languages: The languages you'll need for your project, in terms \
        that CMake recognizes.
        :type languages: tuple

        :param cleanup: If True, cleans up temporary folder used to test \
        generators. Set to False for debugging to see CMake's output files.
        :type cleanup: bool

        :return: CMake Generator object
        :rtype: :class:`CMakeGenerator` or None

        :raises skbuild.exceptions.SKBuildGeneratorNotFoundError:
        """

        candidate_generators = []

        if generator_name is None:
            candidate_generators = self.default_generators
        else:
            # Lookup CMakeGenerator by name. Doing this allow to get a
            # generator object with its ``env`` property appropriately
            # initialized.
            for default_generator in self.default_generators:
                if default_generator.name == generator_name:
                    candidate_generators = [default_generator]
                    break
            if len(candidate_generators) == 0:
                candidate_generators = [CMakeGenerator(generator_name)]

        cmake_exe_path = self.get_cmake_exe_path()

        self.write_test_cmakelist(languages)

        working_generator = self.compile_test_cmakelist(
            cmake_exe_path, candidate_generators)

        if working_generator is None:
            raise SKBuildGeneratorNotFoundError(
                "Could not get working generator for your system."
                "  Aborting build. %s" %
                self.generator_installation_help)

        if cleanup:
            CMakePlatform.cleanup_test()

        return working_generator

    @staticmethod
    @push_dir(directory=test_folder)
    def compile_test_cmakelist(cmake_exe_path, candidate_generators):
        """
        compile_test_cmakelist(cmake_exe_path, candidate_generators)

        Attempt to configure the test project with
        each :class:`CMakeGenerator` from ``candidate_generators``.

        The function returns the first generator allowing to successfully
        configure the test project using ``cmake_exe_path``."""
        # working generator is the first generator we find that works.
        working_generator = None

        # initial status is failure.  If subprocess call of cmake succeeds, it
        # gets set to 0.
        status = -1

        for generator in candidate_generators:
            # clear the cache for each attempted generator type
            if os.path.isdir('build'):
                shutil.rmtree('build')

            with push_dir('build', make_directory=True):
                # call cmake to see if the compiler specified by this
                # generator works for the specified languages
                cmake_execution_string = '{:s} ../ -G "{:s}"'.format(
                    cmake_exe_path, generator.name)
                status = subprocess.call(
                    cmake_execution_string, shell=True, env=generator.env)

            # cmake succeeded, this generator should work
            if status == 0:
                # we have a working generator, don't bother looking for more
                working_generator = generator
                break

        return working_generator


class CMakeGenerator(object):
    """Represents a CMake generator.

    .. automethod:: __init__
    """

    def __init__(self, name, env=None):
        """Instantiate a generator object with the given ``name``.

        By default, ``os.environ`` is associated with the generator. Dictionary
        passed as ``env`` parameter will be merged with ``os.environ``. If an
        environment variable is set in both ``os.environ`` and ``env``, the
        variable in ``env`` is used.
        """
        self._generator_name = name
        self.env = dict(
            list(os.environ.items()) + list(env.items() if env else []))

    @property
    def name(self):
        """Name of CMake generator."""
        return self._generator_name

    @name.setter
    def name(self, name):
        self._generator_name = name
