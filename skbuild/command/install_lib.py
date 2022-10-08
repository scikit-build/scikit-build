"""This module defines custom implementation of ``install_lib`` setuptools
command."""

from typing import List

from setuptools.command.install_lib import install_lib as _install_lib

from ..utils import distribution_hide_listing, distutils_log
from . import CommandMixinProtocol, set_build_base_mixin


class install_lib(set_build_base_mixin, _install_lib):
    """Custom implementation of ``install_lib`` setuptools command."""

    def install(self: CommandMixinProtocol) -> List[str]:
        """Handle --hide-listing option."""
        with distribution_hide_listing(self.distribution):
            outfiles: List[str] = super().install()  # type: ignore[misc]
        if outfiles is not None:
            distutils_log.info("copied %d files", len(outfiles))
        return outfiles
