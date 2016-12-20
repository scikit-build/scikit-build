"""This module defines custom implementation of ``build_py`` setuptools
command."""

from setuptools.command.build_py import build_py as _build_py

from . import set_build_base_mixin
from ..utils import distribution_hide_listing, new_style

from distutils import log as distutils_log


class build_py(set_build_base_mixin, new_style(_build_py)):
    """Custom implementation of ``install_data`` setuptools command."""

    def initialize_options(self):
        """Handle --hide-listing option.

        Initializes ``outfiles_count``.
        """
        super(build_py, self).initialize_options()
        self.outfiles_count = 0

    def build_module(self, module, module_file, package):
        """Handle --hide-listing option.

        Increments ``outfiles_count``.
        """
        super(build_py, self).build_module(module, module_file, package)
        self.outfiles_count += 1

    def run(self, *args, **kwargs):
        """Handle --hide-listing option.

        Display number of copied files. It corresponds to the value
        of ``outfiles_count``.
        """
        with distribution_hide_listing(self.distribution):
            super(build_py, self).run(*args, **kwargs)
        distutils_log.info("copied %d files" % self.outfiles_count)
