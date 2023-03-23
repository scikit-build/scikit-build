"""This module defines custom implementation of ``install_lib`` setuptools
command."""

from __future__ import annotations

from setuptools.command.install_lib import install_lib as _install_lib

from ..utils import distribution_hide_listing, logger
from . import CommandMixinProtocol, set_build_base_mixin


class install_lib(set_build_base_mixin, _install_lib):
    """Custom implementation of ``install_lib`` setuptools command."""

    def install(self: CommandMixinProtocol) -> list[str]:
        """Handle --hide-listing option."""
        with distribution_hide_listing(self.distribution):
            outfiles: list[str] = super().install()  # type: ignore[misc]
        if outfiles is not None:
            logger.info("copied %d files", len(outfiles))
        return outfiles
