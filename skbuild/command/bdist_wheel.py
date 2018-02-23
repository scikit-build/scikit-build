"""This module defines custom implementation of ``bdist_wheel`` setuptools
command."""

import sys

from wheel import archive as _wheel_archive
from wheel.bdist_wheel import bdist_wheel as _bdist_wheel

from . import set_build_base_mixin
from ..utils import distribution_hide_listing, new_style


class bdist_wheel(set_build_base_mixin, new_style(_bdist_wheel)):
    """Custom implementation of ``bdist_wheel`` setuptools command."""

    def run(self, *args, **kwargs):
        """Handle --hide-listing option."""

        old_make_wheelfile_inner = _wheel_archive.make_wheelfile_inner

        def _make_wheelfile_inner(base_name, base_dir='.'):
            with distribution_hide_listing(self.distribution) as hide_listing:
                if hide_listing:
                    zip_filename = base_name + ".whl"
                    print("creating '%s' and adding '%s' to it"
                          % (zip_filename, base_dir))
                old_make_wheelfile_inner(base_name, base_dir)

        _wheel_archive.make_wheelfile_inner = _make_wheelfile_inner

        try:
            super(bdist_wheel, self).run(*args, **kwargs)
        finally:
            _wheel_archive.make_wheelfile_inner = old_make_wheelfile_inner

    def finalize_options(self, *args, **kwargs):
        """Ensure MacOSX wheels include ``x86_64`` instead of ``intel``."""
        # pylint:disable=attribute-defined-outside-init,access-member-before-definition
        if sys.platform == 'darwin' and self.plat_name is None and self.distribution.has_ext_modules():
            # The following code is duplicated in setuptools_wrap
            # pylint:disable=access-member-before-definition
            self.plat_name = "macosx-10.6-x86_64"
        super(bdist_wheel, self).finalize_options(*args, **kwargs)

    def write_wheelfile(self, wheelfile_base, _=None):
        """Write ``skbuild <version>`` as a wheel generator.
        See `PEP-0427 <https://www.python.org/dev/peps/pep-0427/#file-contents>`_ for more details.
        """
        from .. import __version__ as skbuild_version
        generator = "skbuild %s" % skbuild_version
        super(bdist_wheel, self).write_wheelfile(wheelfile_base, generator)
