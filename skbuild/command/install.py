
from distutils.command.install import install as _install

from .. import cmaker

class install(_install):
    def finalize_options(self):
        if not self.build_base or self.build_base == 'build':
            self.build_base = cmaker.DISTUTILS_INSTALL_DIR
        _install.finalize_options(self)

