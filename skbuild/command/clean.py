
import os

try:
    from setuptools.command.clean import clean as _clean
except ImportError:
    from distutils.command.clean import clean as _clean

from shutil import rmtree

from distutils import log

from . import set_build_base_mixin
from ..constants import (CMAKE_BUILD_DIR,
                         CMAKE_INSTALL_DIR,
                         SKBUILD_DIR)
from ..utils import new_style


class clean(set_build_base_mixin, new_style(_clean)):
    def run(self):
        super(clean, self).run()
        for dir_ in (CMAKE_INSTALL_DIR,
                     CMAKE_BUILD_DIR,
                     SKBUILD_DIR):
            if os.path.exists(dir_):
                log.info("removing '%s'", dir_)
            if not self.dry_run and os.path.exists(dir_):
                rmtree(dir_)
