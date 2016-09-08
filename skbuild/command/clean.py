
import os

try:
    from setuptools.command.clean import clean as _clean
except ImportError:
    from distutils.command.clean import clean as _clean

from shutil import rmtree

from distutils import log

from . import new_style, set_build_base_mixin
from .. import cmaker


class clean(set_build_base_mixin, new_style(_clean)):
    def run(self):
        super(clean, self).run()
        for dir_ in (cmaker.CMAKE_INSTALL_DIR,
                     cmaker.CMAKE_BUILD_DIR,
                     cmaker.SKBUILD_DIR):
            if os.path.exists(dir_):
                log.info("removing '%s'", dir_)
            if not self.dry_run and os.path.exists(dir_):
                rmtree(dir_)
