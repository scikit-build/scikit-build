"""Collection of objects allowing to customize behavior of standard
distutils and setuptools commands.
"""

from .. import cmaker


class set_build_base_mixin:
    """Mixin allowing to override distutils and setuptools commands."""

    def finalize_options(self, *args, **kwargs):
        """Override built-in function and set a new `build_base`."""
        try:
            if not self.build_base or self.build_base == "build":
                self.build_base = cmaker.SETUPTOOLS_INSTALL_DIR()
        except AttributeError:
            pass

        super().finalize_options(*args, **kwargs)
