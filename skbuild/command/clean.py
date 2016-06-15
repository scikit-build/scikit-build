
from shutil import rmtree

from distutils.command.clean import clean as _clean
from distutils import log

from .. import cmaker

class clean(_clean):
    def finalize_options(self):
        if not self.build_base or self.build_base == 'build':
            self.build_base = cmaker.DISTUTILS_INSTALL_DIR
        _clean.finalize_options(self)

    def run(self):
        _clean.run(self)
        for dir_ in (cmaker.CMAKE_INSTALL_DIR,
                    cmaker.CMAKE_BUILD_DIR,
                    cmaker.SKBUILD_DIR):
            log.info("removing '%s'", dir_)
            if not self.dry_run:
                rmtree(dir_)

