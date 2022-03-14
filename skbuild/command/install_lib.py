"""This module defines custom implementation of ``install_lib`` setuptools
command."""

from setuptools.command.install_lib import install_lib as _install_lib

from ..utils import distribution_hide_listing, distutils_log, new_style
from . import set_build_base_mixin


class install_lib(set_build_base_mixin, new_style(_install_lib)):
    """Custom implementation of ``install_lib`` setuptools command."""

    def install(self):
        """Handle --hide-listing option."""
        with distribution_hide_listing(self.distribution):
            outfiles = super(install_lib, self).install()
        if outfiles is not None:
            distutils_log.info("copied %d files", len(outfiles))
        return outfiles
