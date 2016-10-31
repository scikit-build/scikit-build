"""This module defines custom implementation of ``build_py`` setuptools
command."""

from setuptools.command.build_py import build_py as _build_py

from . import set_build_base_mixin
from ..utils import new_style

from distutils import log as distutils_log


class build_py(set_build_base_mixin, new_style(_build_py)):
    """Custom implementation of ``install_data`` setuptools command."""

    def initialize_options(self):
        super(build_py, self).initialize_options()
        self.outfiles_count = 0

    def build_module(self, module, module_file, package):
        super(build_py, self).build_module(module, module_file, package)
        self.outfiles_count += 1

    def hide_listing(self):
        return (hasattr(self.distribution, "hide_listing")
                and self.distribution.hide_listing)

    def run(self, *args, **kwargs):
        """Handle --hide-listing option."""
        old_threshold = distutils_log._global_log.threshold
        if self.hide_listing():
            distutils_log.set_verbosity(0)
        super(build_py, self).run(*args, **kwargs)
        distutils_log.set_verbosity(old_threshold)
        distutils_log.info("copied %d files" % self.outfiles_count)
