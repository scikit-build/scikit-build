
try:
    from setuptools.command.build import build as _build
except ImportError:
    from distutils.command.build import build as _build

from .. import cmaker


class build(_build):
    def finalize_options(self):
        try:
            if not self.build_base or self.build_base == 'build':
                self.build_base = cmaker.SETUPTOOLS_INSTALL_DIR
        except AttributeError:
            pass
        _build.finalize_options(self)
