"""This module defines custom implementation of ``install`` setuptools
command."""

from __future__ import annotations

from typing import Any

from setuptools.command.install import install as _install

from . import CommandMixinProtocol, set_build_base_mixin


class install(set_build_base_mixin, _install):
    """Custom implementation of ``install`` setuptools command."""

    def finalize_options(self: CommandMixinProtocol, *args: Any, **kwargs: Any) -> None:
        """Ensure that if the distribution is non-pure, all modules
        are installed in ``self.install_platlib``.

        .. note:: `setuptools.dist.Distribution.has_ext_modules()`
           is overridden in :func:`..setuptools_wrap.setup()`.
        """
        if self.install_lib is None and self.distribution.has_ext_modules():  # type: ignore[attr-defined]
            # pylint:disable=attribute-defined-outside-init
            self.install_lib = self.install_platlib

        super().finalize_options(*args, **kwargs)  # type: ignore[safe-super]
