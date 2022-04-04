"""This module defines custom implementation of ``bdist_wheel`` setuptools
command."""

try:
    from wheel.wheelfile import WheelFile

    _USE_WHEELFILE = True
except ImportError:
    from wheel import archive as _wheel_archive  # Not available with wheel >= 0.32.0

    _USE_WHEELFILE = False

from wheel.bdist_wheel import bdist_wheel as _bdist_wheel

from .. import __version__ as skbuild_version
from ..utils import distribution_hide_listing
from . import set_build_base_mixin


class bdist_wheel(set_build_base_mixin, _bdist_wheel):
    """Custom implementation of ``bdist_wheel`` setuptools command."""

    def run(self, *args, **kwargs):
        """Handle --hide-listing option."""

        if _USE_WHEELFILE:
            old_write_files = WheelFile.write_files

            def update_write_files(wheelfile_self, base_dir):
                with distribution_hide_listing(self.distribution) as hide_listing:
                    if hide_listing:
                        zip_filename = wheelfile_self.filename
                        print(f"creating '{zip_filename}' and adding '{base_dir}' to it")
                    old_write_files(wheelfile_self, base_dir)

            WheelFile.distribution = self.distribution
            WheelFile.write_files = update_write_files

            try:
                super().run(*args, **kwargs)
            finally:
                WheelFile.write_files = old_write_files
                del WheelFile.distribution
        else:
            # pylint: disable-next=used-before-assignment
            old_make_wheelfile_inner = _wheel_archive.make_wheelfile_inner

            def _make_wheelfile_inner(base_name, base_dir="."):
                with distribution_hide_listing(self.distribution) as hide_listing:
                    if hide_listing:
                        zip_filename = base_name + ".whl"
                        print(f"creating '{zip_filename}' and adding '{base_dir}' to it")
                    old_make_wheelfile_inner(base_name, base_dir)

            _wheel_archive.make_wheelfile_inner = _make_wheelfile_inner

            try:
                super().run(*args, **kwargs)
            finally:
                _wheel_archive.make_wheelfile_inner = old_make_wheelfile_inner

    def write_wheelfile(self, wheelfile_base, _=None):
        """Write ``skbuild <version>`` as a wheel generator.
        See `PEP-0427 <https://www.python.org/dev/peps/pep-0427/#file-contents>`_ for more details.
        """
        generator = f"skbuild {skbuild_version}"
        super().write_wheelfile(wheelfile_base, generator)
