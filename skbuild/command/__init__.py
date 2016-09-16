
from .. import cmaker


class set_build_base_mixin(object):
    def finalize_options(self, *args, **kwargs):
        try:
            if not self.build_base or self.build_base == 'build':
                self.build_base = cmaker.SETUPTOOLS_INSTALL_DIR
        except AttributeError:
            pass

        super(set_build_base_mixin, self).finalize_options(*args, **kwargs)
