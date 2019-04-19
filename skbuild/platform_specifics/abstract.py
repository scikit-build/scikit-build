"""This module defines objects useful to discover which CMake generator is
supported on the current platform."""

from __future__ import print_function

import os
import shutil
import subprocess
import textwrap

from ..constants import CMAKE_DEFAULT_EXECUTABLE
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
        raise NotImplementedError  # pragma: no cover

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

    def get_generator(self, generator_name):
        """Loop over generators and return the first that matches the given
        name.
        """
        for default_generator in self.default_generators:
            if default_generator.name == generator_name:
                return default_generator

        return CMakeGenerator(generator_name)

    # TODO: this method name is not great.  Does anyone have a better idea for
    # renaming it?
    def get_best_generator(
            self, generator_name=None, skip_generator_test=False,
            languages=("CXX", "C"), cleanup=True,
            cmake_executable=CMAKE_DEFAULT_EXECUTABLE, cmake_args=()):
        """Loop over generators to find one that works by configuring
        and compiling a test project.

        :param generator_name: If provided, uses only provided generator, \
        instead of trying :attr:`default_generators`.
        :type generator_name: string or None

        :param skip_generator_test: If set to True and if a generator name is \
        specified, the generator test is skipped. If no generator_name is specified \
        and the option is set to True, the first available generator is used.
        :type skip_generator_test: bool

        :param languages: The languages you'll need for your project, in terms \
        that CMake recognizes.
        :type languages: tuple

        :param cleanup: If True, cleans up temporary folder used to test \
        generators. Set to False for debugging to see CMake's output files.
        :type cleanup: bool

        :param cmake_executable: Path to CMake executable used to configure \
        and build the test project used to evaluate if a generator is working.
        :type cmake_executable: string

        :param cmake_args: List of CMake arguments to use when configuring \
        the test project. Only arguments starting with ``-DCMAKE_`` are \
        used.
        :type cmake_args: tuple

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
            candidate_generators = []
            for default_generator in self.default_generators:
                if default_generator.name == generator_name:
                    candidate_generators.append(default_generator)
            if not candidate_generators:
                candidate_generators = [CMakeGenerator(generator_name)]

        self.write_test_cmakelist(languages)

        if skip_generator_test:
            working_generator = candidate_generators[0]
        else:
            working_generator = self.compile_test_cmakelist(
                cmake_executable, candidate_generators, cmake_args)

        if working_generator is None:
            raise SKBuildGeneratorNotFoundError(textwrap.dedent(
                """
                {line}
                scikit-build could not get a working generator for your system. Aborting build.

                {installation_help}

                {line}
                """).strip().format(  # noqa: E501
                    line="*"*80,
                    installation_help=self.generator_installation_help)
            )

        if cleanup:
            CMakePlatform.cleanup_test()

        return working_generator

    @staticmethod
    @push_dir(directory=test_folder)
    def compile_test_cmakelist(
            cmake_exe_path, candidate_generators, cmake_args=()):
        """Attempt to configure the test project with
        each :class:`CMakeGenerator` from ``candidate_generators``.

        Only cmake arguments starting with ``-DCMAKE_`` are used to configure
        the test project.

        The function returns the first generator allowing to successfully
        configure the test project using ``cmake_exe_path``."""
        # working generator is the first generator we find that works.
        working_generator = None

        # Include only -DCMAKE_* arguments
        cmake_args = [arg for arg in cmake_args if arg.startswith("-DCMAKE_")]

        # Do not complain about unused CMake arguments
        cmake_args.insert(0, "--no-warn-unused-cli")

        def _generator_discovery_status_msg(_generator, suffix=""):
            outer = "-" * 80
            inner = ["-" * ((idx * 5) - 3) for idx in range(1, 8)]
            print(outer if suffix == "" else "\n".join(inner))
            print("-- Trying \"%s\" generator%s" % (_generator.description, suffix))
            print(outer if suffix != "" else "\n".join(inner[::-1]))

        for generator in candidate_generators:
            print("\n")
            _generator_discovery_status_msg(generator)

            # clear the cache for each attempted generator type
            if os.path.isdir('build'):
                shutil.rmtree('build')

            with push_dir('build', make_directory=True):
                # call cmake to see if the compiler specified by this
                # generator works for the specified languages
                if generator.toolset:
                    toolset_arg = ['-T', generator.toolset]
                else:
                    toolset_arg = []

                cmd = [cmake_exe_path, '../', '-G', generator.name]
                cmd.extend(toolset_arg)
                cmd.extend(cmake_args)

                status = subprocess.call(cmd, env=generator.env)

            _generator_discovery_status_msg(
                generator, " - %s" % ("success" if status == 0 else "failure"))
            print("")

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

    def __init__(self, name, env=None, toolset=None):
        """Instantiate a generator object with the given ``name``.

        By default, ``os.environ`` is associated with the generator. Dictionary
        passed as ``env`` parameter will be merged with ``os.environ``. If an
        environment variable is set in both ``os.environ`` and ``env``, the
        variable in ``env`` is used.

        Some CMake generators support a ``toolset`` specification to tell the native
        build system how to choose a compiler.
        """
        self._generator_name = name
        self.env = dict(
            list(os.environ.items()) + list(env.items() if env else []))
        self._generator_toolset = toolset
        if toolset is None:
            self._description = name
        else:
            self._description = "%s %s" % (name, toolset)

    @property
    def name(self):
        """Name of CMake generator."""
        return self._generator_name

    @property
    def toolset(self):
        """Toolset specification associated with the CMake generator."""
        return self._generator_toolset

    @property
    def description(self):
        """Name of CMake generator with properties describing the environment (e.g toolset)"""
        return self._description
