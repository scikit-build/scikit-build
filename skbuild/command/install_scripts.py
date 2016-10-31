"""This module defines custom implementation of ``install_scripts`` setuptools
command."""

from setuptools.command.install_scripts import (
    install_scripts as _install_scripts)

from . import set_build_base_mixin
from ..utils import new_style

from distutils import log as disutils_log


class install_scripts(set_build_base_mixin, new_style(_install_scripts)):
    """Custom implementation of ``install_data`` setuptools command."""

    user_options = _install_scripts.user_options + [
        ('hide-listing', None,
         "do not display list of files being included in the distribution"),
    ]

    boolean_options = _install_scripts.boolean_options + ['hide-listing']

    def initialize_options(self):
        super(install_scripts, self).initialize_options()
        self.hide_listing = 0

    def run(self, *args, **kwargs):
        """Handle --hide-listing option."""
        old_threshold = disutils_log._global_log.threshold
        if self.hide_listing:
            disutils_log.set_verbosity(0)
        super(install_scripts, self).run(*args, **kwargs)
        disutils_log.set_verbosity(old_threshold)
        disutils_log.info("copied %d files" % len(self.outfiles))
