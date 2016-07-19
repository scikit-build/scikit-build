
try:
    from setuptools.command.clean import clean as _clean
except ImportError:
    from distutils.command.clean import clean as _clean

from shutil import rmtree

from distutils import log

from .. import cmaker


class clean(_clean):
    def finalize_options(self):
        try:
            if not self.build_base or self.build_base == 'build':
                self.build_base = cmaker.SETUPTOOLS_INSTALL_DIR
        except AttributeError:
            pass

        _clean.finalize_options(self)

    def run(self):
        _clean.run(self)
        for dir_ in (cmaker.CMAKE_INSTALL_DIR,
                     cmaker.CMAKE_BUILD_DIR,
                     cmaker.SKBUILD_DIR):
            log.info("removing '%s'", dir_)
            if not self.dry_run:
                rmtree(dir_)
