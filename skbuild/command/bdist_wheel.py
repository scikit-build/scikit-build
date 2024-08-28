"""This module defines custom implementation of ``bdist_wheel`` setuptools
command."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wheel.bdist_wheel import bdist_wheel as _bdist_wheel
    from wheel.wheelfile import WheelFile
else:
    try:
        from setuptools.command.bdist_wheel import WheelFile  # type: ignore[attr-defined]
        from setuptools.command.bdist_wheel import bdist_wheel as _bdist_wheel
    except ImportError:
        from wheel.bdist_wheel import bdist_wheel as _bdist_wheel
        from wheel.wheelfile import WheelFile

from .._version import version as skbuild_version
from ..utils import distribution_hide_listing
from . import set_build_base_mixin


class bdist_wheel(set_build_base_mixin, _bdist_wheel):  # type: ignore[misc]
    """Custom implementation of ``bdist_wheel`` setuptools command."""

    def run(self, *args: object, **kwargs: object) -> None:
        """Handle --hide-listing option."""

        old_write_files = WheelFile.write_files

        def update_write_files(wheelfile_self: bdist_wheel, base_dir: str) -> None:
            with distribution_hide_listing(self.distribution) as hide_listing:
                if hide_listing:
                    zip_filename = wheelfile_self.filename
                    print(f"creating {zip_filename!r} and adding {base_dir!r} to it", flush=True)
                old_write_files(wheelfile_self, base_dir)

        WheelFile.distribution = self.distribution
        WheelFile.write_files = update_write_files

        try:
            super().run(*args, **kwargs)
        finally:
            WheelFile.write_files = old_write_files
            del WheelFile.distribution

    def write_wheelfile(self, wheelfile_base: str, _: None = None) -> None:
        """Write ``skbuild <version>`` as a wheel generator.
        See `PEP-0427 <https://www.python.org/dev/peps/pep-0427/#file-contents>`_ for more details.
        """
        generator = f"skbuild {skbuild_version}"
        super().write_wheelfile(wheelfile_base, generator)
