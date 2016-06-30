
from distutils.command.build import build as _build

from .. import cmaker

class build(_build):
    def finalize_options(self):
        if not self.build_base or self.build_base == 'build':
            self.build_base = cmaker.DISTUTILS_INSTALL_DIR
        _build.finalize_options(self)

