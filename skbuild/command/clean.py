"""This module defines custom implementation of ``clean`` setuptools command."""

import os

try:
    from setuptools.command.clean import clean as _clean
except ImportError:
    from distutils.command.clean import clean as _clean

from shutil import rmtree

from ..constants import CMAKE_BUILD_DIR, CMAKE_INSTALL_DIR, SKBUILD_DIR
from ..utils import distutils_log, new_style
from . import set_build_base_mixin


class clean(set_build_base_mixin, new_style(_clean)):
    """Custom implementation of ``clean`` setuptools command."""

    def run(self):
        """After calling the super class implementation, this function removes
        the directories specific to scikit-build."""
        super(clean, self).run()
        for dir_ in (CMAKE_INSTALL_DIR(), CMAKE_BUILD_DIR(), SKBUILD_DIR()):
            if os.path.exists(dir_):
                distutils_log.info("removing '%s'", dir_)
            if not self.dry_run and os.path.exists(dir_):
                rmtree(dir_)
