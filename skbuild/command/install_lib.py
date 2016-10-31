"""This module defines custom implementation of ``install_lib`` setuptools
command."""

from setuptools.command.install_lib import install_lib as _install_lib

from . import set_build_base_mixin
from ..utils import new_style

from distutils import log as disutils_log


class install_lib(set_build_base_mixin, new_style(_install_lib)):
    """Custom implementation of ``install_data`` setuptools command."""

    user_options = _install_lib.user_options + [
        ('hide-listing', None,
         "do not display list of files being included in the distribution"),
    ]

    boolean_options = _install_lib.boolean_options + ['hide-listing']

    def initialize_options(self):
        super(install_lib, self).initialize_options()
        self.hide_listing = 0

    def install(self):
        old_threshold = disutils_log._global_log.threshold
        if self.hide_listing:
            disutils_log.set_verbosity(0)
        outfiles = super(install_lib, self).install()
        disutils_log.set_verbosity(old_threshold)
        if outfiles is not None:
            disutils_log.info("copied %d files" % len(outfiles))

    def run(self, *args, **kwargs):
        """Handle --hide-listing option."""
        old_threshold = disutils_log._global_log.threshold
        if self.hide_listing:
            disutils_log.set_verbosity(0)
        super(install_lib, self).run(*args, **kwargs)
        disutils_log.set_verbosity(old_threshold)
