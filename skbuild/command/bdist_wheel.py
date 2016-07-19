
from wheel.bdist_wheel import bdist_wheel as _bdist_wheel

class bdist_wheel(_bdist_wheel):
    def finalize_options(self):
        try:
            if not self.build_base or self.build_base == 'build':
                self.build_base = cmaker.DISTUTILS_INSTALL_DIR
        except AttributeError:
            pass
        _bdist_wheel.finalize_options(self)

