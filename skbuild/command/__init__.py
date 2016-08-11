
from .. import cmaker


class set_build_base_mixin(object):
    def finalize_options(self, *args, **kwargs):
        try:
            if not self.build_base or self.build_base == 'build':
                self.build_base = cmaker.SETUPTOOLS_INSTALL_DIR
        except AttributeError:
            pass

        super(set_build_base_mixin, self).finalize_options(*args, **kwargs)


# distutils/setuptools command classes are old-style classes, which won't work
# with mixins.  To work around this limitation, we dynamically convert them to
# new style classes by creating a new class that inherits from them and also
# <object>.  This ensures that <object> is always at the end of the MRO, even
# after being mixed in with other classes.

def new_style(klass):
    return type("NewStyleClass<{}>".format(klass.__name__), (klass, object), {})
