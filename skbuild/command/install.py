"""This module defines custom implementation of ``install`` setuptools
command."""

from setuptools.command.install import install as _install

from ..utils import new_style
from . import set_build_base_mixin


class install(set_build_base_mixin, new_style(_install)):
    """Custom implementation of ``install`` setuptools command."""

    def finalize_options(self, *args, **kwargs):
        """Ensure that if the distribution is non-pure, all modules
        are installed in ``self.install_platlib``.

        .. note:: `setuptools.dist.Distribution.has_ext_modules()`
           is overridden in :func:`..setuptools_wrap.setup()`.
        """
        # pylint:disable=access-member-before-definition
        if self.install_lib is None and self.distribution.has_ext_modules():
            # pylint:disable=attribute-defined-outside-init
            self.install_lib = self.install_platlib

        super(install, self).finalize_options(*args, **kwargs)
