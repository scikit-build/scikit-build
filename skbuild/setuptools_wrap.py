"""
Compatibility shim for ``skbuild.setuptools_wrap``.

scikit-build 1.0 builds on scikit-build-core, which does not implement the
classic install-classification pipeline this module drove. Nothing is exported.
The module exists only so a bare ``import skbuild.setuptools_wrap`` (some
projects keep one for historical reasons) still succeeds; any attribute access
raises :class:`AttributeError`, since scikit-build-core has no equivalent hook
to monkeypatch. Port to scikit-build-core APIs.
"""

from __future__ import annotations

import warnings

__all__: list[str] = []

warnings.warn(
    "skbuild.setuptools_wrap is a compatibility shim for scikit-build <1.0; it "
    "exposes nothing. Port to scikit-build-core APIs.",
    DeprecationWarning,
    stacklevel=2,
)


def __getattr__(name: str) -> object:
    msg = (
        f"skbuild.setuptools_wrap.{name} is not available in scikit-build >=1.0. "
        "The classic install-classification pipeline it belonged to is gone, and "
        "scikit-build-core's setuptools backend has no equivalent to override. "
        "Port to scikit-build-core APIs."
    )
    raise AttributeError(msg)
