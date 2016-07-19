
try:
    from setuptools.command.bdist import bdist as _bdist
except ImportError:
    from distutils.command.bdist import bdist as _bdist

class bdist(_bdist):
    def finalize_options(self):
        try:
            if not self.build_base or self.build_base == 'build':
                self.build_base = cmaker.DISTUTILS_INSTALL_DIR
        except AttributeError:
            pass
        _bdist.finalize_options(self)

