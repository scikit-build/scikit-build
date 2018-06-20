"""This module defines custom implementation of ``install_scripts`` setuptools
command."""

from distutils import log as distutils_log

from setuptools.command.install_scripts import (
    install_scripts as _install_scripts)

from . import set_build_base_mixin
from ..utils import distribution_hide_listing, new_style


class install_scripts(set_build_base_mixin, new_style(_install_scripts)):
    """Custom implementation of ``install_scripts`` setuptools command."""

    def run(self, *args, **kwargs):
        """Handle --hide-listing option."""
        with distribution_hide_listing(self.distribution):
            super(install_scripts, self).run(*args, **kwargs)
        distutils_log.info("copied %d files" % len(self.outfiles))
