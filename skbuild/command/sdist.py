"""This module defines custom implementation of ``sdist`` setuptools command."""

import os

from distutils.command.sdist import sdist as _sdist

from . import set_build_base_mixin
from ..utils import new_style

from distutils import log as disutils_log


class sdist(set_build_base_mixin, new_style(_sdist)):
    """Custom implementation of ``sdist`` setuptools command."""

    user_options = _sdist.user_options + [
        ('hide-listing', None,
         "do not display list of files being included in the distribution"),
    ]

    boolean_options = _sdist.boolean_options + ['hide-listing']

    def initialize_options(self):
        super(sdist, self).initialize_options()
        self.hide_listing = 0

    def make_release_tree(self, base_dir, files):
        old_threshold = disutils_log._global_log.threshold
        if self.hide_listing:
            disutils_log.set_verbosity(0)
        super(sdist, self).make_release_tree(base_dir, files)
        what = "copied"
        if hasattr(os, 'link'):
            what = "hard-linked"
        disutils_log.set_verbosity(old_threshold)
        disutils_log.info("%s %d files" % (what, len(files)))

    def run(self, *args, **kwargs):
        """Force :class:`.egg_info.egg_info` command to run."""
        self.run_command('generate_source_manifest')
        super(sdist, self).run(*args, **kwargs)
