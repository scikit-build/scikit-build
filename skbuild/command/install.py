
try:
    from setuptools.command.install import install as _install
except ImportError:
    from distutils.command.install import install as _install

from .. import cmaker


class install(_install):
    def finalize_options(self):
        try:
            if not self.build_base or self.build_base == 'build':
                self.build_base = cmaker.SETUPTOOLS_INSTALL_DIR
        except AttributeError:
            pass
        _install.finalize_options(self)
