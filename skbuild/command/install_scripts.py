"""This module defines custom implementation of ``install_scripts`` setuptools
command."""

from setuptools.command.install_scripts import (
    install_scripts as _install_scripts)

from . import set_build_base_mixin
from ..utils import new_style

from distutils import log as distutils_log


class install_scripts(set_build_base_mixin, new_style(_install_scripts)):
    """Custom implementation of ``install_data`` setuptools command."""

    def hide_listing(self):
        return (hasattr(self.distribution, "hide_listing")
                and self.distribution.hide_listing)

    def run(self, *args, **kwargs):
        """Handle --hide-listing option."""
        old_threshold = distutils_log._global_log.threshold
        if self.hide_listing():
            distutils_log.set_verbosity(0)
        super(install_scripts, self).run(*args, **kwargs)
        distutils_log.set_verbosity(old_threshold)
        distutils_log.info("copied %d files" % len(self.outfiles))
