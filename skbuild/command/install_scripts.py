"""This module defines custom implementation of ``install_scripts`` setuptools
command."""

from __future__ import annotations

from typing import Any

from setuptools.command.install_scripts import install_scripts as _install_scripts

from ..utils import distribution_hide_listing, logger
from . import CommandMixinProtocol, set_build_base_mixin


class install_scripts(set_build_base_mixin, _install_scripts):
    """Custom implementation of ``install_scripts`` setuptools command."""

    def run(self: CommandMixinProtocol, *args: Any, **kwargs: Any) -> None:
        """Handle --hide-listing option."""
        with distribution_hide_listing(self.distribution):
            super().run(*args, **kwargs)  # type: ignore[misc]
        logger.info("copied %d files", len(self.outfiles))
