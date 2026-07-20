"""
Compatibility shim for ``skbuild.utils``.

scikit-build 1.0 builds on scikit-build-core and no longer ships these path and
directory helpers. Nothing is exported. The module exists only so a bare
``import skbuild.utils`` still succeeds; any attribute access raises
:class:`AttributeError`. Use scikit-build-core APIs, or ``pathlib``/``os`` for
the path helpers.
"""

from __future__ import annotations

import warnings

__all__: list[str] = []

warnings.warn(
    "skbuild.utils is a compatibility shim for scikit-build <1.0; it exposes nothing. Port to scikit-build-core APIs.",
    DeprecationWarning,
    stacklevel=2,
)


def __getattr__(name: str) -> object:
    msg = (
        f"skbuild.utils.{name} is not available in scikit-build >=1.0. "
        "Use scikit-build-core APIs, or pathlib/os for the path helpers."
    )
    raise AttributeError(msg)
