"""This module defines custom implementation of ``clean`` setuptools command."""

from __future__ import annotations

import os
from shutil import rmtree

import setuptools  # noqa: F401
from distutils.command.clean import clean as _clean

from ..constants import CMAKE_BUILD_DIR, CMAKE_INSTALL_DIR, SKBUILD_DIR
from ..utils import logger
from . import set_build_base_mixin


class clean(set_build_base_mixin, _clean):
    """Custom implementation of ``clean`` setuptools command."""

    def run(self) -> None:
        """After calling the super class implementation, this function removes
        the directories specific to scikit-build."""
        super().run()
        for dir_ in (CMAKE_INSTALL_DIR(), CMAKE_BUILD_DIR(), SKBUILD_DIR()):
            if os.path.exists(dir_):
                logger.info("removing '%s'", dir_)
            # This seems to be there but isn't typed in the stubs TODO
            if not self.dry_run and os.path.exists(dir_):  # type: ignore[attr-defined]
                rmtree(dir_)
