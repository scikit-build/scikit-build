import argparse
import itertools
import os
import os.path
import platform
import re
import subprocess
import shlex
import sys
import sysconfig

from .platform_specifics import get_platform
from .exceptions import SKBuildError

SKBUILD_DIR = "_skbuild"
CMAKE_BUILD_DIR = os.path.join(SKBUILD_DIR, "cmake-build")
CMAKE_INSTALL_DIR = os.path.join(SKBUILD_DIR, "cmake-install")
DISTUTILS_INSTALL_DIR = os.path.join(SKBUILD_DIR, "distutils")

RE_FILE_INSTALL = re.compile(
    r"""[ \t]*file\(INSTALL DESTINATION "([^"]+)".*"([^"]+)"\).*""")

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
    cwd = os.getcwd()

    result = path.replace("/", os.sep)
    if result.startswith(cwd):
        result = os.path.relpath(result, cwd)

    if platform.system() == "Windows":
        result = result.replace("\\\\", os.sep)

    result = result.replace("\n", "")

    return result

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

        self.platform = get_platform()

    def configure(self, clargs=(), generator_id=None):
        """Calls cmake to generate the makefile (or VS solution, or XCode project).

        Input:
        ------
        generator_id: string
            The string representing the CMake generator to use.  If None, uses defaults for your platform.
        """

        # if no provided default generator_id, check environment
        if generator_id is None:
            generator_id = os.environ.get("CMAKE_GENERATOR")

        # if generator_id is provided on command line, use it
        clargs, cli_generator_id = pop_arg('-G', clargs)
        if cli_generator_id is not None:
            generator_id = cli_generator_id

        # use the generator_id returned from the platform, with the current
        # generator_id as a suggestion
        generator_id = self.platform.get_best_generator(generator_id)

        if generator_id is None:
            sys.exit("Could not get working generator for your system."
                     "  Aborting build.")

        if not os.path.exists(CMAKE_BUILD_DIR):
            os.makedirs(CMAKE_BUILD_DIR)

        if not os.path.exists(CMAKE_INSTALL_DIR):
            os.makedirs(CMAKE_INSTALL_DIR)

        if not os.path.exists(DISTUTILS_INSTALL_DIR):
            os.makedirs(DISTUTILS_INSTALL_DIR)

        python_version = sysconfig.get_config_var('VERSION')

        if not python_version:
            python_version = sysconfig.get_config_var('py_version_short')

        if not python_version:
            python_version = ".".join(map(str, sys.version_info[:2]))

        # determine python include dir
        python_include_dir = sysconfig.get_config_var('INCLUDEPY')

        # if Python.h not found (or python_include_dir is None), try to find a
        # suitable include dir
        if (python_include_dir is None or
            not os.path.exists(os.path.join(python_include_dir, 'Python.h'))):
            candidate_prefixes = []

            try:
                candidate_prefixes.append(
                    os.path.dirname(sysconfig.get_config_var('INCLUDEPY')))
            except:
                pass

            try:
                candidate_prefixes.append(
                    sysconfig.get_config_var('INCLUDEDIR'))
            except:
                pass

            try:
                candidate_prefixes.append(
                    os.path.dirname(sysconfig.get_path('include')))
            except:
                pass

            try:
                candidate_prefixes.append(
                    os.path.dirname(sysconfig.get_path('platinclude')))
            except:
                pass

            try:
                candidate_prefixes.append(
                    os.path.join(sysconfig.get_python_inc(),
                                 ".".join(map(str, sys.version_info[:2]))))
            except:
                pass

            try:
                candidate_prefixes.append(sysconfig.get_python_inc())
            except:
                pass

            candidate_prefixes = tuple(filter(bool, candidate_prefixes))

            candidate_versions = (python_version,)
            if python_version:
                candidate_versions += ('',)

            candidates = (
                os.path.join(prefix, ''.join(('python', ver)))
                for (prefix, ver) in itertools.product(
                    candidate_prefixes,
                    candidate_versions
                )
            )

            for candidate in candidates:
                if os.path.exists(os.path.join(candidate, 'Python.h')):
                    # we found an include directory
                    python_include_dir = candidate
                    break

        # TODO(opadron): what happens if we don't find an include directory?

        # determine direct path to libpython
        python_library = sysconfig.get_config_var('LIBRARY')

        # if static (or nonexistent), try to find a suitable dynamic libpython
        if (python_library is None or
            os.path.splitext(python_library)[1][-2:] == '.a'):

            candidate_lib_prefixes = ['', 'lib']

            candidate_extensions = ['.lib', '.so', '.a']
            if sysconfig.get_config_var('WITH_DYLD'):
                candidate_extensions.insert(0, '.dylib')

            candidate_versions = [python_version]
            if python_version:
                candidate_versions.append('')
                candidate_versions.insert(
                    0, "".join(python_version.split(".")[:2]))

            abiflags = getattr(sys, 'abiflags', '')
            candidate_abiflags = [abiflags]
            if abiflags:
                candidate_abiflags.append('')

            libdir = sysconfig.get_config_var('LIBDIR')
            if sysconfig.get_config_var('MULTIARCH'):
                masd = sysconfig.get_config_var('multiarchsubdir')
                if masd:
                    if masd.startswith(os.sep):
                        masd = masd[len(os.sep):]
                    libdir = os.path.join(libdir, masd)

            if libdir is None:
                libdir = os.path.abspath(os.path.join(
                        sysconfig.get_config_var('LIBDEST'), "..", "libs"))

            candidates = (
                os.path.join(
                    libdir,
                    ''.join((pre, 'python', ver, abi, ext))
                )
                for (pre, ext, ver, abi) in itertools.product(
                    candidate_lib_prefixes,
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

        # TODO(opadron): what happens if we don't find a libpython?

        cmd = ['cmake', os.getcwd(), '-G', generator_id,
               '-DCMAKE_INSTALL_PREFIX={0}'.format(
                    os.path.join(os.getcwd(), CMAKE_INSTALL_DIR)),
               '-DPYTHON_EXECUTABLE=' + sys.executable,
               '-DPYTHON_VERSION_STRING=' + sys.version.split(' ')[0],
               '-DPYTHON_INCLUDE_DIR=' + python_include_dir,
               '-DPYTHON_LIBRARY=' + python_library,
               '-DSKBUILD:BOOL=TRUE',
               ]

        cmd.extend(clargs)

        cmd.extend(
            filter(bool,
                   shlex.split(os.environ.get("SKBUILD_CONFIGURE_OPTIONS", "")))
        )

        # changes dir to cmake_build and calls cmake's configure step
        # to generate makefile
        rtn = subprocess.check_call(cmd, cwd=CMAKE_BUILD_DIR)
        if rtn != 0:
            raise RuntimeError("Could not successfully configure your project. "
                               "Please see CMake's output for more information.")

        # Try to catch files that are meant to be installed outside the project
        # root before they are actually installed.  We can not wait for the
        # manifest, so we try to extract the information from the CMake build
        # files.
        bad_installs = []
        install_dir = os.path.join(os.getcwd(), CMAKE_INSTALL_DIR)

        for root, dir_list, file_list in os.walk(CMAKE_BUILD_DIR):
            for filename in file_list:
                if os.path.splitext(filename)[1] != ".cmake":
                    continue

                for line in open(os.path.join(root, filename)):
                    match = RE_FILE_INSTALL.match(line)
                    if match is None:
                        continue

                    destination = os.path.normpath(
                        match.group(1).replace("${CMAKE_INSTALL_PREFIX}",
                                               install_dir))

                    if not destination.startswith(install_dir):
                        bad_installs.append(
                            os.path.join(
                                destination,
                                os.path.basename(match.group(2))
                            )
                        )

        if bad_installs:
            raise SKBuildError("\n".join((
                "",
                "  CMake-installed files must be within the project root.",
                "    Project Root:",
                "      " + install_dir,
                "    Violating Files:",
                "\n".join(
                    ("      " + _install) for _install in bad_installs)
            )))


    def make(self, clargs=(), config="Release", source_dir="."):
        """Calls the system-specific make program to compile code.
        """
        clargs, config = pop_arg('--config', clargs, config)
        if not os.path.exists(CMAKE_BUILD_DIR):
            raise RuntimeError(("CMake build folder ({}) does not exist. "
                                "Did you forget to run configure before "
                                "make?").format(CMAKE_BUILD_DIR))

        cmd = ["cmake", "--build", source_dir,
               "--target", "install", "--config", config]
        cmd.extend(clargs)
        cmd.extend(
            filter(bool,
                   shlex.split(os.environ.get("SKBUILD_BUILD_OPTIONS", "")))
        )

        rtn = subprocess.check_call(cmd, cwd=CMAKE_BUILD_DIR)
        return rtn

    def install(self):
        """Returns a list of tuples of (install location, file list) to install
        via distutils that is compatible with the data_files keyword argument.
        """
        return self._parse_manifest()

    def _parse_manifest(self):
        installed_files = {}
        install_manifest_path = os.path.join(CMAKE_BUILD_DIR,
                                             "install_manifest.txt")
        with open(install_manifest_path, "r") as manifest:
            return [_remove_cwd_prefix(path) for path in manifest]

        return []

