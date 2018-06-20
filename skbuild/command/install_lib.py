"""This module defines custom implementation of ``install_lib`` setuptools
command."""

from distutils import log as distutils_log

from setuptools.command.install_lib import install_lib as _install_lib

from . import set_build_base_mixin
from ..utils import distribution_hide_listing, new_style


class install_lib(set_build_base_mixin, new_style(_install_lib)):
    """Custom implementation of ``install_lib`` setuptools command."""

    def install(self):
        """Handle --hide-listing option."""
        with distribution_hide_listing(self.distribution):
            outfiles = super(install_lib, self).install()
        if outfiles is not None:
            distutils_log.info("copied %d files" % len(outfiles))
