"""This module defines custom implementation of ``sdist`` setuptools command."""

from typing import Optional, Sequence

from setuptools.command.sdist import sdist as _sdist

from ..utils import distribution_hide_listing, logger
from . import CommandMixinProtocol, set_build_base_mixin


class sdist(set_build_base_mixin, _sdist):
    """Custom implementation of ``sdist`` setuptools command."""

    def make_release_tree(self: CommandMixinProtocol, base_dir: str, files: Sequence[str]) -> None:
        """Handle --hide-listing option."""
        with distribution_hide_listing(self.distribution):
            super().make_release_tree(base_dir, files)  # type: ignore[misc]
        logger.info("copied %d files", len(files))

    def make_archive(
        self,
        base_name: str,
        _format: str,
        root_dir: Optional[str] = None,
        base_dir: Optional[str] = None,
        owner: Optional[str] = None,
        group: Optional[str] = None,
    ) -> str:
        """Handle --hide-listing option."""
        logger.info("creating '%s' %s archive and adding '%s' to it", base_name, _format, base_dir)
        with distribution_hide_listing(self.distribution):  # type: ignore[attr-defined]
            return super().make_archive(base_name, _format, root_dir, base_dir, owner, group)

    def run(self, *args: object, **kwargs: object) -> None:
        """Force :class:`.egg_info.egg_info` command to run."""
        self.run_command("generate_source_manifest")
        super().run(*args, **kwargs)
