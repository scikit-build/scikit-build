"""This module defines custom implementation of ``sdist`` setuptools command."""

import contextlib
import os

from distutils import log as distutils_log
from distutils.command.sdist import sdist as _sdist

from . import set_build_base_mixin
from ..utils import distribution_hide_listing, new_style


class sdist(set_build_base_mixin, new_style(_sdist)):
    """Custom implementation of ``sdist`` setuptools command."""

    def make_distribution(self):
        """This function was originally re-implemented in setuptools to workaround
        https://github.com/pypa/setuptools/issues/516 and later ported to scikit-build
        to ensure symlinks are maintained.
        """
        with self._remove_os_link():
            super(sdist, self).make_distribution()

    @staticmethod
    @contextlib.contextmanager
    def _remove_os_link():
        """In a context, remove and restore ``os.link`` if it exists.
        """
        # copied from setuptools.sdist

        class NoValue:
            pass

        orig_val = getattr(os, 'link', NoValue)
        try:
            del os.link
        except Exception:
            pass
        try:
            yield
        finally:
            if orig_val is not NoValue:
                setattr(os, 'link', orig_val)

    def make_release_tree(self, base_dir, files):
        """Handle --hide-listing option."""
        with distribution_hide_listing(self.distribution):
            super(sdist, self).make_release_tree(base_dir, files)
        distutils_log.info("copied %d files" % len(files))

    # pylint:disable=too-many-arguments, unused-argument
    def make_archive(self, base_name, _format, root_dir=None, base_dir=None,
                     owner=None, group=None):
        """Handle --hide-listing option."""
        distutils_log.info("creating '%s' %s archive and adding '%s' to it",
                           base_name, _format, base_dir)
        with distribution_hide_listing(self.distribution):
            super(sdist, self).make_archive(
                base_name, _format, root_dir, base_dir)

    def run(self, *args, **kwargs):
        """Force :class:`.egg_info.egg_info` command to run."""
        self.run_command('generate_source_manifest')
        super(sdist, self).run(*args, **kwargs)
