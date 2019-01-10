"""This module defines custom implementation of ``build_ext`` setuptools command."""

import os

from distutils.file_util import copy_file

try:
    from setuptools.command.build_ext import build_ext as _build_ext
except ImportError:
    from distutils.command.build_ext import build_ext as _build_ext

from . import set_build_base_mixin
from ..constants import CMAKE_INSTALL_DIR
from ..utils import new_style


class build_ext(set_build_base_mixin, new_style(_build_ext)):
    """Custom implementation of ``build_ext`` setuptools command."""

    def copy_extensions_to_source(self):
        """This function is only-called when doing inplace build.

        It is customized to ensure the extensions compiled using distutils
        are copied back to the source tree instead of the :func:`skbuild.constants.CMAKE_INSTALL_DIR()`.
        """
        build_py = self.get_finalized_command('build_py')
        for ext in self.extensions:
            fullname = self.get_ext_fullname(ext.name)
            filename = self.get_ext_filename(fullname)
            modpath = fullname.split('.')
            package = '.'.join(modpath[:-1])
            package_dir = build_py.get_package_dir(package)
            # skbuild: strip install dir for inplace build
            package_dir = package_dir[len(CMAKE_INSTALL_DIR()) + 1:]
            dest_filename = os.path.join(package_dir,
                                         os.path.basename(filename))
            src_filename = os.path.join(self.build_lib, filename)

            # Always copy, even if source is older than destination, to ensure
            # that the right extensions for the current Python/platform are
            # used.
            copy_file(
                src_filename, dest_filename, verbose=self.verbose,
                dry_run=self.dry_run
            )
            if ext._needs_stub:
                self.write_stub(package_dir or os.curdir, ext, True)
