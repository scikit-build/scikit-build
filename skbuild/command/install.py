"""This module defines custom implementation of ``install`` setuptools
command."""

from setuptools.command.install import install as _install

from . import set_build_base_mixin


class install(set_build_base_mixin, _install):
    """Custom implementation of ``install`` setuptools command."""

    def finalize_options(self, *args, **kwargs):
        """Ensure that if the distribution is non-pure, all modules
        are installed in ``self.install_platlib``.

        .. note:: `setuptools.dist.Distribution.has_ext_modules()`
           is overridden in :func:`..setuptools_wrap.setup()`.
        """
        if self.install_lib is None and self.distribution.has_ext_modules():
            # pylint:disable=attribute-defined-outside-init
            self.install_lib = self.install_platlib

        super().finalize_options(*args, **kwargs)
