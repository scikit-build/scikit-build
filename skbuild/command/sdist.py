"""This module defines custom implementation of ``sdist`` setuptools command."""

import os

from distutils.command.sdist import sdist as _sdist

from . import set_build_base_mixin
from ..utils import new_style

from distutils import log as distutils_log


class sdist(set_build_base_mixin, new_style(_sdist)):
    """Custom implementation of ``sdist`` setuptools command."""

    def hide_listing(self):
        return (hasattr(self.distribution, "hide_listing")
                and self.distribution.hide_listing)

    def make_release_tree(self, base_dir, files):
        old_threshold = distutils_log._global_log.threshold
        if self.hide_listing():
            distutils_log.set_verbosity(0)
        super(sdist, self).make_release_tree(base_dir, files)
        what = "copied"
        if hasattr(os, 'link'):
            what = "hard-linked"
        distutils_log.set_verbosity(old_threshold)
        distutils_log.info("%s %d files" % (what, len(files)))

    def run(self, *args, **kwargs):
        """Force :class:`.egg_info.egg_info` command to run."""
        self.run_command('generate_source_manifest')
        super(sdist, self).run(*args, **kwargs)
